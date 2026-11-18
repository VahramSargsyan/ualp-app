"""Source-locked UALP Career KB 008 Neon TEST transaction generator checks."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from career_kb.neon_test_import_adapter import (
    ARTIFACT_SHA256, TARGET_DATABASE, TARGET_ROLE, SESSION_GATE_VALUE,
    _payload, _postflight_gate, _preflight_gate, _quote_json, _source_presence_gate,
    build_statements, verify_official_archive,
)
from career_kb.transactional_import import CareerImportError, load_plan, PLAN_HASH, validate_frozen_plan


def sources():
    plan = Path(os.environ.get('UALP_CAREER_008_PLAN_PATH', '/missing/plan.json'))
    archive = Path(os.environ.get('UALP_CAREER_008_ARCHIVE_PATH', '/missing/source.zip'))
    if not plan.is_file() or not archive.is_file():
        pytest.skip('Source-locked original O*NET files must be supplied explicitly')
    return load_plan(plan), archive


def test_sql_policy_fence_stays_neon_test_only():
    gate = _preflight_gate()
    assert "current_database() IS DISTINCT FROM 'ualp_test'" in gate
    assert "current_user IS DISTINCT FROM 'ualp_test_owner'" in gate
    assert SESSION_GATE_VALUE in gate and PLAN_HASH in gate
    assert "<> 17" in gate and "<> 7" in gate
    for name in ('ualp_assessment_runs','ualp_responses','ualp_scale_scores'):
        assert name in gate
    assert not any(x in gate.upper() for x in ('DROP TABLE','TRUNCATE ','DELETE FROM'))


def test_existing_snapshot_is_fail_closed():
    s=_source_presence_gate()
    assert 'partial existing snapshot' in s
    assert 'existing unrelated source records' in s
    assert all(x in s for x in ('ualp_career_requirements','ualp_career_snapshots'))
    assert '40' in s and '10' in s and '2' in s


def test_sql_payload_literal_quoting():
    value={'label':"Director's office",'unicode':'Արմենիա','scale':None,'raw':'3.88'}
    literal=_quote_json(value)
    assert literal.startswith("'") and literal.endswith("'::jsonb")
    assert "Director''s office" in literal
    assert '\\u0531' in literal


def test_final_readback_checks_every_one_of_seven_tables():
    s=_postflight_gate()
    assert s.count('IS DISTINCT FROM')==7
    assert s.count('RAISE EXCEPTION')==7
    assert 'raw_value' not in s or 'requirements' in s
    assert 'jsonb_populate_recordset' in s


def test_plan_with_official_source_archive():
    plan, archive = sources()
    verify_official_archive(archive,plan)
    assert plan['planSha256']==PLAN_HASH
    assert len(_payload(plan))==7
    assert len(plan['requirements'])==40
    assert sum(x['evidenceStatus']=='SUPPRESSED' and x['rawValue'] is None for x in plan['requirements'])==1


def test_real_plan_produces_atomic_19_statement_allowlist():
    plan,_=sources()
    s=build_statements(plan)
    assert len(s)==19
    assert 'SET LOCAL statement_timeout' in s[1]
    assert 'pg_advisory_xact_lock' in s[3]
    assert SESSION_GATE_VALUE in s[4]
    assert 'CREATE TEMP TABLE' in s[6] and 'ON COMMIT DROP' in s[6]
    assert 'INSERT INTO pg_temp.' in s[7]
    assert s[9].count('import_mode')==1
    assert len([v for v in s if v.startswith('INSERT INTO public.ualp_career_')])==7
    assert all(v.endswith('ON CONFLICT DO NOTHING;') for v in s[10:17])
    assert 'source mismatch' in s[17]
    assert 'EXACT_SOURCE_READBACK_PASS' in s[18]
    assert not any(x in v.upper() for v in s for x in ['DROP TABLE','DELETE FROM','TRUNCATE ','ALTER TABLE'])


@pytest.mark.parametrize('field,value',[
    ('planSha256','0'*64),
    ('mutationAuthorized',True),
    ('careerFitCalculated',True),
    ('personalData',True),
])
def test_plan_tampering_blocks_sql(field,value):
    plan,_=sources()
    bad=copy.deepcopy(plan)
    bad[field]=value
    with pytest.raises(CareerImportError):
        build_statements(bad)


def test_requirement_value_tampering_blocks_sql():
    plan,_=sources()
    bad=copy.deepcopy(plan)
    bad['requirements'][0]['rawValue']='3.44'
    with pytest.raises(CareerImportError,match='SHA-256'):
        build_statements(bad)


def test_missing_or_wrong_source_archive_blocks_sql(tmp_path):
    plan,archive=sources()
    with pytest.raises(CareerImportError):
        verify_official_archive(tmp_path/'missing.zip',plan)
    other=tmp_path/'corrupt.zip'
    other.write_bytes(archive.read_bytes()+b'TAMPER')
    with pytest.raises(CareerImportError,match='digest'):
        verify_official_archive(other,plan)


def test_source_file_manifest_mismatch_fails():
    plan,archive=sources()
    bad=copy.deepcopy(plan)
    bad['sourceSnapshot']['files']['essential_skills.csv']['sizeBytes'] +=1
    with pytest.raises(CareerImportError,match='byte count'):
        verify_official_archive(archive,bad)
