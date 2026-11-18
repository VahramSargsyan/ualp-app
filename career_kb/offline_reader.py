"""Fail-closed, read-only parser for checksum-pinned O*NET 31.0 CSV files.

Only verifies *local* byte integrity against a separately supplied manifest.
It never downloads data or authenticates provenance of the downloaded bytes.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from pathlib import Path

RELEASE = "31.0"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
PREFIX = "https://www.onetcenter.org/dl_files/database/db_31_0_csv/"
FILES = ("occupation_data.csv", "essential_skills.csv", "scales_reference.csv")
HEADERS = {
    "occupation_data.csv": ("O*NET-SOC Code", "Title", "Description"),
    "scales_reference.csv": ("Scale ID", "Scale Name", "Minimum", "Maximum"),
    "essential_skills.csv": (
        "O*NET-SOC Code", "Title", "Element ID", "Element Name",
        "Scale ID", "Scale Name", "Data Value", "N", "Standard Error",
        "Lower CI Bound", "Upper CI Bound", "Recommend Suppress",
        "Not Relevant", "Date", "Domain Source",
    ),
}
CODE = re.compile(r"\d{2}-\d{4}\.\d{2}\Z")
HEX = re.compile(r"[a-f0-9]{64}\Z")
MAX_BYTES = 32 * 1024 * 1024


class SourceLockError(ValueError):
    """Source format, identity, integrity or selected data are inconsistent."""


def require(test: bool, message: str) -> None:
    if not test:
        raise SourceLockError(message)


def finite_number(value: str, name: str) -> Decimal:
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError):
        raise SourceLockError(f"Invalid {name}") from None
    require(result.is_finite(), f"Nonfinite {name}")
    return result


def source_manifest(directory: Path, manifest: Path) -> dict:
    """Verify all three complete source files before parsing any subset."""
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    require(metadata.get("schemaVersion") == "UALP-ONET-31.0-OFFLINE-LOCK-v1", "Lock schema version")
    require(metadata.get("provider") == "O*NET Database", "Unsupported provider")
    require(metadata.get("release") == RELEASE, "Source release mismatch")
    require(metadata.get("licenseUrl") == LICENSE, "Source license mismatch")
    files = metadata.get("files")
    require(isinstance(files, dict) and set(files) == set(FILES), "Exact source files required")
    checks = {}
    for name in FILES:
        info = files[name]
        require(isinstance(info, dict), f"Missing {name} metadata")
        require(info.get("sourceUrl") == PREFIX + name, f"Source URL mismatch: {name}")
        expected_hash = info.get("sha256")
        expected_size = info.get("sizeBytes")
        expected_rows = info.get("rowCount")
        require(isinstance(expected_hash, str) and HEX.fullmatch(expected_hash) is not None,
                f"Missing exact SHA-256: {name}")
        require(type(expected_size) is int and 0 < expected_size <= MAX_BYTES,
                f"Invalid size: {name}")
        require(type(expected_rows) is int and 0 < expected_rows <= 100000,
                f"Invalid rowCount: {name}")
        path = directory / name
        require(path.is_file() and not path.is_symlink(), f"Missing safe file: {name}")
        raw = path.read_bytes()
        require(len(raw) == expected_size, f"Source size mismatch: {name}")
        require(hashlib.sha256(raw).hexdigest() == expected_hash,
                f"Source digest mismatch: {name}")
        checks[name] = {"sha256": expected_hash, "sizeBytes": expected_size,
                        "rowCount": expected_rows,
                        "sourceUrl": info["sourceUrl"]}
    return checks


def rows(directory: Path, name: str) -> list[dict[str, str]]:
    try:
        with (directory / name).open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            require(reader.fieldnames == list(HEADERS[name]), f"Unexpected columns in {name}")
            data = list(reader)
    except UnicodeDecodeError:
        raise SourceLockError(f"Invalid UTF-8 in {name}") from None
    require(data, f"Empty source {name}")
    require(all(None not in row and all(v is not None for v in row.values()) for row in data),
            f"Malformed CSV record: {name}")
    return data


def parse_subset(directory: Path, manifest: Path, selected_codes: list[str]) -> dict:
    """Parse a small occupation subset from complete, individually pinned files.

    Returns source-referenced occupational ratings, NOT career-suitability or
    individual learner scores. NOT_RELEVANT/SUPPRESSED/MISSING remain null.
    """
    require(0 < len(selected_codes) <= 5 and len(selected_codes) == len(set(selected_codes)),
            "Select 1-5 distinct occupations")
    require(all(CODE.fullmatch(code) is not None for code in selected_codes),
            "Invalid occupational code")
    checks = source_manifest(directory, manifest)
    occupations, skills, scales = (rows(directory, name) for name in FILES)
    for name, dataset in zip(FILES, (occupations, skills, scales)):
        require(len(dataset) == checks[name]["rowCount"], f"Row count mismatch: {name}")
    by_occ = {}
    for row in occupations:
        code = row["O*NET-SOC Code"]
        require(CODE.fullmatch(code) is not None and code not in by_occ,
                "Duplicate or invalid O*NET-SOC code")
        require(bool(row["Title"].strip()) and bool(row["Description"].strip()),
                "Empty occupation definition")
        by_occ[code] = row
    require(set(selected_codes).issubset(by_occ), "Requested occupation missing")

    by_scale = {}
    for row in scales:
        code = row["Scale ID"]
        require(code and code not in by_scale and row["Scale Name"].strip(),
                "Duplicate or empty scale")
        low = finite_number(row["Minimum"], "scale minimum")
        high = finite_number(row["Maximum"], "scale maximum")
        require(low < high, "Invalid scale interval")
        by_scale[code] = (low, high, row["Scale Name"])

    requirements = []
    seen = set()
    for row in skills:
        code, element, scale = (row[k] for k in ("O*NET-SOC Code", "Element ID", "Scale ID"))
        require(code in by_occ, "Skill references unknown occupation")
        require(scale in by_scale, "Skill references unknown scale")
        require(element.strip() and row["Element Name"].strip(), "Unknown skill element")
        require(row["Title"] == by_occ[code]["Title"], "Occupation title mismatch")
        require(row["Scale Name"] == by_scale[scale][2], "Scale label mismatch")
        identity = (code, element, scale)
        require(identity not in seen, "Duplicate occupation/skill/scale")
        seen.add(identity)
        require(row["Recommend Suppress"] in ("", "Y", "N") and
                row["Not Relevant"] in ("", "Y", "N"), "Unknown missingness flag")
        require(bool(row["Date"].strip()) and bool(row["Domain Source"].strip()),
                "Missing update provenance")
        if code not in selected_codes:
            continue
        low, high, scale_name = by_scale[scale]
        if row["Recommend Suppress"] == "Y":
            status, value = "SUPPRESSED", None
        elif row["Not Relevant"] == "Y":
            status, value = "NOT_RELEVANT", None
        elif row["Data Value"].strip() == "":
            status, value = "NOT_REPORTED", None
        else:
            decimal = finite_number(row["Data Value"], "skill rating")
            require(low <= decimal <= high, "Out-of-range skill rating")
            status, value = "OBSERVED", str(decimal)
        requirements.append({
            "occupationCode": code, "elementId": element,
            "elementName": row["Element Name"], "competencyKind": "ESSENTIAL_SKILL",
            "scaleId": scale, "scaleName": scale_name,
            "scaleMinimum": str(low), "scaleMaximum": str(high),
            "value": value, "evidenceStatus": status,
            "updatedAtSource": row["Date"], "domainSource": row["Domain Source"],
        })
    require(requirements, "Selected occupations have no sourced skill records")
    return {
        "dataset": "O*NET Database", "release": RELEASE,
        "geography": "United States / O*NET-SOC taxonomy",
        "licenseUrl": LICENSE,
        "integrityStatus": "LOCAL_BYTES_MATCH_DECLARED_SHA256",
        "officialOriginVerified": False,
        "warning": "Offline file hashes are NOT independent proof of official download origin",
        "sourceFiles": checks,
        "occupations": [
            {"occupationCode": code, "title": by_occ[code]["Title"],
             "description": by_occ[code]["Description"]} for code in selected_codes
        ],
        "requirements": requirements,
        "careerFitCalculated": False, "learnerEvidence": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read pinned O*NET 31.0 CSV offline; no network or DB")
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--occupation-code", required=True, action="append", dest="codes")
    args = parser.parse_args()
    result = parse_subset(args.source_dir, args.manifest, args.codes)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
