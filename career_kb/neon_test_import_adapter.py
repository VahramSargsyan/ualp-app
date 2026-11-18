"""Generate fail-closed, fully transactional SQL for exact O*NET 31.0 on UALP Neon TEST.

This module neither connects to any database nor changes the existing localhost-only
CI importer. The caller must send *all* generated statements through one Neon
run_sql_transaction call on the exact authorized UALP TEST branch. A single SQL
statement, manual replay of only some statements, or running it on another
branch is explicitly forbidden. Never commit generated real-source SQL/JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

from career_kb.transactional_import import (
    CareerImportError, EXPECT, PLAN_HASH, SOURCE_FILE_HASHES, TABLES,
    guard, load_plan,
)

ARTIFACT_SHA256 = '4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d'
TARGET_DATABASE = 'ualp_test'
TARGET_ROLE = 'ualp_test_owner'
SESSION_GATE_VALUE = 'APPROVED_UALP_NEON_TEST_IMPORT_EXACT_008'
ADVISORY_LOCK = (198315, 3100)
SCHEMA_VERSION = 'UALP-POSTGRES-TEST-v0.1'
BASELINE = {'ualp_assessment_runs': 2, 'ualp_responses': 81, 'ualp_scale_scores': 33}


def verify_official_archive(archive: Path, plan: dict) -> None:
    """Revalidate the exact downloaded official bytes; not merely the supplied plan."""
    guard(archive.is_file(), 'Original O*NET source ZIP must exist locally')
    guard(hashlib.sha256(archive.read_bytes()).hexdigest() == ARTIFACT_SHA256,
          'Official artifact digest mismatch')
    with ZipFile(archive) as z:
        guard(z.testzip() is None, 'Official artifact ZIP CRC mismatch')
        for name, hash_value in SOURCE_FILE_HASHES.items():
            key = f'sources/{name}'
            guard(key in z.namelist(), f'Missing original source file {name}')
            raw = z.read(key)
            guard(hashlib.sha256(raw).hexdigest() == hash_value,
                  f'Original file SHA mismatch: {name}')
            guard(plan['sourceSnapshot']['files'][name]['sizeBytes'] == len(raw),
                  f'Source file byte count mismatch: {name}')
        lock = json.loads(z.read('receipt/source_lock.json'))
        for name, value in SOURCE_FILE_HASHES.items():
            guard(lock['files'][name]['sha256'] == value,
                  f'Source lock mismatch: {name}')
        receipt = json.loads(z.read('receipt/acquisition_receipt.json'))
        guard(receipt.get('triggerCommit') == plan['sourceAttestation']['runCommit']
              and receipt.get('completedAtUTC') == plan['sourceAttestation']['capturedAtUtc'],
              'Original HTTPS acquisition receipt mismatch')


def _encoded(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if type(value).__name__ == 'Jsonb' and hasattr(value, 'obj'):
        return value.obj
    if isinstance(value, (str, int, float, type(None), bool, list, dict)):
        return value
    raise CareerImportError(f'Unexpected SQL payload type {type(value).__name__}')


def _quote_json(value: object) -> str:
    # standard_conforming_strings is forced ON inside the same PostgreSQL tx.
    return "'" + json.dumps(value, sort_keys=True, ensure_ascii=True,
                             separators=(',', ':')).replace("'", "''") + "'::jsonb"


def _preflight_gate() -> str:
    count_sql = "(SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name LIKE 'ualp_%')"
    ccount_sql = "(SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name LIKE 'ualp_career_%')"
    tests = [
        "current_database() IS DISTINCT FROM 'ualp_test'",
        "current_user IS DISTINCT FROM 'ualp_test_owner'",
        f"current_setting('ualp.career_neon_test_import_gate',true) IS DISTINCT FROM '{SESSION_GATE_VALUE}'",
        f"current_setting('ualp.career_neon_test_plan_sha256',true) IS DISTINCT FROM '{PLAN_HASH}'",
        f"{count_sql} <> 17",
        f"{ccount_sql} <> 7",
        f"(SELECT count(*) FROM public.ualp_schema_version WHERE version_key='runtime_schema' AND version_value='{SCHEMA_VERSION}') <> 1",
    ]
    for name, size in BASELINE.items():
        tests.append(f'(SELECT count(*) FROM public.{name}) <> {size}')
    return ("DO $ualp_career_008_gate$ BEGIN IF " + " OR\n    ".join(tests) +
            " THEN RAISE EXCEPTION 'UALP Career KB 008 TEST-only import gate denied'; "
            "END IF; END $ualp_career_008_gate$;")


def _source_presence_gate() -> str:
    checks = []
    total = []
    for table, pk, _ in TABLES:
        expect = 1 if table == 'ualp_career_snapshots' else (2 if table in ('ualp_career_occupations','ualp_career_occupation_versions','ualp_career_scales') else 10 if table in ('ualp_career_competencies','ualp_career_competency_versions') else 40)
        c = f'(SELECT count(*) FROM public.{table})'
        checks.append(f'{c} <> {expect}')
        total.append(c)
    return ("DO $ualp_career_008_existing$ BEGIN\n"
            "IF EXISTS (SELECT 1 FROM public.ualp_career_snapshots WHERE snapshot_id = 'ONET_DB_31_0') THEN\n"
            "  IF " + " OR\n     ".join(checks) +
            " THEN RAISE EXCEPTION 'UALP Career KB 008 partial existing snapshot'; END IF;\n"
            "ELSIF " + " + ".join(total) +
            " <> 0 THEN RAISE EXCEPTION 'UALP Career KB 008 existing unrelated source records';\n"
            "END IF; END $ualp_career_008_existing$;")


def _payload(plan: dict) -> list[tuple[str, list[dict]]]:
    s=plan['sourceSnapshot']
    att=plan['sourceAttestation']
    sets=[
        [{'snapshot_id': s['snapshotId'], 'provider': s['provider'],
          'release': s['release'], 'license_url': s['licenseUrl'],
          'geography': s['geography'], 'manifest_sha256': s['manifestSha256'],
          'file_checks': s['files'], 'acquired_at': att['capturedAtUtc']}],
        [{'occupation_id': x['occupationId'], 'taxonomy': x['taxonomy'],
          'source_external_code': x['externalCode']} for x in plan['occupations']],
        [{'occupation_version_id': x['occupationVersionId'], 'occupation_id': x['occupationId'],
          'snapshot_id': x['snapshotId'], 'source_external_code': x['externalCode'],
          'source_locale': x['sourceLocale'], 'title': x['title'],
          'description': x['description']} for x in plan['occupationVersions']],
        [{'competency_id': x['competencyId'], 'kind': x['kind'],
          'provider_element_id': x['providerElementId']} for x in plan['competencies']],
        [{'competency_version_id': x['competencyVersionId'],
          'competency_id': x['competencyId'], 'snapshot_id': x['snapshotId'],
          'source_locale': x['sourceLocale'], 'label': x['label']}
          for x in plan['competencyVersions']],
        [{'snapshot_id': x['snapshotId'], 'scale_id': x['scaleId'],
          'label': x['label'], 'minimum': x['minimum'], 'maximum': x['maximum']}
          for x in plan['scales']],
        [{'requirement_id': x['requirementId'], 'snapshot_id': x['snapshotId'],
          'occupation_version_id': x['occupationVersionId'],
          'competency_version_id': x['competencyVersionId'],
          'source_record_id': x['sourceRecordId'], 'scale_id': x['scaleId'],
          'scale_minimum': x['scaleMinimum'], 'scale_maximum': x['scaleMaximum'],
          'raw_value': x['rawValue'], 'evidence_status': x['evidenceStatus'],
          'source_updated_at': x['updatedAtSource'], 'domain_source': x['domainSource']}
          for x in plan['requirements']]
    ]
    out=[]
    counts=[1,2,2,10,10,2,40]
    for (table, _, columns), rows, size in zip(TABLES,sets,counts,strict=True):
        guard(len(rows)==size and all(set(x)==set(columns) for x in rows),
              f'Incorrect source columns/count for {table}')
        out.append((table, rows))
    return out


def _postflight_gate() -> str:
    pieces=[]
    for table,pk,_ in TABLES:
        keys='snapshot_id,scale_id' if table=='ualp_career_scales' else pk
        expected=(f"SELECT COALESCE(jsonb_agg(to_jsonb(e) ORDER BY {keys}), '[]'::jsonb) "
                  f"FROM jsonb_populate_recordset(NULL::public.{table}, "
                  f"(SELECT payload FROM pg_temp.ualp_career_008_payload WHERE table_name='{table}')) e")
        actual=(f"SELECT COALESCE(jsonb_agg(to_jsonb(a) ORDER BY {keys}), '[]'::jsonb) "
                f"FROM public.{table} a")
        pieces.append(f"IF ({actual}) IS DISTINCT FROM ({expected}) THEN\n"
                      f" RAISE EXCEPTION 'UALP Career KB 008 source mismatch: {table}';\nEND IF;")
    return "DO $ualp_career_008_postflight$ BEGIN\n"+"\n".join(pieces)+"\nEND $ualp_career_008_postflight$;"


def build_statements(plan: dict) -> list[str]:
    # Original method rigorously checks the SHA of the entire source-plan payload.
    from career_kb.transactional_import import validate_frozen_plan
    validate_frozen_plan(plan)
    rows=_payload(plan)
    guard(len(rows)==7, 'Career KB table set changed')
    values=",\n".join(f"('{table}', {_quote_json(rec)})" for table,rec in rows)
    result=[
        "SET LOCAL lock_timeout = '5s';",
        "SET LOCAL statement_timeout = '30s';",
        "SET LOCAL standard_conforming_strings = on;",
        f"SELECT pg_advisory_xact_lock({ADVISORY_LOCK[0]}, {ADVISORY_LOCK[1]});",
        ("SELECT set_config('ualp.career_neon_test_import_gate', '"+SESSION_GATE_VALUE+"', true) AS test_gate, "
         "set_config('ualp.career_neon_test_plan_sha256', '"+PLAN_HASH+"', true) AS source_plan;"),
        _preflight_gate(),
        ("CREATE TEMP TABLE ualp_career_008_payload (table_name text PRIMARY KEY, "
         "payload jsonb NOT NULL) ON COMMIT DROP;"),
        f"INSERT INTO pg_temp.ualp_career_008_payload(table_name,payload) VALUES\n{values};",
        _source_presence_gate(),
        "SELECT CASE WHEN EXISTS (SELECT 1 FROM public.ualp_career_snapshots WHERE snapshot_id='ONET_DB_31_0') THEN 'NOOP' ELSE 'INSERTED' END AS import_mode;",
    ]
    for table,_,columns in TABLES:
        fields=', '.join(columns)
        result.append(f"INSERT INTO public.{table} ({fields}) SELECT {fields} "
                      f"FROM jsonb_populate_recordset(NULL::public.{table}, "
                      f"(SELECT payload FROM pg_temp.ualp_career_008_payload WHERE table_name='{table}')) r "
                      "ON CONFLICT DO NOTHING;")
    result.append(_postflight_gate())
    result.append("SELECT 'EXACT_SOURCE_READBACK_PASS' AS verdict, "
                  "(SELECT count(*) FROM public.ualp_career_requirements) AS source_requirements, "
                  "(SELECT count(*) FROM public.ualp_career_requirements WHERE evidence_status='SUPPRESSED' AND raw_value IS NULL) AS suppressed_null;")
    guard(len(result)==19, 'Unexpected SQL execution plan length')
    guard(all('DROP TABLE' not in s.upper() and 'TRUNCATE ' not in s.upper() for s in result),
          'Destructive statement forbidden in TEST importer')
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description='Generate exact only Neon TEST O*NET import transaction')
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    opts=parser.parse_args()
    guard(opts.output.suffix=='.json' and not opts.output.exists(),
          'Refuse to overwrite existing SQL plan')
    plan=load_plan(opts.plan)
    verify_official_archive(opts.source_zip,plan)
    statements=build_statements(plan)
    opts.output.write_text(json.dumps(statements,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('UALP_CAREER_KB_008_SQL_EXPORT_PASS source='+PLAN_HASH+' statements='+str(len(statements)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
