# UALP-MVP-001 — Render Free TEST deployment receipt

Date (UTC): 2026-11-15
Mode: BUILD_NEW_APP
Risk: L3 fresh isolated schema / experimental psychometric material
Source repo: VahramSargsyan/ualp-app (public)
Feature branch: feature/ualp-mvp-001-postgres-test
Exact deployed source SHA: b5398cb972e5e91897c998409d7ae283e56fd847
PR: https://github.com/VahramSargsyan/ualp-app/pull/2 (DRAFT, not merged)
Service: ualp-postgres-private-test
Service ID: srv-dbsr7pmk1f9s73a2rmp0
Render workspace: My Workspace (tea-d1r9ktmmcj7s73am6c10)
Render plan: FREE
Render region: Frankfurt
Auto deploy: OFF
Render initial deploy: dep-dbsr7q6k1f9s73a2rog0 (LIVE, SHA b5398cb972e5e91897c998409d7ae283e56fd847)
Render environment-only redeploy: dep-dbsra6u7bikc73c94b4g (source SHA d08c0b59723d61c5c8bebf068c0d7e936d1420ef; LIVE verified 2026-11-15 13:36 UTC)
Render TEST URL: https://ualp-postgres-private-test.onrender.com
Neon project: snowy-leaf-35157339 (ualp-postgres-test)
Neon database: ualp_test, PostgreSQL 18.7, Free organization

## Verified evidence

- Render build_ended = succeeded, deploy_ended = succeeded, get_deploy status = LIVE; SHA matched b5398cb... .
- Render app logs show Uvicorn startup complete on port 10000.
- Render logs show GET / HTTP/1.1 => 200 OK.
- GitHub Actions deterministic test workflow PASS on deployed source before deployment.
- Neon query confirmed 10 isolated UALP tables and one draft form: 21 items, 5 options, 27 scales, 42 links and 27 scoring rules.
- Neon SQL read-only scoring of a full synthetic high-response profile: 27 scales, 6 parent scales, zero coverage errors.

## Blocking env configuration

The sensitive Neon DATABASE_URL could not be transferred to Render via connected tools because the host safety layer blocked credential transmission between services. The block was not bypassed. Render was created WITHOUT DATABASE_URL and UALP_ACCESS_KEY; non-secret UALP_ENV=TEST was set. After the initial successful shell deployment, a fresh owner-only UALP_ACCESS_KEY was generated locally and added directly using the Render environment configuration tool. This triggered a second deployment. The **only** remaining missing variable is DATABASE_URL, which the owner must copy directly from Neon Console to Render Environment. Access key value is never stored in this public repository.

The web server is LIVE, but private assessment APIs are intentionally unavailable until DATABASE_URL is set by the owner in Render's Environment settings (UALP_ACCESS_KEY is already set). Never paste secrets into GitHub, issues, PR comments or public source. Use the Neon console Connect dialog for the pooled postgresql:// URL targeting the dedicated ualp_test database. Generate the owner key separately; never reuse a real password.

## NOT_RUN / next gate

- Live authenticated GET /api/forms/UALP_WV21_RU_LIKERT against Render + Neon: NOT_RUN (env not yet configured).
- Live POST /api/runs with 21 responses: NOT_RUN; no production/user test answers entered.
- Live idempotent repeat + rejected conflicting payload + independent PostgreSQL readback: NOT_RUN.
- Mobile layout usability with actual owner device: NOT_RUN.
- Browser health endpoint external fetch: NOT_RUN (provider tool could not directly open public Render URL); the Render logs show actual GET / returning 200.

## Rollback, risk and authorization

- Existing VBOS/ЖЭК, their databases and services untouched.
- New Render Free service is separable; stop/suspend it to pause use. Do not delete TEST DB or data without authorization.
- There is no PROD environment or permission.
- Render has five other Free services in the same workspace; shared free usage may suspend services at quota.
- Private TEST gate is a shared bearer key; not suitable for real external users or high-stakes use.
- The source Work Values pilot is DRAFT/NOT_REVIEWED; no validated psychometric results claimed.
- No cost-bearing resource intentionally selected. No Codex/paid API run.

Status: DEPLOYED_TEST_SHELL; DATABASE_NOT_CONNECTED; USER_ACCEPTANCE_BLOCKED.
