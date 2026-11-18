"""UALP Career KB-005: isolated PostgreSQL 18 DDL+rollback rehearsal.

Safeguards: an exact localhost-only disposable CI database, synthetic rows, no
Neon/Render/Vercel/PROD credentials, no source data or personal records.
"""

import hashlib
import json
import os
from pathlib import Path
from uuid import UUID

import psycopg
import pytest
from psycopg.conninfo import conninfo_to_dict

MODE = "EPHEMERAL_POSTGRES_CAREER_KB"
BASE_SCHEMA = Path("migrations/001_initial_postgres_test.sql")
CANDIDATE = Path("docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql")
ROLLBACK = Path("docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_ROLLBACK_DISPOSABLE_ONLY.sql")

BASE_TABLES = (
    "ualp_schema_version", "ualp_catalog_forms", "ualp_catalog_items",
    "ualp_catalog_options", "ualp_catalog_scales", "ualp_catalog_links",
    "ualp_catalog_scoring_rules", "ualp_assessment_runs", "ualp_responses",
    "ualp_scale_scores",
)
CAREER_TABLES = (
    "ualp_career_snapshots", "ualp_career_occupations",
    "ualp_career_occupation_versions", "ualp_career_competencies",
    "ualp_career_competency_versions", "ualp_career_scales",
    "ualp_career_requirements",
)


def safe_local_connection():
    if os.getenv("UALP_CI_MODE") != MODE:
        pytest.skip("Only the explicitly disposable PostgreSQL 18 CI runner may execute this rehearsal")
    url = os.getenv("UALP_CI_DATABASE_URL", "")
    try:
        cfg = conninfo_to_dict(url)
    except Exception:
        pytest.fail("Missing or malformed disposable CI URL")
    assert cfg.get("host") == "127.0.0.1", "P0: no remote database hosts"
    assert cfg.get("port", "5432") == "5432", "P0: unexpected port"
    assert cfg.get("dbname") == "ualp_ci", "P0: no shared database"
    assert cfg.get("user") == "postgres", "P0: isolated local role only"
    assert "neon" not in url.lower() and "render" not in url.lower()
    return url


def rows_fingerprint(conn):
    """Preserve exact old assessment table rows, not merely table counts."""
    details = {}
    for table in BASE_TABLES:  # fixed, hardcoded identifiers, no dynamic user input
        rows = [v[0] for v in conn.execute(
            f"SELECT row_to_json(t)::text FROM public.{table} t ORDER BY 1"
        ).fetchall()]
        details[table] = rows
    digest = hashlib.sha256(json.dumps(details, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    return digest, {t: len(details[t]) for t in BASE_TABLES}


def career_tables(conn):
    return {r[0] for r in conn.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
          AND table_name LIKE 'ualp_career_%'
    """).fetchall()}


def insert_original_synthetic_run(conn):
    conn.execute("""INSERT INTO ualp_catalog_forms
        (form_id,form_key,form_version,locale,status,validation_status,
         item_count,algorithm_version)
        VALUES ('CI-FORM','CI-ONLY','ci-v1','en','DRAFT','NOT_REVIEWED',1,'CI-MEAN-v1')""")
    conn.execute("""INSERT INTO ualp_catalog_items
        (item_id,form_id,prompt,display_order,required)
        VALUES ('CI-ITEM','CI-FORM','Synthetic question',1,true)""")
    conn.execute("""INSERT INTO ualp_catalog_options
        (form_id,option_key,label,score_value,display_order)
        VALUES ('CI-FORM','V0','Synthetic zero',0,1)""")
    conn.execute("""INSERT INTO ualp_catalog_scales
        (scale_id,form_id,scale_key,label,is_parent)
        VALUES ('CI-SCALE','CI-FORM','TEST','Synthetic scale',true)""")
    conn.execute("""INSERT INTO ualp_catalog_links
        (item_id,scale_id,weight,direction)
        VALUES ('CI-ITEM','CI-SCALE',1,'POSITIVE')""")
    conn.execute("""INSERT INTO ualp_catalog_scoring_rules
        (form_id,scale_id,method,min_items,algorithm_version,status)
        VALUES ('CI-FORM','CI-SCALE','MEAN',1,'CI-MEAN-v1','DRAFT')""")
    run = UUID("00000000-0000-0000-0000-000000000111")
    request = UUID("00000000-0000-0000-0000-000000000112")
    conn.execute("""INSERT INTO ualp_assessment_runs
        (run_id,request_id,form_id,payload_sha256,consent,status,algorithm_version)
        VALUES (%s,%s,'CI-FORM',%s,true,'COMPLETED','CI-MEAN-v1')""",
        (run, request, "a" * 64))
    conn.execute("""INSERT INTO ualp_responses (run_id,item_id,option_key)
        VALUES (%s,'CI-ITEM','V0')""", (run,))
    conn.execute("""INSERT INTO ualp_scale_scores
        (run_id,scale_id,raw_score,answered_count,algorithm_version)
        VALUES (%s,'CI-SCALE',0,1,'CI-MEAN-v1')""", (run,))


def reject(conn, label, statement, params=None, *, contains=None,
           sqlstate=None, exact_constraint=None):
    """Reject for the intended reason, not an unrelated earlier uniqueness guard."""
    with pytest.raises(psycopg.Error) as caught:
        conn.execute(statement, params)
    if contains:
        assert contains.lower() in str(caught.value).lower(), (label, str(caught.value))
    if sqlstate:
        assert caught.value.sqlstate == sqlstate, (label, caught.value.sqlstate)
    if exact_constraint:
        assert caught.value.diag.constraint_name == exact_constraint, (
            label, caught.value.diag.constraint_name, exact_constraint)
    print(f"NEGATIVE_PASS {label}: {caught.value.sqlstate} "
          f"constraint={caught.value.diag.constraint_name}", flush=True)


def add_snapshot(conn, snapshot_id="SNAP-CI-31"):
    conn.execute("""INSERT INTO ualp_career_snapshots
        (snapshot_id,provider,release,license_url,geography,
         manifest_sha256,file_checks,acquired_at)
        VALUES (%s,'O*NET Database','31.0',%s,'US',%s,%s::jsonb,%s::timestamptz)""",
        (snapshot_id, "https://creativecommons.org/licenses/by/4.0/",
         ("f" if snapshot_id != "SNAP-CI-31" else "e") * 64,
         json.dumps({"synthetic": "no external downloaded source"}),
         "2026-11-18T14:16:55+00:00"))


def insert_synthetic_40(conn):
    snapshot = "SNAP-CI-31"
    add_snapshot(conn, snapshot)
    conn.execute("""INSERT INTO ualp_career_scales
        (snapshot_id,scale_id,label,minimum,maximum) VALUES
        ('SNAP-CI-31','IM','Importance',1,5),
        ('SNAP-CI-31','LV','Level',0,7)""")
    for role in (0, 1):
        code = f"15-2051.0{role}"
        oid = f"CI-OCC-{role}"
        vid = f"CI-OCCV-{role}"
        conn.execute("""INSERT INTO ualp_career_occupations
            (occupation_id,taxonomy,source_external_code) VALUES (%s,'ONET-SOC-31.0',%s)""",
            (oid, code))
        conn.execute("""INSERT INTO ualp_career_occupation_versions
            (occupation_version_id,occupation_id,snapshot_id,source_external_code,
             source_locale,title,description)
            VALUES (%s,%s,%s,%s,'en',%s,'Invented CI occupation description')""",
            (vid, oid, snapshot, code, f"Synthetic CI role {role}"))
    for n in range(10):
        conn.execute("""INSERT INTO ualp_career_competencies
            (competency_id,kind,provider_element_id)
            VALUES (%s,'ESSENTIAL_SKILL',%s)""",
            (f"CI-SKILL-{n}", f"TEST-FICTIONAL-{n}"))
        conn.execute("""INSERT INTO ualp_career_competency_versions
            (competency_version_id,competency_id,snapshot_id,source_locale,label)
            VALUES (%s,%s,%s,'en',%s)""",
            (f"CI-SKILLV-{n}", f"CI-SKILL-{n}", snapshot,
             f"Invented CI skill {n}"))
    for role in (0, 1):
        for n in range(10):
            for scale, low, high, value in (("IM", 1, 5, "3.5"),
                                            ("LV", 0, 7, "4.5")):
                suppressed = role == 1 and n == 3 and scale == "LV"
                conn.execute("""INSERT INTO ualp_career_requirements
                    (requirement_id,snapshot_id,occupation_version_id,
                     competency_version_id,source_record_id,scale_id,
                     scale_minimum,scale_maximum,raw_value,evidence_status,
                     source_updated_at,domain_source)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'08/2026','CI_SYNTHETIC')""",
                    (f"CI-REQ-{role}-{n}-{scale}", snapshot, f"CI-OCCV-{role}",
                     f"CI-SKILLV-{n}", f"CI-SOURCE-{role}-{n}-{scale}",
                     scale, low, high, None if suppressed else value,
                     "SUPPRESSED" if suppressed else "OBSERVED"))


def test_disposable_career_schema_and_rollback():
    url = safe_local_connection()
    schema = CANDIDATE.read_text(encoding="utf-8")
    undo = ROLLBACK.read_text(encoding="utf-8")
    assert "APPROVED_DISPOSABLE_TEST" in schema and "APPROVED_DISPOSABLE_TEST" in undo
    with psycopg.connect(url, autocommit=True) as conn:
        assert conn.info.server_version >= 180000, "Expected PostgreSQL 18 service"
        assert conn.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'").fetchone()[0] == 0, "P0: DB not empty"
        conn.execute(BASE_SCHEMA.read_text(encoding="utf-8"))
        insert_original_synthetic_run(conn)
        baseline_hash, baseline_counts = rows_fingerprint(conn)
        assert len(BASE_TABLES) == 10 and all(v == 1 for v in baseline_counts.values())
        print("BASELINE_HASH", baseline_hash, "BASE_TABLE_ROWS", baseline_counts, flush=True)

        # Unauthorized DDL must roll back its entire transaction, and leave baseline intact.
        reject(conn, "migration_requires_session_gate", schema,
               contains="not authorized in this session")
        conn.execute("ROLLBACK")  # proposed DDL starts BEGIN before raising
        assert career_tables(conn) == set()
        assert rows_fingerprint(conn)[0] == baseline_hash

        conn.execute("SELECT set_config('ualp.career_migration_gate',%s,false)",
                     ("APPROVED_DISPOSABLE_TEST",))
        conn.execute(schema)
        assert career_tables(conn) == set(CAREER_TABLES)
        assert rows_fingerprint(conn)[0] == baseline_hash
        print("DDL_PASS 7_additive_tables baseline_unchanged", flush=True)

        # A second run on an existing schema must abort rather than silently overwrite.
        reject(conn, "repeated_ddl_no_overwrite", schema, contains="already exists")
        conn.execute("ROLLBACK")
        assert career_tables(conn) == set(CAREER_TABLES)
        assert rows_fingerprint(conn)[0] == baseline_hash

        # Rollback is a separate explicit gate, including if all new tables are empty.
        reject(conn, "rollback_requires_separate_gate", undo,
               contains="rollback is not authorized")
        conn.execute("ROLLBACK")
        assert career_tables(conn) == set(CAREER_TABLES)

        insert_synthetic_40(conn)
        counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                  for t in CAREER_TABLES}
        assert counts == {
            "ualp_career_snapshots": 1,
            "ualp_career_occupations": 2,
            "ualp_career_occupation_versions": 2,
            "ualp_career_competencies": 10,
            "ualp_career_competency_versions": 10,
            "ualp_career_scales": 2,
            "ualp_career_requirements": 40,
        }
        assert conn.execute("SELECT count(*) FROM ualp_career_requirements WHERE raw_value IS NULL AND evidence_status = 'SUPPRESSED'").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM ualp_career_requirements WHERE evidence_status = 'OBSERVED'").fetchone()[0] == 39
        print("SEEDED_DATA_PASS", counts, flush=True)

        # An extra synthetic competency makes each negative test use a fresh
        # (snapshot, role, competency, scale) tuple. Otherwise an existing
        # unique constraint masks the FK or rating guard under examination.
        conn.execute("""INSERT INTO ualp_career_competencies
            (competency_id,kind,provider_element_id)
            VALUES ('CI-SKILL-NEG','ESSENTIAL_SKILL','TEST-FICTIONAL-NEG')""")
        conn.execute("""INSERT INTO ualp_career_competency_versions
            (competency_version_id,competency_id,snapshot_id,source_locale,label)
            VALUES ('CI-SKILLV-NEG','CI-SKILL-NEG','SNAP-CI-31','en',
                    'Synthetic negative-case competency')""")
        constraints = dict(conn.execute("""SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint WHERE conrelid='ualp_career_requirements'::regclass""").fetchall())
        scale_names = [name for name, rule in constraints.items()
                       if 'REFERENCES ualp_career_scales' in rule]
        source_record_names = [name for name, rule in constraints.items()
                               if 'UNIQUE (snapshot_id, source_record_id)' in rule]
        assert len(scale_names) == 1 and len(source_record_names) == 1

        # Every source relationship, rating bound and missingness is enforced in SQL.
        base_req = """INSERT INTO ualp_career_requirements
            (requirement_id,snapshot_id,occupation_version_id,
             competency_version_id,source_record_id,scale_id,
             scale_minimum,scale_maximum,raw_value,evidence_status,
             source_updated_at,domain_source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'08/2026','CI_SYNTHETIC')"""
        def args(tag, *, snap="SNAP-CI-31", occ="CI-OCCV-0", competency="CI-SKILLV-NEG", scale="IM", minimum=1, maximum=5, value="2.5", status="OBSERVED", record=None):
            return (f"CI-NEG-{tag}", snap, occ, competency, record or f"CI-NEG-SOURCE-{tag}",
                    scale, minimum, maximum, value, status)

        reject(conn, "unknown_competency_fk", base_req,
               args("FK", competency="CI-SKILLV-UNKNOWN"), sqlstate="23503")
        reject(conn, "invalid_rating_above_scale", base_req,
               args("HI", value="6"), sqlstate="23514")
        reject(conn, "observed_requires_value", base_req,
               args("NULL", value=None), sqlstate="23514")
        reject(conn, "suppressed_requires_null", base_req,
               args("SUPPRESS", status="SUPPRESSED", value="0"), sqlstate="23514")
        reject(conn, "scale_bounds_composite_fk", base_req,
               args("SCALE", maximum=6), sqlstate="23503",
               exact_constraint=scale_names[0])
        reject(conn, "duplicate_source_record_rejected", base_req,
               args("DUP", record="CI-SOURCE-0-0-IM"), sqlstate="23505",
               exact_constraint=source_record_names[0])
        add_snapshot(conn, "SNAP-CI-OTHER")
        reject(conn, "different_snapshot_occupation_fk", base_req,
               args("XSNAP", snap="SNAP-CI-OTHER"), sqlstate="23503")
        reject(conn, "referenced_snapshot_delete_restricted",
               "DELETE FROM ualp_career_snapshots WHERE snapshot_id='SNAP-CI-31'", sqlstate="23001")
        assert rows_fingerprint(conn)[0] == baseline_hash
        # No unexpected writes survived the negatives.
        assert conn.execute("SELECT count(*) FROM ualp_career_requirements").fetchone()[0] == 40
        print("NEGATIVE_SOURCE_INTEGRITY_PASS 8_checks", flush=True)

        conn.execute("SELECT set_config('ualp.career_rollback_gate',%s,false)",
                     ("APPROVED_DISPOSABLE_TEST",))
        reject(conn, "rollback_refuses_populated_tables", undo,
               contains="nonempty tables")
        conn.execute("ROLLBACK")
        assert career_tables(conn) == set(CAREER_TABLES)
        assert conn.execute("SELECT count(*) FROM ualp_career_requirements").fetchone()[0] == 40

        # Emulate separately approved snapshot cleanup, in reverse FK order,
        # on this DISPOSABLE service only. Never perform this on populated Neon.
        for table in (
            "ualp_career_requirements", "ualp_career_scales",
            "ualp_career_competency_versions", "ualp_career_competencies",
            "ualp_career_occupation_versions", "ualp_career_occupations",
            "ualp_career_snapshots",
        ):
            conn.execute(f"DELETE FROM public.{table}")
        assert all(conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] == 0
                   for t in CAREER_TABLES)
        assert rows_fingerprint(conn)[0] == baseline_hash
        conn.execute(undo)
        assert career_tables(conn) == set()
        final_hash, final_counts = rows_fingerprint(conn)
        assert (final_hash, final_counts) == (baseline_hash, baseline_counts)
        assert conn.execute("SELECT version_value FROM ualp_schema_version WHERE version_key='runtime_schema'").fetchone()[0] == "UALP-POSTGRES-TEST-v0.1"
        print("ROLLBACK_PASS 7_tables_removed after_explicit_cleanup base_sha256_unchanged", flush=True)
        receipt = {
            "testLevel": "REAL_DISPOSABLE_POSTGRESQL_18_E2E",
            "status": "PASS",
            "databaseTarget": "localhost:5432/ualp_ci",
            "schemaSource": str(CANDIDATE),
            "rollbackSource": str(ROLLBACK),
            "baseAssessmentTableCount": len(BASE_TABLES),
            "baseRowsPerTable": baseline_counts,
            "baseRowsSHA256BeforeAndAfter": baseline_hash,
            "careerTablesCreatedAndDropped": len(CAREER_TABLES),
            "syntheticImportedRequirements": 40,
            "observedRequirements": 39,
            "suppressedNullRequirements": 1,
            "negativeChecks": 12,
            "neonOrProdTouched": False,
            "sourceDataImported": False,
        }
        output = os.environ.get("UALP_CI_RECEIPT_PATH")
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("CAREER_KB_DISPOSABLE_POSTGRES_RECEIPT", json.dumps(receipt, sort_keys=True), flush=True)
