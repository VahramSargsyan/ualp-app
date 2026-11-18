"""Real, isolated PostgreSQL 18 E2E for one exact source-locked O*NET plan.

Everything here is synthetic except the *public occupational source plan* downloaded
from original GitHub Actions evidence. Never runs on Neon or an external database.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID

import pytest

from career_kb.transactional_import import (
    CareerImportError, EXPECT, PLAN_HASH, SNAPSHOT_ID, load_plan,
    run_disposable_import, validate_frozen_plan,
)

SOURCE_PLAN = Path(os.environ.get("UALP_CAREER_PLAN_PATH", "/nonexistent-source-plan"))
CAREER_TABLES = (
    "ualp_career_snapshots", "ualp_career_occupations",
    "ualp_career_occupation_versions", "ualp_career_competencies",
    "ualp_career_competency_versions", "ualp_career_scales", "ualp_career_requirements",
)
BASE_TABLES = (
    "ualp_schema_version", "ualp_catalog_forms", "ualp_catalog_items", "ualp_catalog_options",
    "ualp_catalog_scales", "ualp_catalog_links", "ualp_catalog_scoring_rules",
    "ualp_assessment_runs", "ualp_responses", "ualp_scale_scores",
)


def baseline(conn):
    """Digest all original table rows, including IDs/values; order independent."""
    result = {}
    with conn.cursor() as cur:
        for name in BASE_TABLES:
            cur.execute(f"SELECT * FROM {name}")
            result[name] = sorted(
                [tuple(str(value) if value is not None else None for value in row)
                 for row in cur.fetchall()], key=lambda row: str(row))
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(), {
        k: len(v) for k, v in result.items()
    }


def counts(conn):
    with conn.cursor() as cur:
        return {t: cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                for t in CAREER_TABLES}


def require_sqlstate(conn, sql, state, *, params=None):
    """DB must reject the statement, but independent suite must continue."""
    import psycopg
    # The scripts contain their own BEGIN/COMMIT, so use an autocommit
    # connection and explicitly roll back the deliberately aborted transaction.
    try:
        with pytest.raises(psycopg.Error) as caught:
            conn.execute(sql, params)
        assert caught.value.sqlstate == state, (caught.value.sqlstate, state)
    finally:
        conn.execute("ROLLBACK")


def test_source_plan_guard_without_db():
    plan = load_plan(SOURCE_PLAN)
    assert validate_frozen_plan(plan) == PLAN_HASH
    assert plan["sourceSnapshot"]["release"] == "31.0"
    assert sorted(v["externalCode"] for v in plan["occupations"]) == ["15-2051.00", "15-2051.01"]
    assert len(plan["requirements"]) == EXPECT["requirements"]
    cases = [
        ("replace_skill_rating", lambda p: p["requirements"][0].__setitem__("rawValue", "4.50")),
        ("alter_sha", lambda p: p["sourceSnapshot"]["files"]["essential_skills.csv"].__setitem__("sha256", "0" * 64)),
        ("invent_fit", lambda p: p.__setitem__("careerFitCalculated", True)),
        ("drop_requirement", lambda p: p["requirements"].pop()),
        ("extra_field", lambda p: p.__setitem__("learnerAnswers", [1])),
        ("change_attestation", lambda p: p["sourceAttestation"].__setitem__("runCommit", "0" * 40)),
        ("remove_suppression", lambda p: next(x for x in p["requirements"] if x["evidenceStatus"] == "SUPPRESSED").__setitem__("evidenceStatus", "OBSERVED")),
    ]
    for name, modifier in cases:
        altered = copy.deepcopy(plan)
        modifier(altered)
        with pytest.raises(CareerImportError):
            validate_frozen_plan(altered)


def test_real_postgres_transactionality():
    if os.environ.get("UALP_CI_MODE") != "EPHEMERAL_POSTGRES_CAREER_IMPORT":
        pytest.skip("Isolated GitHub Actions PostgreSQL 18 only")
    import psycopg
    from psycopg.conninfo import conninfo_to_dict
    from career_kb.transactional_import import local_ci_destination

    dsn = os.environ["UALP_CI_DATABASE_URL"]
    local_ci_destination(dsn)
    p = conninfo_to_dict(dsn)
    assert p["host"] == "127.0.0.1" and p["dbname"] == "ualp_ci"
    plan = load_plan(SOURCE_PLAN)
    with psycopg.connect(dsn, autocommit=True) as conn:
        assert conn.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'").fetchone()[0] == 0
        conn.execute(Path("migrations/001_initial_postgres_test.sql").read_text())
        # Synthetic baseline: actual links, score and response, not blank database.
        conn.execute("""INSERT INTO ualp_catalog_forms
          (form_id,form_key,form_version,locale,status,validation_status,item_count,algorithm_version)
          VALUES ('CI-CAR-FORM','CI-CAREER-ONLY','ci-v1','en','DRAFT','SYNTHETIC',1,'CI-MEAN')""")
        conn.execute("""INSERT INTO ualp_catalog_items(item_id,form_id,prompt,display_order)
          VALUES('CI-CAR-ITEM','CI-CAR-FORM','synthetic question',1)""")
        conn.execute("""INSERT INTO ualp_catalog_options(form_id,option_key,label,score_value,display_order)
          VALUES('CI-CAR-FORM','A','synthetic',2,1)""")
        conn.execute("""INSERT INTO ualp_catalog_scales(scale_id,form_id,scale_key,label,is_parent)
          VALUES('CI-CAR-SCALE','CI-CAR-FORM','CI','Synthetic',true)""")
        conn.execute("""INSERT INTO ualp_catalog_links(item_id,scale_id)
          VALUES('CI-CAR-ITEM','CI-CAR-SCALE')""")
        conn.execute("""INSERT INTO ualp_catalog_scoring_rules
          (form_id,scale_id,method,min_items,algorithm_version,status)
          VALUES('CI-CAR-FORM','CI-CAR-SCALE','MEAN',1,'CI-MEAN','DRAFT')""")
        conn.execute("""INSERT INTO ualp_assessment_runs
          (run_id,request_id,form_id,payload_sha256,consent,status,algorithm_version,created_at)
          VALUES('aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa','bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb',
          'CI-CAR-FORM', repeat('a',64),true,'COMPLETED','CI-MEAN','2026-11-18T00:00:00Z')""")
        conn.execute("""INSERT INTO ualp_responses(run_id,item_id,option_key)
          VALUES('aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa','CI-CAR-ITEM','A')""")
        conn.execute("""INSERT INTO ualp_scale_scores
          (run_id,scale_id,raw_score,answered_count,algorithm_version)
          VALUES('aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa','CI-CAR-SCALE',2,1,'CI-MEAN')""")
        before_digest, before_counts = baseline(conn)
        assert len(before_counts) == 10 and all(n >= 1 for n in before_counts.values())
        # Explicitly arm *disposable* schema only. Refuse if not armed.
        sql = Path("docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql").read_text()
        require_sqlstate(conn, sql, "P0001")
        conn.execute("SET ualp.career_migration_gate = 'APPROVED_DISPOSABLE_TEST'")
        conn.execute(sql)
        assert all(n == 0 for n in counts(conn).values())
        assert baseline(conn)[0] == before_digest
        print("DDL_PASS 7_empty_tables / original_assessment_unchanged")

        # Test rollback of a failed transaction at three different stages.
        for stage in ("snapshots", "occupation_versions", "requirements"):
            with pytest.raises(CareerImportError, match="CI injected failure"):
                run_disposable_import(plan, dsn, fault_after=stage)
            assert all(n == 0 for n in counts(conn).values())
            assert baseline(conn)[0] == before_digest
            print("ATOMIC_ABORT_PASS", stage)

        # Two concurrent first writes must serialize to one insert and one NOOP.
        def submit(_):
            return run_disposable_import(plan, dsn)["status"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(submit, range(2)))
        assert sorted(statuses) == ["INSERTED", "NOOP"]
        print("CONCURRENT_FIRST_WRITES_PASS", statuses)
        expected_counts = {
            "ualp_career_snapshots": 1, "ualp_career_occupations": 2,
            "ualp_career_occupation_versions": 2,
            "ualp_career_competencies": 10, "ualp_career_competency_versions": 10,
            "ualp_career_scales": 2, "ualp_career_requirements": 40,
        }
        assert counts(conn) == expected_counts
        assert baseline(conn)[0] == before_digest
        assert conn.execute("""SELECT count(*) FROM ualp_career_requirements
          WHERE evidence_status='OBSERVED' AND raw_value IS NOT NULL""").fetchone()[0] == 39
        assert conn.execute("""SELECT count(*) FROM ualp_career_requirements
          WHERE evidence_status='SUPPRESSED' AND raw_value IS NULL""").fetchone()[0] == 1
        assert run_disposable_import(plan, dsn)["status"] == "NOOP"
        print("REAL_IMPORT_READBACK_PASS", expected_counts)
        print("IDEMPOTENT_NOOP_PASS")

        # Drift of existing record blocks any replay and must not repair it silently.
        requirement = plan["requirements"][0]
        rid = requirement["requirementId"]
        conn.execute("""UPDATE ualp_career_requirements SET raw_value = 1.00
          WHERE requirement_id = %s""", (rid,))
        with pytest.raises(CareerImportError, match="Stored snapshot differs"):
            run_disposable_import(plan, dsn)
        assert conn.execute("""SELECT raw_value FROM ualp_career_requirements
            WHERE requirement_id=%s""", (rid,)).fetchone()[0] == 1
        # Restore the exact source value in the disposable database.
        conn.execute("""UPDATE ualp_career_requirements SET raw_value = %s
          WHERE requirement_id = %s""", (requirement["rawValue"], rid))
        assert run_disposable_import(plan, dsn)["status"] == "NOOP"
        print("PREEXISTING_CONFLICT_PASS / original_source_restored")

        # Wrong environment must fail *before* DB connection attempts.
        with pytest.raises(CareerImportError, match=r"Only 127[.]0[.]0[.]1"):
            from career_kb.transactional_import import local_ci_destination
            old_url = os.environ["UALP_CI_DATABASE_URL"]
            try:
                evil = "postgresql://postgres@neon.example.com:5432/ualp_ci"
                os.environ["UALP_CI_DATABASE_URL"] = evil
                local_ci_destination(evil)
            finally:
                os.environ["UALP_CI_DATABASE_URL"] = old_url
        print("REMOTE_DB_FENCE_PASS")

        rollback = Path("docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_ROLLBACK_DISPOSABLE_ONLY.sql").read_text()
        require_sqlstate(conn, rollback, "P0001")
        conn.execute("SET ualp.career_rollback_gate = 'APPROVED_DISPOSABLE_TEST'")
        require_sqlstate(conn, rollback, "P0001")  # populated tables
        assert baseline(conn)[0] == before_digest
        print("POPULATED_ROLLBACK_REFUSED_PASS")
        # Test only: complete reverse dependency order; no actual TEST tables.
        for table in reversed(CAREER_TABLES):
            conn.execute(f"DELETE FROM {table}")
        assert all(n == 0 for n in counts(conn).values())
        conn.execute(rollback)
        assert conn.execute("""SELECT count(*) FROM pg_tables WHERE schemaname='public'
            AND tablename LIKE 'ualp_career_%'""").fetchone()[0] == 0
        after_digest, after_counts = baseline(conn)
        assert after_digest == before_digest and after_counts == before_counts
        print("GUARDED_ROLLBACK_PASS 7_tables_removed baseline_digest", before_digest)
        receipt = {
            "status": "REAL_O_NET31_PLAN_TRANSACTIONAL_IMPORT_PASS",
            "testLevel": "REAL_DISPOSABLE_POSTGRESQL_18_E2E",
            "dataOrigin": "OFFICIAL_ONET_31_PUBLIC_OCCUPATION_DATA",
            "planSha256": PLAN_HASH,
            "sourceFiles": plan["sourceSnapshot"]["files"],
            "rowsImported": expected_counts,
            "requirementsObserved": 39,
            "requirementsSuppressedNull": 1,
            "atomicAbortStages": ["snapshots", "occupation_versions", "requirements"],
            "concurrentFirstWrites": sorted(statuses),
            "repeatResult": "NOOP",
            "conflictingReplay": "REJECTED_WITHOUT_OVERWRITE",
            "remoteDatabaseFence": "DENIED",
            "rollback": "POPULATED_REFUSED_THEN_EMPTY_PASS",
            "legacyDigestBeforeAfter": before_digest,
            "legacyTableCount": len(before_counts),
            "neonTestTouched": False,
            "prodTouched": False,
        }
        output = Path(os.environ["UALP_CAREER_RECEIPT_PATH"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        print("TRANSACTIONAL_IMPORT_RECEIPT", json.dumps({k: v for k, v in receipt.items() if k != "sourceFiles"}, sort_keys=True))
