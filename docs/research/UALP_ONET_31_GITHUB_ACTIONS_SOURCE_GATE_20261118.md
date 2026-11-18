# UALP O*NET 31.0 — one-time GitHub Actions source-lock
Date: 2026-11-18
CAPABILITY: UALP-CAREER-KB-003
STATUS: OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS (run #44322510909)
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



## Exact execution result — 2026-11-18 14:16 UTC

STATUS: **OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS**
RUN_ID: **44322510909**; RUN_ATTEMPT: **1**; CONCLUSION: **SUCCESS**.
RUN_URL: https://github.com/VahramSargsyan/ualp-app/actions/runs/44322510909
WORKFLOW_EXACT_COMMIT: `1171ece481fde70a7493ddf581fb0a54d9f6fa68` (initial source+workflow).
JOB_ID: `134864896990` — acquire-and-validate / SUCCESS.
ARTIFACT_ID: `14435511727`
ARTIFACT_URL: https://github.com/VahramSargsyan/ualp-app/actions/runs/44322510909/artifacts/14435511727
ARTIFACT_SHA256: `4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d`
ARTIFACT_EXPIRES: **2026-11-25 14:16 UTC** (7-day GitHub retention). **Download/save the ZIP before expiry.** ZIP contains all three exact O*NET CSVs, source_lock.json, acquisition_receipt.json and real_occupation_skill_subset.json.

Independent artifact readback at recipient: zip CRC PASS; 3 raw CSV SHA256 recomputed and exactly equal to the generated manifest; exact official origin URL echoed by GitHub TLS/HTTP response; HTTP 200; full CSV 1016/18200/33 data rows confirmed; 2 occupations, 40 source-backed skill rating rows. This validates received file bytes against the directly fetched data. The offline reader's `officialOriginVerified: false` is *by design*: pure local checksum validation cannot independently attest remote origin; separately captured GitHub HTTPS transport evidence supports source provenance.

| Source file | Exact SHA256 | Bytes | Data rows |
|---|---|---:|---:|
| occupation_data.csv | `a09eae1d6609686e44e05b7290993a1c8b523d8ca224bc0eedc194c855c3ee02` | 268030 | 1016 |
| essential_skills.csv | `68c4d31d8c55077238395dca40cc4e6d32e6a608b5474bb8264b1f98ae415bd7` | 2328135 | 18200 |
| scales_reference.csv | `bcba23858ce21ecaacbde303a8993e35d46724b4afb8c9ec2b10e04f42adcfc9` | 1006 | 33 |

**Actual role subset:**
- `15-2051.01` — Business Intelligence Analysts.
- `15-2051.00` — Data Scientists.
- 40 essential-skills measure records: **39 OBSERVED, 1 SUPPRESSED**. Suppressed value stays `null`. Both `IM` (1–5) and `LV` (0–7) source scales preserved, never normalized to career fit.
- All downloaded files carry O*NET 31.0 Database CC BY 4.0 attribution to USDOL/ETA; extracted/filtered subset is a UALP transformation without endorsement.

VERIFICATION: GitHub Actions PASS; real-source local reader PASS within runner; ZIP CRC + raw-file hash/row receipt independent PASS.
NOT_RUN: PostgreSQL schema/import, Neon TEST, Vercel authenticated runtime, Android, UAT; all intentionally out of scope.
ROLLBACK: leave separate branch unmerged or revert document commits. No existing application or data touched.
NEXT_BOUNDARY: if later authorized, plan separately scoped additive Career KB schema/source import and migration+rollback. The one-shot trigger is path-filtered to workflow file, which is unchanged in this receipt-only commit.
