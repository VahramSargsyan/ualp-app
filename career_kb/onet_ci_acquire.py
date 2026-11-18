"""One-shot O*NET 31.0 official CSV acquisition and exact offline reader check.

No credentials, paid APIs, database access, network fallback, or repo writes.
This helper is intended only for the separately-scoped GitHub Actions check.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.request

from career_kb.offline_reader import (
    FILES, HEADERS, LICENSE, MAX_BYTES, PREFIX,
    SourceLockError, parse_subset, require,
)

EXPECTED_ROWS = {
    "occupation_data.csv": 1016,
    "essential_skills.csv": 18200,
    "scales_reference.csv": 33,
}
PREFERRED_CODES = ("15-2051.01", "15-2051.00", "47-2152.00")
USER_AGENT = "UALP-Source-Verification/1.0 (noncommercial offline O*NET database QA)"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def csv_records(raw: bytes, filename: str) -> list[dict[str, str]]:
    """Validate exact 31.0 schema and complete, clean CSV records."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise SourceLockError(f"Non-UTF-8 official source: {filename}") from None
    reader = csv.DictReader(io.StringIO(text, newline=""))
    require(reader.fieldnames == list(HEADERS[filename]), f"31.0 source header mismatch: {filename}")
    records = list(reader)
    require(bool(records), f"Empty source: {filename}")
    require(all(None not in row and all(v is not None for v in row.values()) for row in records),
            f"Malformed CSV record: {filename}")
    return records


def download_official(filename: str) -> tuple[bytes, dict]:
    """Bounded HTTPS request to exact official URL; no redirects to another origin."""
    require(filename in FILES, "Unapproved filename")
    url = PREFIX + filename
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/csv,application/octet-stream,*/*;q=0.8",
    })
    with urllib.request.urlopen(request, timeout=35) as response:
        require(response.status == 200, f"Official server HTTP {response.status}: {filename}")
        final_url = response.geturl()
        require(final_url == url, f"Official source redirected: {filename}")
        content_type = response.headers.get("Content-Type", "").lower()
        require("text/html" not in content_type, f"Unexpected HTML: {filename}")
        raw = response.read(MAX_BYTES + 1)
        require(0 < len(raw) <= MAX_BYTES, f"Source byte size invalid: {filename}")
        metadata = {
            "sourceUrl": url,
            "finalUrl": final_url,
            "httpStatus": response.status,
            "contentType": content_type,
            "retrievedAtUTC": timestamp(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "sizeBytes": len(raw),
        }
    return raw, metadata


def select_occupations(occupations: list[dict], skills: list[dict]) -> list[str]:
    """Select two real O*NET occupations with actual Essential Skills records."""
    actual = {row["O*NET-SOC Code"] for row in occupations}
    skills_codes = {row["O*NET-SOC Code"] for row in skills}
    selected = [code for code in PREFERRED_CODES if code in actual and code in skills_codes][:2]
    require(len(selected) == 2, "Two preferred real occupations with Essential Skills unavailable")
    return selected


def acquire(source_dir: Path, report_dir: Path, commit_sha: str) -> dict:
    source_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "capabilityId": "UALP-CAREER-KB-003",
        "release": "31.0",
        "status": "IN_PROGRESS",
        "triggerCommit": commit_sha,
        "startedAtUTC": timestamp(),
        "officialURLsOnly": True,
        "files": {},
        "noDatabaseWrites": True,
        "noCareerScoring": True,
    }
    receipt_path = report_dir / "acquisition_receipt.json"
    try:
        lock = {
            "schemaVersion": "UALP-ONET-31.0-OFFLINE-LOCK-v1",
            "provider": "O*NET Database",
            "release": "31.0",
            "licenseUrl": LICENSE,
            "files": {},
        }
        datasets = {}
        for filename in FILES:
            raw, metadata = download_official(filename)
            records = csv_records(raw, filename)
            require(len(records) == EXPECTED_ROWS[filename],
                    f"Frozen 31.0 row count differs: {filename} ({len(records)})")
            (source_dir / filename).write_bytes(raw)
            metadata["rowCount"] = len(records)
            receipt["files"][filename] = metadata
            lock["files"][filename] = {
                "sourceUrl": metadata["sourceUrl"],
                "sha256": metadata["sha256"],
                "sizeBytes": metadata["sizeBytes"],
                "rowCount": metadata["rowCount"],
            }
            datasets[filename] = records

        manifest_path = report_dir / "source_lock.json"
        manifest_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        codes = select_occupations(datasets["occupation_data.csv"], datasets["essential_skills.csv"])
        subset = parse_subset(source_dir, manifest_path, codes)
        require(len(subset["occupations"]) == 2, "Did not read two actual occupations")
        assert subset["careerFitCalculated"] is False
        for code in codes:
            require(any(r["occupationCode"] == code for r in subset["requirements"]),
                    f"Missing sourced skills: {code}")
        (report_dir / "real_occupation_skill_subset.json").write_text(
            json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        receipt.update({
            "status": "OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS",
            "completedAtUTC": timestamp(),
            "selectedOccupationCodes": codes,
            "selectedTitles": [o["title"] for o in subset["occupations"]],
            "selectedRequirementCount": len(subset["requirements"]),
            "fileHashesIndependentlyFromOfficialTLSDownloads": True,
            "localReaderOriginClaim": subset["officialOriginVerified"],
            "sourceLicenseAttribution": (
                "O*NET 31.0 Database by USDOL/ETA, CC BY 4.0; "
                "no endorsement; data unchanged in full CSV files, subset extracted by UALP"
            ),
        })
        return receipt
    except Exception as exc:
        receipt.update({
            "status": "BLOCKED_FAIL_CLOSED",
            "completedAtUTC": timestamp(),
            "errorType": type(exc).__name__,
            "error": str(exc)[:400],
        })
        raise
    finally:
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"O*NET source acquisition status: {receipt['status']}")
        if receipt["status"] == "OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS":
            print("Real occupations: " + ", ".join(receipt["selectedOccupationCodes"]))
            print("Requirements: " + str(receipt["selectedRequirementCount"]))
        else:
            print("Blocker: " + receipt.get("errorType", "Unknown"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Official O*NET 31.0 source lock in a one-shot CI runner")
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--commit-sha", required=True)
    args = parser.parse_args()
    acquire(args.source_dir, args.report_dir, args.commit_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
