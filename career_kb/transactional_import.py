"""Fail-closed, transaction-atomic import of ONE frozen O*NET Career KB plan.

No remote/Neon/PROD connectivity is permitted. This is a disposable-Postgres
rehearsal-only writer, not a deployment migration or webapp integration.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

PLAN_HASH = "78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d"
MANIFEST_HASH = "03bbd9bd709eab4ac764a940f5110ab9292645b67d34c3ef600f28fcc3f9da78"
SOURCE_FILE_HASHES = {
    "occupation_data.csv": "a09eae1d6609686e44e05b7290993a1c8b523d8ca224bc0eedc194c855c3ee02",
    "essential_skills.csv": "68c4d31d8c55077238395dca40cc4e6d32e6a608b5474bb8264b1f98ae415bd7",
    "scales_reference.csv": "bcba23858ce21ecaacbde303a8993e35d46724b4afb8c9ec2b10e04f42adcfc9",
}
SNAPSHOT_ID = "ONET_DB_31_0"
SOURCE_RUN_COMMIT = "1171ece481fde70a7493ddf581fb0a54d9f6fa68"
SOURCE_ATT_DATE = "2026-11-18T14:16:55+00:00"
EXPECT = {"occupations": 2, "occupationVersions": 2, "competencies": 10,
          "competencyVersions": 10, "scales": 2, "requirements": 40}
MODE = "EPHEMERAL_POSTGRES_CAREER_IMPORT"


class CareerImportError(ValueError):
    """Source lock, destination, pre-existing data or authorization did not match."""


def guard(condition: bool, message: str) -> None:
    if not condition:
        raise CareerImportError(message)


def canonical_bytes(document: dict) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def validate_frozen_plan(plan: dict) -> str:
    """Validate both checksum and explicit data-privacy/source policies before SQL."""
    guard(isinstance(plan, dict), "Plan must be a JSON object")
    guard(set(plan) == {"schemaVersion", "readOnly", "mutationAuthorized", "personalData",
                               "careerFitCalculated", "sourceSnapshot", "sourceAttestation",
                               "occupations", "occupationVersions", "competencies",
                               "competencyVersions", "scales", "requirements", "planSha256"},
          "Unrecognized or missing plan keys")
    guard(plan.get("planSha256") == PLAN_HASH, "Not the approved frozen import plan hash")
    payload = dict(plan)
    payload.pop("planSha256")
    guard(hashlib.sha256(canonical_bytes(payload)).hexdigest() == PLAN_HASH,
          "Plan contents do not match pinned SHA-256")
    guard(plan["schemaVersion"] == "UALP-CAREER-KB-IMPORT-PLAN-v0.1", "Plan schema changed")
    guard(plan["readOnly"] is True and plan["mutationAuthorized"] is False and
          plan["personalData"] is False and plan["careerFitCalculated"] is False,
          "A source-only, read-only logical plan is required")
    src = plan["sourceSnapshot"]
    guard(src["snapshotId"] == SNAPSHOT_ID and src["provider"] == "O*NET Database"
          and src["release"] == "31.0" and
          src["manifestSha256"] == MANIFEST_HASH and
          src["geography"] == "United States / O*NET-SOC taxonomy" and
          src["licenseUrl"] == "https://creativecommons.org/licenses/by/4.0/",
          "Source snapshot policy mismatch")
    guard(set(src["files"]) == set(SOURCE_FILE_HASHES), "Source file set mismatch")
    for name, expected_hash in SOURCE_FILE_HASHES.items():
        guard(src["files"][name]["sha256"] == expected_hash,
              f"O*NET 31.0 source SHA mismatch: {name}")
    att = plan["sourceAttestation"]
    guard(att == {"status": "GITHUB_HTTPS_RECEIPT_MATCHES_LOCK",
                  "capturedAtUtc": SOURCE_ATT_DATE,
                  "runCommit": SOURCE_RUN_COMMIT}, "Source attestation mismatch")
    for name, count in EXPECT.items():
        guard(isinstance(plan[name], list) and len(plan[name]) == count,
              f"Unexpected bounded source row count: {name}")
    roles = {x["externalCode"] for x in plan["occupations"]}
    guard(roles == {"15-2051.00", "15-2051.01"}, "Career role scope widened")
    guard({x["scaleId"] for x in plan["scales"]} == {"IM", "LV"},
          "Unexpected source scale")
    guard(sum(x["evidenceStatus"] == "OBSERVED" for x in plan["requirements"]) == 39
          and sum(x["evidenceStatus"] == "SUPPRESSED" for x in plan["requirements"]) == 1,
          "Unexpected missingness state")
    guard(all((x["rawValue"] is None) == (x["evidenceStatus"] != "OBSERVED")
              for x in plan["requirements"]), "Missingness cannot become zero")
    return PLAN_HASH


def local_ci_destination(dsn: str) -> None:
    """Permit only the exact disposable CI database, never a Neon/remote DB."""
    guard(os.environ.get("UALP_CI_MODE") == MODE, "Disposable PostgreSQL CI mode required")
    guard(os.environ.get("UALP_CI_DATABASE_URL") == dsn,
          "CI DB URL must come from the pinned environment variable")
    try:
        from psycopg.conninfo import conninfo_to_dict
        p = conninfo_to_dict(dsn)
    except Exception as exc:
        raise CareerImportError("Invalid PostgreSQL URL") from exc
    guard(p.get("host") == "127.0.0.1" and p.get("port", "5432") == "5432" and
          p.get("dbname") == "ualp_ci" and p.get("user") == "postgres" and
          p.get("sslmode") in (None, "disable"),
          "Only 127.0.0.1:5432/ualp_ci postgres account is allowed")


# Explicit SQL/table mappings. Never construct SQL from untrusted plan keys.
TABLES = (
    ("ualp_career_snapshots", "snapshot_id", (
        "snapshot_id", "provider", "release", "license_url", "geography",
        "manifest_sha256", "file_checks", "acquired_at")),
    ("ualp_career_occupations", "occupation_id", (
        "occupation_id", "taxonomy", "source_external_code")),
    ("ualp_career_occupation_versions", "occupation_version_id", (
        "occupation_version_id", "occupation_id", "snapshot_id", "source_external_code",
        "source_locale", "title", "description")),
    ("ualp_career_competencies", "competency_id", (
        "competency_id", "kind", "provider_element_id")),
    ("ualp_career_competency_versions", "competency_version_id", (
        "competency_version_id", "competency_id", "snapshot_id", "source_locale", "label")),
    ("ualp_career_scales", "scale_id", (
        "snapshot_id", "scale_id", "label", "minimum", "maximum")),
    ("ualp_career_requirements", "requirement_id", (
        "requirement_id", "snapshot_id", "occupation_version_id", "competency_version_id",
        "source_record_id", "scale_id", "scale_minimum", "scale_maximum", "raw_value",
        "evidence_status", "source_updated_at", "domain_source")),
)


def expected_rows(plan: dict):
    from psycopg.types.json import Jsonb
    s = plan["sourceSnapshot"]
    a = plan["sourceAttestation"]
    d = datetime.fromisoformat(a["capturedAtUtc"].replace("Z", "+00:00"))
    yield [((s["snapshotId"], s["provider"], s["release"], s["licenseUrl"],
             s["geography"], s["manifestSha256"], Jsonb(s["files"]), d))]
    yield [(x["occupationId"], x["taxonomy"], x["externalCode"])
           for x in plan["occupations"]]
    yield [(x["occupationVersionId"], x["occupationId"], x["snapshotId"],
            x["externalCode"], x["sourceLocale"], x["title"], x["description"])
           for x in plan["occupationVersions"]]
    yield [(x["competencyId"], x["kind"], x["providerElementId"])
           for x in plan["competencies"]]
    yield [(x["competencyVersionId"], x["competencyId"], x["snapshotId"],
            x["sourceLocale"], x["label"])
           for x in plan["competencyVersions"]]
    yield [(x["snapshotId"], x["scaleId"], x["label"], Decimal(x["minimum"]),
            Decimal(x["maximum"])) for x in plan["scales"]]
    yield [(x["requirementId"], x["snapshotId"], x["occupationVersionId"],
            x["competencyVersionId"], x["sourceRecordId"], x["scaleId"],
            Decimal(x["scaleMinimum"]), Decimal(x["scaleMaximum"]),
            None if x["rawValue"] is None else Decimal(x["rawValue"]),
            x["evidenceStatus"], x["updatedAtSource"], x["domainSource"])
           for x in plan["requirements"]]


def unwrap_json(row: tuple) -> tuple:
    return tuple(value.obj if hasattr(value, "obj") and type(value).__name__ == "Jsonb" else value
                 for value in row)


def inspect_exact(cur, plan: dict) -> None:
    """Fail-closed readback: exact rows, no partial or divergent snapshot."""
    for (table, pk, columns), records in zip(TABLES, expected_rows(plan)):
        if table in ("ualp_career_occupations", "ualp_career_competencies"):
            key_ids = [row[0] for row in records]
            cur.execute(f"SELECT {','.join(columns)} FROM {table} WHERE {pk} = ANY(%s)",
                        (key_ids,))
        else:
            cur.execute(f"SELECT {','.join(columns)} FROM {table} WHERE snapshot_id = %s",
                        (SNAPSHOT_ID,))
        fetched = [tuple(row) for row in cur.fetchall()]
        want = [unwrap_json(row) for row in records]
        guard(len(fetched) == len(want), f"Partial/extra snapshot rows: {table}")
        # All rows have a stable primary ID in the first position except scale,
        # for which snapshot_id plus scale_id forms the compound identity.
        sort_key = (lambda row: row[1]) if table == "ualp_career_scales" else (lambda row: row[0])
        guard(sorted(fetched, key=sort_key) == sorted(want, key=sort_key),
              f"Stored snapshot differs from frozen source: {table}")


def run_disposable_import(plan: dict, dsn: str, *, fault_after: str | None = None) -> dict:
    """Insert all tables atomically. Identical replays NOOP; any drift raises.

    fault_after is intentionally CI-only and is never a CLI/user-facing argument.
    """
    validate_frozen_plan(plan)
    local_ci_destination(dsn)
    guard(fault_after in (None, "snapshots", "occupation_versions", "requirements"),
          "Unknown injected test fault")
    import psycopg

    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user")
                guard(cur.fetchone() == ("ualp_ci", "postgres"),
                      "Connected to an unexpected PostgreSQL database")
                cur.execute("SELECT pg_advisory_xact_lock(198315, 3100)")
                cur.execute("SET LOCAL lock_timeout = '5s'")
                cur.execute("SET LOCAL statement_timeout = '30s'")
                cur.execute("SELECT snapshot_id FROM ualp_career_snapshots WHERE snapshot_id = %s",
                            (SNAPSHOT_ID,))
                if cur.fetchone() is not None:
                    inspect_exact(cur, plan)
                    return {"status": "NOOP", "planSha256": PLAN_HASH,
                            "snapshots": 1, "requirements": 40}
                for (table, pk, columns), records in zip(TABLES, expected_rows(plan)):
                    col_sql = ",".join(columns)
                    marks = ",".join(["%s"] * len(columns))
                    insert = f"INSERT INTO {table} ({col_sql}) VALUES ({marks}) ON CONFLICT DO NOTHING"
                    for record in records:
                        cur.execute(insert, record)
                        guard(cur.rowcount == 1,
                              f"Existing identity/key conflicts with frozen plan: {table}")
                    if fault_after == "snapshots" and table == "ualp_career_snapshots":
                        raise CareerImportError("CI injected failure after snapshot insert")
                    if fault_after == "occupation_versions" and table == "ualp_career_occupation_versions":
                        raise CareerImportError("CI injected failure after version insert")
                    if fault_after == "requirements" and table == "ualp_career_requirements":
                        raise CareerImportError("CI injected failure after requirements insert")
                inspect_exact(cur, plan)
                return {"status": "INSERTED", "planSha256": PLAN_HASH,
                        "snapshots": 1, "requirements": 40}


def load_plan(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_frozen_plan(data)
    return data


def main() -> int:
    """No unsafe defaults; this command works only with the ephemeral CI mode."""
    import argparse
    parser = argparse.ArgumentParser(description="Strict one-snapshot O*NET import to ephemeral PG only")
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    plan = load_plan(args.plan)
    result = run_disposable_import(plan, os.environ.get("UALP_CI_DATABASE_URL", ""))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
