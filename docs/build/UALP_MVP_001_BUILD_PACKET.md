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


## UALP-MVP-003 — single-owner derived profile from completed assessments (2026-11-16)

CAPABILITY_ID: UALP-MVP-003
USER_RESULT: After entering the existing TEST key, the owner sees a consolidated read-only profile showing which assessment methods have actually been completed, number of completions, date and version of latest completion, and saved parent-scale values. Reassessment updates the latest snapshot. Methods not completed/validated appear as pending, NEVER fabricated results.
WORKFLOW_MODE: IMPLEMENT_FEATURE
RISK_CLASS: L2 — limited read-only output on sensitive profile scores, no schema change.
BASE_COMMIT: 8c5439dc4d06c93fccf797c532502e730f35c7f0 (MVP-002 USER_ACCEPTED_TEST)
OWNER_BRANCH: feature/ualp-mvp-003-profile-test
TEST_TARGET: distinct Vercel Hobby Preview for MVP-003, existing isolated Neon Free ualp_test; ephemeral PostgreSQL 18 in CI with synthetic data.
OWNER / TEST: Vahram / UALP owner-only private TEST.
CANONICAL_SOURCE: ualp_assessment_runs, ualp_catalog_forms, ualp_scale_scores and ualp_catalog_scales; no alternate browser cache or hand-authored scores.
SCOPE: key-gated GET /api/profile; group stored COMPLETED runs by form, show latest run per method and count, only parent scores, track no scores for uncompleted methods; mobile profile accessible without re-taking questions; view latest saved result; preserve existing history and test flows.
OUT_OF_SCOPE: user accounts/IDs, cross-user profiles, storage of inferred traits, cross-test psychometric norms, fit/readiness scoring, career advice, new tests/catalog imports, local credential storage, paid or PROD deployment, merging unaccepted PRs.
SHARED_HOTSPOTS: webapp/main.py, webapp/index.html, tests/test_real_postgres_integration.py and CI workflows.
SCHEMA_IMPACT / MIGRATION_PLAN: NONE. Derive profile read-only from existing 10-table catalog/runtime and existing index; do not touch stored IDs, statuses, scores, responses or version schema. Do not leak responses or scoring keys into profile JSON.
ACCEPTANCE: no/invalid key denied; empty profile is truthful; one saved method returns 1 Work Values with 1 run and six original parent scores; second synthetic assessment demonstrates independent method groups; subsequent completion updates latest snapshot; no DB writes; no false RIASEC/ICAR scores; mobile navigation and return to old history / questionnaire work.
REQUIRED_EVIDENCE: GitHub Python+JS checks, ephemeral real PostgreSQL integration (single/second method and updated latest), exact Vercel Preview deploy, read-only Neon counts, owner phone acceptance.
ROLLBACK: revert MVP-003 Preview branch only; user profile is derived, so no data migration or stored-profile deletion. MVP-002 accepted Preview and Neon unchanged.
PAID_API_BUDGET: 0; EXECUTOR_PERMISSION: current assistant only.
UNRESOLVED_DECISIONS: NONE for single-owner noncommercial TEST. Personal-account identity, privacy policy, psychometric standards and multi-user data partition remain separately gated.
STOP_CONDITIONS: authentication or privacy regression, new migration/account policy need, paid infra, failed real DB check after focused repairs.
AUTHORIZATION_END: MVP-003 TEST acceptance/review, then stop. No main/PROD promotion.


## UALP-MVP-004 — RIASEC 60 source/licensing/scoring gate (2026-11-16)

CAPABILITY_ID: UALP-MVP-004
USER_RESULT: Add a second interest-assessment family to the owner-only UALP profile after correct source, adaptation and scoring gates; display six RIASEC interest scores separately from Work Values, not an averaged score.
CURRENT_WORKFLOW_MODE: ECOSYSTEM_PLANNING (source/licensing/readiness), plus bounded synthetic-only scoring preparation. Actual instrument rollout and Neon import remain BLOCKED.
RISK_CLASS: L3 — adapted licensed content + new durable catalog rows and changes to Work-Values-only runtime.
BASE_COMMIT: b7b068e0a4db92e44014c46110e7fbf474040d9c (MVP-003 USER_ACCEPTED_TEST)
OWNER_BRANCH: feature/ualp-mvp-004-riasec-source-gate
OWNER / TEST: Vahram / separate Vercel Preview and Neon Free ualp_test only after gates.
CANONICAL_SOURCE: owner-private UALP Assessment Library MASTER v0.7 / CANONICAL DB, Google Drive spreadsheet (reference, NOT runtime): https://docs.google.com/spreadsheets/d/1WDLyR3A1qwg-r8gcw28dd2hvm2F0pu9rw3ueblWc4-4/edit
SOURCE_ENTITY: ASSESS-001; ASSESSVER-000001; FORM-000001; ONET_SHORT_60_DIGITAL; 60 source-indexed form memberships; SCALE-000001..000006; RESPSET-000001; RIASEC-SUM-v1.
OFFICIAL_SOURCES: https://services.onetcenter.org/reference/mnm/ip/ip_questions ; https://www.onetcenter.org/license_tools.html ; https://www.onetcenter.org/license_toolsdev.html
SOURCE_CONTENT_STATUS: Canonical 60 indexes and 10 items per R,I,A,S,E,C exist. Only sample original English prompts are stored as text in the source spreadsheet; most English prompts are external source-resolved references. The 60 Russian translation rows ITEMTR-000061..000120 are marked CULTURAL_ADAPTATION / NOT_REVIEWED / DRAFT, so they are not approved for a public deployment.
SCORING_POLICY: Digital 60-item form has five response levels; official API transport 1..5, internal scores 0..4 (transport minus one). Exactly 10 distinct items per R/I/A/S/E/C; sum to [0,40] per scale, six independent raw scores. No reversed links, imputation, population norms, percentile, occupational matching or cross-instrument raw-score averaging. Paper 60-item form uses different binary scoring and must NOT be substituted.
VALIDATION_STATUS: Library source coverage 60/60 PASS and 10x6 balance PASS. Library RU translation coverage 60/60 DRAFT; human semantic equivalence BLOCKED; RU response options 5/5 DRAFT and human review BLOCKED; RU release gate BLOCKED / NOT_RELEASED. Evidence for English original does not validate RU adaptation.
LICENSE_POLICY: If the original English tool is genuinely copied verbatim, O*NET Tools CC BY-ND 4.0 is an available licence. Russian adaptation uses the O*NET Tools Developer License requiring source attribution, modification notice, licence link and validation study prior to modified-product release. AI-only semantic review is insufficient. Never put the item bank, responses or scoring keys in public GitHub. Do not imply USDOL/ETA endorses UALP.
CURRENT_SCOPE: source/licence provenance audit; scoring invariants; pure Python synthetic-only scorer and deterministic tests. DO NOT enable RIASEC routes/UI or write to Neon in this stage.
OUT_OF_SCOPE: releasing actual RU draft, creating user accounts, RIASEC profile interpretations, matching occupations, new paid API, PROD, unrelated modules or VBOS.
SHARED_HOTSPOTS_FUTURE: webapp/main.py hardcodes ENABLED_FORM; fetch_form requires 21 items; compute_scores requires 42 links and 27 MEAN rules; UI fixed to Work Values. These contracts require a separately reviewed form-scoped runtime adapter, not silent reuse. History/profile also have Work Values-only navigation.
SCHEMA_IMPACT_NOW: NONE. In a future authorized block, import only ADDITIVE versioned RIASEC catalog rows and keep existing Work Values IDs/statuses/relations intact.
MIGRATION_PLAN_FUTURE: Obtain exact approved item manifest with checksums, TEST backup, dry-run on disposable PostgreSQL containing existing Work Values fixture, exact guarded additive catalog install, readback 60 items, five options, 60 links, six SUM rules; verify original run/21 responses/27 scores unchanged. Rollback must disable the new form and remove only unused new catalog records by exact ID in rehearsed TEST, or restore verified backup; no destructive reset.
DEPENDENCIES: Human RU wording review; appropriate adapted-content validation; source confirmation for actual 60 prompts; accepted additive migration plan. No paid services.
ACCEPTANCE_OF_PREP_STAGE: Synthetic 60 item answers, all six scales and 10 item links each; 0/40 and mixed numerical outputs; reject malformed, incomplete, duplicate or imbalanced inputs; no actual instrument content exposed; old tests pass.
ACCEPTANCE_FUTURE: owner-only key-gated complete 60-question TEST, persisted six raw RIASEC scores independent of Work Values, history/profile compatibility, exact Neon/Vercel proof and owner phone acceptance. No unsupported high-stakes use.
ROLLBACK_NOW: Revert only these source-gate preparation commits; MVP-003 and live Neon unchanged.
UNRESOLVED_DECISIONS / BLOCKERS: (1) RU translation human review and validation not passed; (2) approved source import and migration are not yet implemented; (3) final language and internal pilot constraints require owner product decision if moving beyond source prep.
PAID_API_BUDGET: 0; EXECUTOR_PERMISSION: current assistant only.
AUTHORIZATION_END: report current source gate and stop. No PROD/main merge or unreviewed survey publication.
