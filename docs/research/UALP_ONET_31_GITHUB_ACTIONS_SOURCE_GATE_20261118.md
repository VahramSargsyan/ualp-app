# UALP O*NET 31.0 — one-time GitHub Actions source-lock
Date: 2026-11-18
CAPABILITY: UALP-CAREER-KB-003
STATUS: WORKFLOW_SUBMITTED / RUN_OUTCOME_NOT_YET_OBSERVED
BASE_COMMIT: a2b060a0295f612aca3127fdd6753b8304e5815a
WORKFLOW_BRANCH: feature/ualp-onet-31-source-lock-once
TRIGGER: one scoped push changing .github/workflows/ualp-onet-31-source-lock-once.yml on this branch only.
GITHUB_ACTIONS: explicit owner approval 2026-11-18 to run one source-lock workflow; additional executors/Codex/paid APIs NOT AUTHORIZED.
PUBLIC_REPOSITORY: yes; GitHub-hosted public-repo Actions no paid API expenditure planned.
SOURCE: https://www.onetcenter.org/database.html; O*NET 31.0 CC BY 4.0.
OFFICIAL_FILE_URLS: exact file URLs as previously frozen in docs/research/UALP_ONET_31_OFFLINE_READER_RECEIPT_20261118.md.
EXPECTED_ROWS: occupation_data.csv=1016; essential_skills.csv=18200; scales_reference.csv=33 (official page metadata).
SOURCE_RECEIPT: Job downloads official HTTPS CSV files into RUNNER_TEMP; rejects unexpected redirect, wrong status, HTML, corrupted bytes, schema or changed row counts; records SHA-256, source URL, timestamp, byte length; creates source_lock.json; runs the existing offline reader on two present real occupations (preferred BI Analyst, Data Scientist, plumber), with correct-source check.
ARTIFACT: ualp-onet31-one-shot-source-lock-evidence, 7 days, includes source_lock.json, exact downloaded CSVs and readback subset (if available), and acquisition_receipt.json on blocked attempts.
BOUNDARY: No network fallback/mirror, secrets, authentication, paid API, database access, schema change, owner scores, Vercel TEST, Android, main, current Draft PR #7 or PROD.
SECURITY: permissions contents:read, checkout persist-credentials:false, no PR/head untrusted arbitrary scripts, one push path/branch trigger, no workflow_dispatch, 8 minute job timeout.
ROLLBACK: revert/delete separate experiment branch only; existing source branch at a2b060a0295f612aca3127fdd6753b8304e5815a and owner TEST code remain as-is. No data restore needed.
EVIDENCE_REQUIRED: inspect exact workflow run ID/job logs/artifact receipt and validate source hash/readback. HTTP/DNS error or schema mismatch is BLOCKED, not PASS.
STOP: after one actual job attempt plus at most bounded evidence-driven fix if needed; do not start other blocks automatically.
