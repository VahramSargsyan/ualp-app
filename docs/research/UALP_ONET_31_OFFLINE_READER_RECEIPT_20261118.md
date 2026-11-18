# UALP — O*NET 31.0 source lock / offline reader receipt
Date: 2026-11-18
CAPABILITY: UALP-CAREER-KB-002
STATUS: PARTIAL / LOCAL_READER_TESTED / OFFICIAL_SOURCE_BYTES_BLOCKED
BASE_COMMIT: 8e98b8c38227ff6e4397a35daca4d3b7ce95f7b8
SOURCE_AUTHORITY: https://www.onetcenter.org/database.html
LICENCE: https://creativecommons.org/licenses/by/4.0/

## Exact source catalogue (official website evidence, no bytes acquired)

O*NET Database release **31.0** (August 2026). The following direct URLs were identified from the official page (CSV downloads):
- https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv
- https://www.onetcenter.org/dl_files/database/db_31_0_csv/essential_skills.csv
- https://www.onetcenter.org/dl_files/database/db_31_0_csv/scales_reference.csv

Official documentation:
- https://www.onetcenter.org/dictionary/31.0/csv/occupation_data.html
- https://www.onetcenter.org/dictionary/31.0/csv/essential_skills.html
- https://www.onetcenter.org/dictionary/31.0/csv/scales_reference.html

Published table counts (site metadata, NOT independently checked from downloaded files):
- occupation_data.csv: 1,016 rows
- essential_skills.csv: 18,200 rows
- scales_reference.csv: 33 rows

Fields verified in official dictionary: `O*NET-SOC Code, Title, Description` for occupations; `Scale ID, Scale Name, Minimum, Maximum` for scales; fifteen O*NET skill-rating metadata columns including `Recommend Suppress`, `Not Relevant`, `Date`, `Domain Source` in Essential Skills.

## Source acquisition blocker

Attempted official CSV through both web downloader and container HTTPS. Web reader returned cache miss for binary/CSV download; container could not resolve `www.onetcenter.org` (DNS NameResolutionError). No official CSV bytes were obtained. Therefore:
- SOURCE_FILES_DOWNLOADED: NO
- REAL_FILE_SHA256: UNKNOWN (no invented digests)
- REAL_ROW_READBACK: NOT_RUN
- REAL_OCCUPATION_SKILL_SUBSET: NOT_RUN
- OFFICIAL_SOURCE_LOCK: BLOCKED

Untrusted third-party mirrors or current-version Web Services API have **not** been substituted for an exact release. O*NET Services are not required for the offline reader and no account, key or paid service was created.

## Reader delivered

`career_kb/offline_reader.py` is offline-only and accepts exactly three named CSV files plus an operator-pinned JSON manifest. It verifies:
- named official 31.0 URLs, release and CC BY 4.0 metadata;
- exact UTF-8 source-file SHA-256 + byte size + rowCount before parsing;
- declared source headers, internal occupation code identity, scale reference and bounds;
- source element ID, deduplicated (occupation, element, scale) and description/scale label consistency;
- independent missingness states `OBSERVED / SUPPRESSED / NOT_RELEVANT / NOT_REPORTED`;
- 1–5 selected occupation codes; no implicit whole-database output, network, DB or score mapping.

Output explicitly sets `officialOriginVerified: false`: matching a manifest is **not** independent proof of official acquisition. Source provenance must be independently attested when direct download becomes available. The result includes a separate warning and `careerFitCalculated: false`, no learner data.

### Manifest structure

Required `source_lock.json` (to be generated only after independently obtaining the real CSV files):

```json
{
  "schemaVersion": "UALP-ONET-31.0-OFFLINE-LOCK-v1",
  "provider": "O*NET Database",
  "release": "31.0",
  "licenseUrl": "https://creativecommons.org/licenses/by/4.0/",
  "files": {
    "occupation_data.csv": {"sourceUrl": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv", "sha256": "<real lowercase sha256>", "sizeBytes": 0, "rowCount": 0},
    "essential_skills.csv": {"sourceUrl": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/essential_skills.csv", "sha256": "<real lowercase sha256>", "sizeBytes": 0, "rowCount": 0},
    "scales_reference.csv": {"sourceUrl": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/scales_reference.csv", "sha256": "<real lowercase sha256>", "sizeBytes": 0, "rowCount": 0}
  }
}
```

This example is intentionally **NOT VALID**; no source lock is claimed. Never replace unknown hashes with synthetic ones.

CLI (only after official bytes and verified manifest exist):
```sh
python -m career_kb.offline_reader --source-dir /path/to/exact-31-0-csv-files --manifest /path/to/verified-source_lock.json --occupation-code 15-2051.00
```

Occupation code in command is an illustrative lookup key, not an assertion that the corresponding file was parsed.

## Real tests performed

- Synthetic offline `python -m pytest -q tests/test_career_kb_offline_reader.py`: 12 PASS, 0 FAIL.
- `python -m compileall -q career_kb tests/test_career_kb_offline_reader.py`: PASS.
- Negative checks include modified bytes, fake digest, false source URL, unknown/duplicate selected role, duplicate skill link, invalid headers, out-of-range, non-finite source value, orphan scale, rowCount mismatch and missingness `null`.
- Real O*NET 31.0 dataset E2E: NOT_RUN (source acquisition blocked).
- GitHub Actions, Neon, Vercel, Android, full authenticated E2E: NOT_RUN. Existing assessment runtime untouched.
- Test fixtures contain fully invented occupation codes, content, ratings; they are **not real O*NET facts**.

## License/market boundary

The O*NET 31.0 Database is CC BY 4.0 with attribution, modification notice and no endorsement. This is distinct from O*NET Interest Profiler instrument licensing. U.S. occupation data do not establish Armenia employment demand, education equivalence or local licensing. No IQ, occupational ranking, score normalization or user-skill inference.

## Next exact technical blocker / safe resolution

In an outbound-network-enabled, authorized environment, download the **three official URLs above directly** (or through the already-authorized Cloud Browser in Work mode), retain response evidence and exact bytes, calculate SHA256/byte size/row counts, and run the same offline test against 1–2 actual occupation codes. Preserve source release and byte hashes in a frozen local receipt. No new paid API or account needed. Do **not** import to Neon until a distinct MIGRATION_PLAN and approval.

ROLLBACK: revert this documentation + Python-only change. No PostgreSQL data, TEST URL, main, Draft PR #7 or PROD touched.
