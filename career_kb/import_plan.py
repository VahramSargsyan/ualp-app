"""Deterministic, source-locked Career KB import *proposal* (never writes a DB).

Outputs logical rows for a separately authorized additive PostgreSQL migration.
No external API calls, personal data, assessment scoring or migration execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from career_kb.offline_reader import (
    RELEASE, FILES, PREFIX, LICENSE, SourceLockError, parse_subset,
)

SCHEMA = "UALP-CAREER-KB-IMPORT-PLAN-v0.1"
DEFAULT_CODES = ("15-2051.00", "15-2051.01")


def _guard(condition: bool, message: str) -> None:
    if not condition:
        raise SourceLockError(message)


def _canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _official_receipt(receipt_path: Path | None, file_checks: dict) -> dict:
    if receipt_path is None:
        return {"status": "NOT_ATTESTED", "capturedAtUtc": None, "runCommit": None}
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    _guard(receipt.get("release") == RELEASE and receipt.get("officialURLsOnly") is True,
           "Official download receipt is missing or mismatched")
    _guard(receipt.get("status") == "OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS",
           "Official receipt did not PASS")
    _guard(receipt.get("noDatabaseWrites") is True and receipt.get("noCareerScoring") is True,
           "Unexpected receipt activity")
    files = receipt.get("files")
    _guard(isinstance(files, dict) and set(files) == set(FILES),
           "Incomplete official receipt")
    for filename in FILES:
        evidence = files[filename]
        locked = file_checks[filename]
        _guard(evidence.get("httpStatus") == 200 and
               evidence.get("sourceUrl") == PREFIX + filename and
               evidence.get("finalUrl") == PREFIX + filename and
               evidence.get("sha256") == locked["sha256"] and
               evidence.get("sizeBytes") == locked["sizeBytes"] and
               evidence.get("rowCount") == locked["rowCount"],
               f"Official receipt/hash mismatch for {filename}")
    ts = receipt.get("completedAtUTC")
    _guard(isinstance(ts, str) and (ts.endswith("+00:00") or ts.endswith("Z")),
           "Official receipt timestamp missing")
    commit = receipt.get("triggerCommit")
    _guard(isinstance(commit, str) and len(commit) == 40 and
           all(c in "0123456789abcdef" for c in commit), "Invalid workflow source commit")
    return {"status": "GITHUB_HTTPS_RECEIPT_MATCHES_LOCK",
            "capturedAtUtc": ts, "runCommit": commit}


def make_import_plan(source_dir: Path, manifest: Path, codes: list[str],
                     receipt: Path | None = None) -> dict:
    """Verify full original CSV set then emit a bounded, deterministic data plan.

    Real source URLs and all three hashes must already be locked by the
    offline reader. The output is NOT SQL; it has no database side effects.
    """
    _guard(bool(codes) and len(codes) == len(set(codes)) and len(codes) <= 2,
           "This pilot permits exactly 1 or 2 distinct occupational codes")
    _guard(set(codes).issubset(DEFAULT_CODES), "Pilot occupations must be pre-reviewed")
    selected = sorted(codes)
    source = parse_subset(source_dir, manifest, selected)
    checks = source["sourceFiles"]
    attestation = _official_receipt(receipt, checks)
    manifest_sha256 = hashlib.sha256(manifest.read_bytes()).hexdigest()
    snapshot_id = "ONET_DB_31_0"

    occupations = []
    occupation_versions = []
    for occupation in source["occupations"]:
        code = occupation["occupationCode"]
        oid = f"UALP_OCC_ONET_SOC:{code}"
        occupations.append({"occupationId": oid, "taxonomy": "O*NET-SOC",
                            "externalCode": code})
        occupation_versions.append({"occupationVersionId": f"ONET_31_0_OCC:{code}",
                                    "occupationId": oid, "snapshotId": snapshot_id,
                                    "externalCode": code, "sourceLocale": "en",
                                    "title": occupation["title"],
                                    "description": occupation["description"]})

    competencies = {}
    competency_versions = {}
    scales = {}
    requirements = []
    for row in source["requirements"]:
        element, code, scale = row["elementId"], row["occupationCode"], row["scaleId"]
        cid = f"UALP_ONET_ESSENTIAL_SKILL:{element}"
        cvid = f"ONET_31_0_SKILL:{element}"
        competencies[cid] = {"competencyId": cid, "kind": "ESSENTIAL_SKILL",
                             "providerElementId": element}
        ver = {"competencyVersionId": cvid, "competencyId": cid,
               "snapshotId": snapshot_id, "sourceLocale": "en",
               "label": row["elementName"]}
        _guard(cvid not in competency_versions or competency_versions[cvid] == ver,
               "Conflicting labels for one source skill")
        competency_versions[cvid] = ver
        srow = {"snapshotId": snapshot_id, "scaleId": scale,
                "label": row["scaleName"], "minimum": row["scaleMinimum"],
                "maximum": row["scaleMaximum"]}
        _guard(scale not in scales or scales[scale] == srow,
               "Conflicting scale definitions")
        scales[scale] = srow
        requirements.append({
            "requirementId": f"ONET_31_0_REQ:{code}:{element}:{scale}",
            "snapshotId": snapshot_id,
            "occupationVersionId": f"ONET_31_0_OCC:{code}",
            "competencyVersionId": cvid,
            "sourceRecordId": f"O-NET31:ESSENTIAL_SKILLS:{code}:{element}:{scale}",
            "scaleId": scale,
            "scaleMinimum": row["scaleMinimum"],
            "scaleMaximum": row["scaleMaximum"],
            "rawValue": row["value"],
            "evidenceStatus": row["evidenceStatus"],
            "updatedAtSource": row["updatedAtSource"],
            "domainSource": row["domainSource"],
        })
    requirements.sort(key=lambda r: r["requirementId"])
    _guard(len(set(r["requirementId"] for r in requirements)) == len(requirements),
           "Duplicate requirement IDs")
    # A single selected occupation in release 31.0 has 10 skills * 2 scales.
    _guard(len(requirements) == len(selected) * 20 and
           len(competencies) == 10 and set(scales) == {"IM", "LV"},
           "Unexpected pilot source coverage")
    _guard(sum(r["evidenceStatus"] != "OBSERVED" for r in requirements)
           == sum(r["rawValue"] is None for r in requirements),
           "Suppressed / missing values were transformed")

    plan = {
        "schemaVersion": SCHEMA,
        "readOnly": True,
        "mutationAuthorized": False,
        "personalData": False,
        "careerFitCalculated": False,
        "sourceAttestation": attestation,
        "sourceSnapshot": {
            "snapshotId": snapshot_id,
            "provider": source["dataset"], "release": source["release"],
            "licenseUrl": LICENSE, "geography": source["geography"],
            "manifestSha256": manifest_sha256,
            "files": {name: checks[name] for name in FILES},
        },
        "occupations": sorted(occupations, key=lambda r: r["occupationId"]),
        "occupationVersions": sorted(occupation_versions,
                                     key=lambda r: r["occupationVersionId"]),
        "competencies": [competencies[k] for k in sorted(competencies)],
        "competencyVersions": [competency_versions[k] for k in sorted(competency_versions)],
        "scales": [scales[k] for k in sorted(scales)],
        "requirements": requirements,
    }
    # The digest covers the entire immutable plan, except the digest itself.
    plan["planSha256"] = hashlib.sha256(_canonical(plan)).hexdigest()
    return plan


def main() -> int:
    arg = argparse.ArgumentParser(description="Generate read-only O*NET Career KB migration input proposal")
    arg.add_argument("--source-dir", required=True, type=Path)
    arg.add_argument("--manifest", required=True, type=Path)
    arg.add_argument("--receipt", type=Path, help="Exact GitHub Actions acquisition receipt")
    arg.add_argument("--occupation-code", dest="codes", action="append", required=True)
    arg.add_argument("--output", required=True, type=Path)
    args = arg.parse_args()
    plan = make_import_plan(args.source_dir, args.manifest, args.codes, args.receipt)
    _guard(args.output.suffix == ".json" and not args.output.exists(),
           "Must use a new .json output path; existing files are immutable")
    args.output.write_text(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(f"CAREER_KB_IMPORT_PLAN_ONLY PASS: {plan['planSha256']} "
          f"roles={len(plan['occupations'])} requirements={len(plan['requirements'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
