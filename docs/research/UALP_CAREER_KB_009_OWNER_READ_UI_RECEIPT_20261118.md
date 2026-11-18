# UALP-CAREER-KB-009 — Owner-only O*NET profession explorer
DATE: 2026-11-18
MODE: IMPLEMENT_FEATURE
STATUS: SOURCE_COMMITTED / LOCAL_CONTRACT_PASS / NEON_READBACK_PASS / VERCEL_RUNTIME_NOT_RUN
BASE_COMMIT: d18f4c8e53396616c3a0437a504da599a5a54987
GITHUB_BRANCH: feature/ualp-career-kb-009-owner-read-ui
EXACT_UI_AND_BACKEND_COMMIT: 001cdea714dfe70bb34109c96fdf7f0fff10d3fb

## Completed owner outcome
Added an owner-session-protected Career KB read API and a separate in-app profession view. Existing FastAPI endpoints, persisted assessment data and RIASEC/Work Values scoring unchanged. The source is O*NET Database 31.0, attribution USDOL/ETA, CC BY 4.0, U.S.-only taxonomy; UALP is not endorsed by the source provider.

New API: GET /api/careers and GET /api/careers/{code}. Uses the same `authorized` dependency from webapp/main.py. Returns only two allowlisted source occupational descriptions: 15-2051.00 Data Scientists, 15-2051.01 Business Intelligence Analysts, with ten essential skill descriptors and exactly twenty raw O*NET measurements for each. Distinct Importance [1–5] and Level [0–7] scales retained; null SUPPRESSED stays null and is not treated as zero.

Safety gates: UALP_ENV=TEST; exact UALP Neon TEST database and role with Neon endpoint; snapshot manifest SHA256 03bbd9bd709eab4ac764a940f5110ab9292645b67d34c3ef600f28fcc3f9da78, three official CSV SHA256 values, seven table row counts and full content digests exactly equal to verified 008 release. Any source or database drift yields 503 without source detail. Unknown career code yields 404. SQL transaction explicitly read only; no response/user-profile/assessment joins; all client source fields rendered by DOM textContent, no HTML injection.

## Code and test scope
- career_kb/owner_read_api.py — strict source-lock API and two GET route handlers (wired at end of webapp/main.py).
- webapp/main.py — only TEST app version increase and a router hook; preserves owner session.
- webapp/index.html — additive profession section, dashboard button, read-only details and attribution; all other screens remain.
- tests/test_career_kb_owner_read_api.py — 15 isolated FastAPI contract tests using fabricated rows; 401, 404, 405, 503 negative tests, exact source/DB gates and SUPPRESSED/null.
- tests/verify_career_kb_ui.cjs — independent synthetic browser/DOM smoke, no credentials or live data.

LOCAL_CHECKS: Python pytest **15 PASS / 0 FAIL**, `compileall` PASS; Node JavaScript syntax PASS and synthetic owner UI smoke PASS. Static integration readback after GitHub commit requires checking exact blob paths. Full application pytest NOT_RUN in current Python container (psycopg unavailable). Do not label fixture HTTP tests a real Neon-bound API runtime.

NEON_TEST_READBACK: independent read-only SQL against project snowy-leaf-35157339 / ualp_test shows both source occupations, 10 distinct skills/20 source measurements each (one SUPPRESSED/null), exact source release and file hash; no database writes in 009.

## Blocker and recovery
Vercel account connector returned **zero UALP projects and zero available deployments** under the connected Hobby team and default account. Do not create a replacement project or invent an existing URL. Exact hosted Preview deploy, signed owner mobile flow, endpoint verification and owner UAT: **NOT_RUN**.
This is a code-only block; rollback is revert the separate feature branch. No database migration, backup or restore required and no PROD action.
OWNER PR #7, existing Vercel Preview and GitHub main remain unchanged.
NEXT_BOUNDARY: recover the previously authorized Vercel project connection and deliver an exact-commit Preview, then check owner login, both occupation cards, the SUPPRESSED cell, HTTPS failure states, mobile UI and preserved existing assessment flows. No job fitting/matching algorithm authorized.
STOP after this bounded source and verification receipt.
