# UALP-MVP-001 Build Packet — PostgreSQL private TEST revision

DECISION_SOURCE: Owner on 2026-11-15 explicitly rejected Apps Script and requested a normal database at zero cost. This change supersedes the earlier Apps Script technology choice for the NEW UALP implementation. Main remains unchanged until review.

CAPABILITY_ID: UALP-MVP-001
USER_RESULT: One owner completes a 21-item draft Work Values assessment on mobile or desktop; answers and reproducible 6 parent / 27 total scale scores persist atomically in PostgreSQL.
WORKFLOW_MODE: BUILD_NEW_APP
RISK_CLASS: L3 (new persisted data schema; isolated TEST only)
BASE_COMMIT: 2387d9759e834b42432fcfacf31a53215e4e11fc
OWNER_BRANCH: feature/ualp-mvp-001-postgres-test
TEST_TARGET: existing Neon Free project snowy-leaf-35157339 / ualp_test; Vercel Hobby Preview only (non-commercial personal pilot). The owner replaced Render with Vercel on 2026-11-15.
PROD: NOT_AUTHORIZED / NOT_CONFIGURED
PAID_API_BUDGET: 0
EXECUTOR_PERMISSION: current assistant only; no Codex.

CANONICAL_SOURCE_OF_TRUTH:
- Candidate assessment source v0.7 is a provenance reference, not a silently updated live dependency. After approved one-time source-reviewed import, PostgreSQL holds versioned assessment content and runtime state in separated tables.
- Google Sheets/Apps Script must not be a production or runtime dependency. Never upload unreviewed item bank contents, objective answer keys, participant responses, credentials or secrets to public GitHub.

SCOPE: Standalone Python/FastAPI browser interface, PostgreSQL schema, initial development-only Work Values pilot, server-side scoring, strict 21-answer validation, explicit consent, atomic response/score commit, idempotency, TEST authentication, tests and free-hosting configuration.
OUT_OF_SCOPE: 13 remaining modules, live employer/hiring decisions, public respondent signup, role matching, learning engine, PROD, payments and paid services.
MODULES: app.py (Vercel adapter), webapp/, tests/, migrations/, requirements.txt, docs/. Legacy render.yaml is retained only as a prior deployment record; not a build target.
SHARED_HOTSPOTS: imported canonical IDs, scoring algorithm, database schema version, source-license/translation status, private data boundary.
DO_NOT_TOUCH: VBOS, ЖЭК, existing Neon proud-hat project, any production app, canonical assessment workbook/source.

SCHEMA_IMPACT: Dedicated NEW PostgreSQL database only, no existing user data migrated. New ualp_ namespace tables; no destructive migration. Once accepted, any change requires versioned MIGRATION_PLAN and rollback.
MIGRATION_PLAN: One-time, content-reviewed import from v0.7 source into new isolated tables; source snapshot remains immutable. Never auto-reset or overwrite saved answer data. Initial empty database install is additive.
DEPENDENCIES: Python 3.12, FastAPI, psycopg 3, Neon Free PostgreSQL 18, Vercel Hobby Preview (free only). No Google Apps Script, Render runtime or paid API required.
ACCEPTANCE: 21 questions/5 options; scoring 0–4 raw MEAN by 6 domains and 21 facets; 21 responses and 27 scores committed per run; duplicate retry creates no second run; conflicting retry rejected; incomplete/invalid content rejected; private TEST gate; accessible mobile page; live Neon readback.
REQUIRED_EVIDENCE: local deterministic tests, actual PostgreSQL TEST integration, server health, deployed TEST smoke, exact commit/URL, privacy and duplicate retry negative tests.
ROLLBACK: Vercel Preview is disposable; retain isolated Neon database and source, leave main unchanged. Previous Render UALP shell may be suspended separately without touching VBOS. No destructive migration.
UNRESOLVED_DECISIONS: Source workbook rights and public reuse, future user account model, formal content validation and production privacy policy. These block publication/hiring, not a private single-owner pilot.
AUTHORIZATION_END: report this bounded block; no PROD or next feature implied.


## UALP-MVP-002 — history and reopening saved results (2026-11-16)

CAPABILITY_ID: UALP-MVP-002
USER_RESULT: Owner enters existing TEST access key, sees a bounded list of completed Work Values runs ordered newest first and reopens the existing six-domain scores, including the first completed run.
WORKFLOW_MODE: IMPLEMENT_FEATURE
RISK_CLASS: L2 — private read-only history API and mobile UI, no data mutation.
BASE_COMMIT: cdbcc5779de0b8128fc1fe769408ac49cc3dcc81
OWNER_BRANCH: feature/ualp-mvp-002-history-test (depends on unmerged MVP-001 branch; do not promote to main)
TEST_TARGET: isolated Vercel Hobby Preview; isolated Neon Free ualp_test readback; real PostgreSQL 18 synthetic CI.
OWNER / TEST: Vahram / Vercel Preview-only.
CANONICAL: ualp_assessment_runs and ualp_scale_scores already persisted in Neon; never derive history from local browser storage.
SCOPE: existing key-gated GET /api/history (max 10 per page, stable keyset cursor, completed runs only), links to existing key-gated GET /api/runs/{run_id}, mobile history UI and return navigation, bounded CI/real-DB integration.
OUT_OF_SCOPE: accounts, identities/multi-user, edits/deletes, raw answer replay, public access, new psychometric interpretations, PR merge, PROD, paid infrastructure.
SHARED_HOTSPOTS: webapp/main.py; webapp/index.html; tests/test_real_postgres_integration.py.
SCHEMA_IMPACT: NONE; reuse existing (form_id, created_at DESC) index. No new tables/columns/stable IDs/statuses.
MIGRATION_PLAN: NONE. Existing run stays unchanged. Rollback: revert history commit/Preview branch; MVP-001 Preview and DB remain untouched.
ACCEPTANCE: require TEST key, history newest-first, 10 max per page with cursor, exact first run visible, reopen original six stored scores, no response leakage, inaccessible unauthorized, cursor errors 422, no inserted rows.
REQUIRED_EVIDENCE: deterministic tests, ephemeral real Postgres integration, Vercel Preview exact commit, owner phone scenario, Neon read-only record counts.
PAID_API_BUDGET: 0; EXECUTOR: current assistant only.
UNRESOLVED_DECISIONS: NONE within one-owner TEST; multi-user ownership and retention remain future, not assumed here.
AUTHORIZATION_END: report MVP-002 and stop; no main merge or PROD.
