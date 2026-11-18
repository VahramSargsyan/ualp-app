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


### MVP-004 continuation — Russian editorial v0.2 and CI full HTTP adapter

DATE: 2026-11-16
MODE: IMPLEMENT_FEATURE for dormant adapter/CI only; editorial preparation is not an independent bilingual approval.
CURRENT_HEAD_AT_START: a4c806251a46c66a89d44cd97ef07884d7ef1ed5
CONTENT_OUTPUT: Private owner-only Google review Sheet ID 1kwbz7MymuOrJZwo0FUn8AcMSqxePFUKdJyFwGFg2Jwc, tab Вопросы 60 columns O:Q. 60/60 editor draft proposed wordings; nine suggested edits, one additional explanatory note. Response tab Варианты 5 columns J:L has one midpoint wording proposal. All canonical statuses DRAFT/NOT_REVIEWED, reviewers PENDING, canonical library remains unchanged.
TECHNICAL_OUTPUT: Full HTTP GET form and POST 60-item SUM scoring with PostgreSQL persistence, idempotent retries, conflict detection, concurrent duplicate recovery, history/profile coexistence, readable six scores and fail-closed rubric checks. This is NOT enabled for original content or user-entered RIASEC.
CRITICAL_EXPOSURE_FENCE: The only second form key supported by code is CI_RIASEC_60_SYNTHETIC, and even this is rejected unless UALP_ENV=TEST, UALP_CI_MODE=EPHEMERAL_POSTGRES, UALP_CI_RIASEC_INTEGRATION=1, and the active PostgreSQL connection is localhost/127.0.0.1 with database ualp_ci and user postgres. Production/Neon/Vercel clients cannot opt into it by setting a key or request parameter. Work Values ENABLED_FORM unchanged.
REAL_TEST_LEVEL: GitHub Actions workflow ualp-real-pg-ci.yml with temporary localhost postgres:18 and fabricated form/question/answer IDs only; test_08 passes 60-answer HTTP lifecycle, SQL score recomputation, authorization/disabled form, retries, conflict and simultaneous POSTs. No actual user data, source translations or copyrighted original questions in public repo.
SCHEMA_IMPACT: NONE at this preparation stage; no Neon writes/migrations.
BACKUP / ROLLBACK: No live DB change or backup required. Revert only the CI adapter/verification commits and discard independent private editorial proposal Sheet if needed; previous v0.3 TEST and canonical UALP v0.7 remain.
OPEN_BLOCKER: Developer License validation for the modified RU content is NOT completed; independent bilingual semantic review and intended-purpose evaluation are NOT_RUN. No release of RU content, no authenticated user-facing RIASEC questionnaire and no main/PROD promotion.


### MVP-004 private personal TEST preparation / exact source-lock gate (2026-11-16)

MODE: IMPLEMENT_FEATURE (bounded preflight only); SOURCE_AUDIT read-only.
BASE_COMMIT: 86bd6d7d2d8bf67f885aad278d11065f71ae3481 (PR #6 draft).
OWNER / TEST: single owner; existing UALP Vercel Preview + isolated Neon ualp_test, but no new actual form deployment in this block.
PURPOSE: Prepare exact-content private RU RIASEC catalog source-lock before any durable catalog migration or runtime activation; preserve accepted MVP-003 Work Values.
RIGHTS_SCOPE: The O*NET Tools Developer License defines "Share" in section 1(9) as providing to the public. Section 3(b) validation obligations are prefaced "If You Share Adapted Material You produce." A strictly private owner-only local research copy is meaningfully different from public release; do NOT treat this as blanket legal advice or authorization to publish adaptations. Original O*NET attribution, modification notice, no-endorsement, and any future release conditions remain. Official URLs: https://www.onetcenter.org/license_toolsdev.html ; https://www.onetcenter.org/license_tools.html .
SOURCE_EVIDENCE: read-only Google Sheets exact canonical ASSESS-001/FORM-000001: 60 unique source-indexed item IDs, 60 ru DRAFT/NOT_REVIEWED translations; 60 one-to-one positive-weight links, six 10-item SUM rules, five ru draft response labels. Private editorial v0.2: 60/60 IDs aligned and full draft, 9 proposed changes; none independently approved.
CHANGE: Add webapp/riasec_manifest.py read-only JSON preflight and tests/test_riasec_manifest.py with synthetic content only. Strict required fields, 60 ordered unique item identities, 10 each R/I/A/S/E/C, exactly five 0..4 options and six canonical areas, source/algorithm/status/purpose/private-scope and licence checks, SHA256 over canonical UTF-8 JSON and optional expected digest. Duplicate JSON keys rejected. CLI outputs receipt counts/digest only; no private prompts or DB calls. Nothing is made available to respondents by this code.
PRIVATE_MANIFEST_FUTURE: In later separately approved step, derive a private JSON manifest from canonical and editor source in protected local/Drive/Neon staging (never public GitHub). Use exact schema in new preflight module; lock its checksum on source readback, then generate additive catalog install with stable private source IDs. This block does not itself produce or import that private JSON manifest.
NEON_MIGRATION_PLAN_FUTURE: Before writes, capture exact source commit, immutable private SHA256 and pre-write catalog/run/responses/scores counts; create verifiable TEST backup/recovery point; rehearse additive 60-item/5-option/6-scale/60-link/6-rule install on disposable PG with existing Work Values fixtures; fail closed on any duplicate IDs or source SHA mismatch; verify current 1 run/21 responses/27 scores are byte-for-byte unchanged and all new rows match; rollback by disabling only new form and removing only never-used new catalog IDs after rehearsal, otherwise restore verified backup. No schema rewrite or destructive reset.
CHECKS: GitHub automated pure preflight tests + existing full Python/JS/real PG suites. Neon owner actual data read-only postflight. No RIASEC translation release/personal human testing in this block.
NOT_RUN: independent bilingual review, scientific validation, actual private source import, Neon migration, real-owner 60-question web flow, TEST URL user acceptance, PROD.
RISK: L3 content/version lock for any later import. No new API cost, account, executor, or PROD permission. Do not present draft RU scores as validated diagnostics or use for hiring.
ROLLBACK: revert only this branch's preflight/test/packet commits to base commit; no live app or database changes to undo.
AUTHORIZATION_END: preflight code, automated tests, read-only source and Neon verification, PR receipt, STOP. Subsequent actual content import / private run is a new bounded migration + release block with explicit gate checks and rollback.


### MVP-004 owner-private source lock and guarded Neon rehearsal checkpoint

DATE: 2026-11-16
MODE: IMPLEMENT_FEATURE (guarded private catalog preparation/rehearsal). Owner-only Russian TEST; no public/PROD release or additional executor.
SOURCE_HEAD: 5df9be8f1b0c24d6b6c542b0474279692740ee31
PRIVATE_MANIFEST: Frozen owner-private draft v0.2 in a separate, owner-only Google Drive file, no item texts/response labels committed to GitHub. Canonical SHA256 over UTF-8 JSON with alphabetically sorted keys: 9d54adb24827f3902ba91858e711e92d343488b1863d22a695847dbdd47197be.
SOURCE_MEMBERSHIP: Original canonical FORM-000001 / 60 source-indexed stable ITEM IDs, 10 per R/I/A/S/E/C, 6 SUM scales/rules, five 0..4 options; 9 proposed RU editorial wording changes. Mark all adapted questions/answer labels DRAFT_NOT_REVIEWED, owner-only experimental. No independent bilingual/psychometric approval.
PREWRITE_SAFETY: Read-only Neon ualp_test before migration: 1 form, 21 items, 5 options, 27 scales, 42 links, 27 rules, 1 run, 21 responses, 27 scores. Actual RIASEC IDs and Work Values IDs are distinct. Neon Free pre-RIASEC copy-on-write backup branch is READY, with parent LSN recorded privately; backup has no compute. Separate isolated disposable rehearsal branch has exactly the same baseline data. No PROD or VBOS project involved.
REHEARSAL: TWO attempted fully transactional additive catalog installs on the separate rehearsal Neon branch, both ROLLED BACK, with verified no form/items added, old data unchanged and parent branch not mutated.
BLOCKER 1: SQL syntax error caused by use of "FROM source, CROSS JOIN LATERAL"; repaired to "FROM source CROSS JOIN LATERAL".
BLOCKER 2: overly broad scale-ID collision probe LIKE 'SCALE-00000_' matches three legitimate Work Values IDs ending 000007, 000008, 000009. Precise remedy for a later controlled attempt is strict equality against intended six source IDs SCALE-000001 through SCALE-000006, plus exact item/form ID collision checks. Never relax checks broadly or delete old IDs.
REPAIR_CYCLES: Two evidence-producing cycles exhausted for this bounded block; STOP before any third write attempt. Fix should be tested against the exact existing baseline on the separate rehearsal branch in a new authorized block, then verify all rows and original owner data before considering the main TEST import.
NONDESTRUCTIVE_READBACK: Rehearsal and main both remain: forms 1/items 21/options 5/scales 27/links 42/rules 27/runs 1/responses 21/scores 27. Pre-RIASEC backup branch READY.
MIGRATION_NOT_RUN_ON_MAIN: No RIASEC content imported into working main Neon, no form route activated, no new TEST URL or human RIASEC completion.
TESTS: The existing synthetic-only source-lock/HTTP/real-PostgreSQL CI suite previously PASS at source HEAD; actual private-manifest CLI against native JSON and real source migration PASS are NOT_RUN. Do not equate failed transactional rehearsals with accepted migration.
REMAINING_DEPENDENCIES: Narrow SQL collision check, new isolated rehearsal PASS + row-by-row readback, verification of private manifest hash, safe additive main TEST import with backup and rollback, runtime adaptation with owner-key auth and visible attribution/experimental warning, exact Vercel Preview deploy, owner-phone acceptance.
ROLLBACK: No main database rollback required because no write occurred. Keep the original Neon's backup branch available until the next gated import is accepted. No public manifest content should be added to repository.
AUTHORIZATION_END: Report partial checkpoint and stop the blocked migration block under two-cycle repair limit.


### MVP-004 private RIASEC — guarded TEST catalog + owner Preview candidate (2026-11-16)

CAPABILITY_ID: UALP-MVP-004 / OWNER_RU_PRIVATE_TEST
WORKFLOW_MODE: IMPLEMENT_FEATURE (one scoped catalog migration / owner-only UI & API)
RISK: L3 for adapted content and durable catalog, never a scientific validation claim.
BASE_COMMIT: fe76ec3f8d02a5821e0034da3d0ebdfe710f67c0
SOURCE_BUILD_BRANCH: feature/ualp-mvp-004-riasec-source-gate (Draft PR #6; no main merge).
OWNER_TEST: existing Neon Free ualp_test, original Vercel Hobby Preview, existing owner access key, no new infrastructure costs.
SOURCE_LOCK: The exact private source v0.2 is SHA-256 9d54adb24827f3902ba91858e711e92d343488b1863d22a695847dbdd47197be. 60 Russian items, five scored responses, six R/I/A/S/E/C dimensions, 10 each; content remains owner-private, never committed to GitHub. Human translation/psychometric validation NOT_RUN, DRAFT / NOT_REVIEWED.
GUARD: Source input SHA-256, exact stable form/item/scale IDs, six specific scale IDs (avoid broad legacy matching), 60/5/6 data checks and exact baseline counts. Atomic Postgres DO statement aborts all changes on any mismatch. No schema changes or user data rewrites.
PREINSTALL: Copy-on-write Neon branch named ualp-mvp004-pre-riasec-backup-20261116 ready, from accepted main TEST parent LSN; untouched and preserved.
REHEARSAL: Reused ualp-mvp004-riasec-rehearsal-20261116 PostgreSQL branch, verified exact baseline 1 form/21 items/5 options/27 scales/42 links/27 rules/1 user run/21 answers/27 scores. New atomic additive catalog install PASS. Source item text 60/60, option labels/values 5/5, scale descriptions 6/6 and six SUM rules matched private source by exact readback.
TEST_MIGRATION: The exact guarded additive statement applied to primary Neon TEST, readback PASS; current catalog totals 2 forms, 81 items, 10 options, 33 scales, 102 links and 33 rules; user data unchanged at 1 run/21 answers/27 scores. Main and rehearsal new catalog readbacks identical. Nine protected Work Values table-content fingerprints match between main and rehearsal.
SCHEMA_IMPACT: NONE; additive catalog rows only. No PROD, VBOS, ЖЭК or other PostgreSQL project touched.
ROLLBACK_EVIDENCE: Synthetic-only unused 60-item catalog add/remove on ephemeral PG18 CI passed using strict exact IDs, zero user runs and FK order; original Work Values rows and runs remained unchanged. Neon no-compute backup held. ACTUAL destructive TEST rollback NOT_RUN, since new TEST catalog import passed. Never restore backup over newer user responses without separate protected reconciliation; never delete catalog once referenced by runs.
OWNER_ONLY_RUNTIME: FastAPI is TEST-only, protected by original X-UALP-Access-Key and exact Neon TEST database/hostname. Real RIASEC form enabled only for key ONET_SHORT_60_DIGITAL, exact FORM-000001 and RU-v0.2-editorial-DRAFT-20261116; before GET/POST the server reconstructs and compares the 60-item/5-option/6-scale private SHA-256 source-lock, rejects drift. CI synthetic form retains localhost-only fence. UI shows separate 60-item questionnaire, O*NET attribution and developer-license link, six raw 0–40 interest sums, profile preserved independently of Work Values. No public self-service account, professional interpretations, IQ norms or occupational matching.
TEST_RESULTS: GitHub unit/JS checks 58 PASS, 10 intentionally skipped (real-PostgreSQL tests run separately); ephemeral real PostgreSQL 18/FastAPI suite 10 PASS. Exact commit Vercel GitHub status SUCCESS/Ready for owner Preview; real signed-in phone flow NOT_RUN.
ACCEPTANCE_URL: https://ualp-app-git-feature-ualp-mvp-004-riasec-553356-vahram-sargsyan.vercel.app
HUMAN_ACCEPTANCE: Owner opens Preview under existing authentication, enters prior private TEST access key without sharing, checks Work Values screen/history, selects RIASEC 60, reviews O*NET source notice, answers each, sees six raw 0–40 results, returns to profile and confirms Work Values prior result remains. Owner acceptance pending; real live RIASEC respondent run has NOT_RUN until owner explicitly tests. Do not claim owner acceptance based on CI/build status.
LICENSE_STATUS: O*NET Tools Developer License permits adaptations subject to license restrictions. Owner-only pilot with protected access is not professional/public validation. Retain source/changes notice; do not publish instrument for mass use before applicable validation and licensing checks.
MIGRATION_ROLLBACK: If owner Preview fails, revert only feature-branch runtime to prior accepted Work Values version and disable actual RIASEC route. Do not delete source IDs and do not reset Work Values. Catalog remains DRAFT/inactive; if zero RIASEC runs, exact-ID catalog removal only with a separately approved and rehearsed guarded plan. Keep Neon backup until user acceptance.
NOT_RUN: External reviewer approval, psychometric validation, runtime auth on actual remote Preview via tool, full mobile walkthrough and owner acceptance, PROD. No app-level manual runtime claim, no main merge.
FILES_TO_COPY: none. PR branch and connected app integration only.
AUTHORIZATION_END: After exact CI and Preview build verification, present owner TEST URL for mobile acceptance; do not promote to main/PROD automatically.


### MVP-005 — remember owner sign-in (2026-11-16)

CAPABILITY_ID: UALP-MVP-005 / OWNER_DEVICE_SESSION
USER_RESULT: enter the existing private key once, optionally remember this browser for 30 days; keep sign-in on home/result navigation; explicit logout.
MODE: IMPLEMENT_FEATURE. RISK: L3 authentication boundary.
BASE_COMMIT: a45439abe1d0e4390547298d25480525f35e703b on feature/ualp-mvp-004-riasec-source-gate / PR #6. Same private Preview lane, no main merge or PROD.
OWNER_ACCEPTANCE_EVIDENCE: Owner supplied phone result and reopened-profile screenshots, confirming RIASEC scores reload and both RIASEC and existing Work Values appear. This is owner-observed mobile acceptance of those flows, not scientific validation or an assistant database audit.
AUTHORIZATION: Owner explicitly requests avoiding repeated 32+ character key entry and remembered app access. Current assistant only, budget 0. No new account provider, multi-user rollout, APK, paid infrastructure or source content changes.
IMPLEMENTATION: Dedicated login endpoint exchanges existing key for host-bound HMAC-SHA256 signed session (random nonce, expiry; no raw access key in cookie). Secure / HttpOnly / SameSite=Strict / __Host- cookie. Remember checkbox adds 30-day Max-Age; unchecked uses browser-session cookie, also with a 30-day cryptographic upper bound. Key rotation invalidates all sessions. No localStorage/sessionStorage credential persistence. Same-origin custom-header + Origin/Fetch-Metadata checks for cookie mutations. Existing explicit-header clients/CI still work. Logout clears this browser cookie; no per-device server-side revocation registry, so an independently stolen token is valid until expiry/key rotation.
SCOPE: webapp/main.py, webapp/owner_session.py, webapp/index.html, focused auth/SQL/UI tests, this packet and current-state documentation.
DATA / MIGRATION: No DB writes for login/logout, no schema migration, no change to IDs, scores, catalog or saved answers. No Neon credentials or real private key needed during development.
ACCEPTANCE: valid key -> secure cookie -> new page/browser context -> profile and tests without key -> logout -> unauthorized. Bad key, malformed/expired/tampered/other-host cookie and cross-origin writes rejected. Existing 21/60-item scoring/save/retry regressions maintained.
LOCAL_CHECKS: Python full suite 67 PASS / 11 intentionally skipped real-PostgreSQL tests; compileall and JavaScript syntax PASS. Browser and exact-commit CI/Preview checks recorded in PR delivery receipt.
BROWSER_TEST: tests/verify_owner_session_ui.cjs expects Playwright and local HTTPS uvicorn on 127.0.0.1:8843 with synthetic key, using mocked catalog/results. Its browser cookie/login/logout are actual backend HTTP, but it does not prove Neon persistence. Use CHROMIUM_PATH where needed.
ROLLBACK: Revert this scoped feature commit to baseline runtime, removing cookie authorization and login UI. Existing saved results remain untouched. Old cookies become unused; key rotation invalidates them if required. No DB restore.
RESIDUAL_LIMITS: Stable Preview hostname required; a different deployment hostname/browser has a separate cookie. Vercel protection is independent. Refreshing an unfinished questionnaire still loses unfinished answers; draft resume is out of scope. Scientific validation remains NOT_RUN.
AUTHORIZATION_END: verified private Preview candidate and owner instructions; no automatic next capability/main/PROD promotion.


### MVP-006 — consent-based private draft resume (2026-11-16)

CAPABILITY_ID: UALP-MVP-006 / PRIVATE_DRAFT_RESUME
USER_RESULT: After explicitly choosing browser-local draft saving, the single owner can answer part of Work Values or the 60-item RIASEC, reload/close/reopen the same browser+Preview hostname, authenticate, and resume from the saved item index with earlier option choices intact; a successful save or logout removes the relevant local draft(s).
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 UX plus local handling of sensitive responses (privacy-sensitive, no canonical mutation).
BASE_COMMIT: ae1fe11b383a1904956a577c34bdf6b6d7c12225 (MVP-005 0.4.1 unmerged draft candidate).
OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test, based on original PR #6 feature branch. PR #6 remains the predecessor; do not merge either into main/PROD without separate acceptance.
OWNER / TEST_TARGET: Vahram, synthetic local HTTPS Chromium + ephemeral PostgreSQL CI + isolated Vercel Hobby Preview only, no new infrastructure or cost.
CANONICAL: Existing Neon TEST PostgreSQL catalog, run, response and score tables are the only authoritative source for *submitted* answers. Browser localStorage is only an opt-in provisional incomplete draft; never treat it as a completed run or a backend truth.
SCOPE: webapp/index.html state/UX, backend visible version, existing JS browser CI and documentation. Opt-in checkbox separate from consent to server submission; two independent form-key draft slots (Work Values / RIASEC), selected option keys + ordered item IDs + exact formVersion + current index + original requestId + savedAt/expiry, no question texts or access key. Resume requires current authenticated owner session and renewed server submission consent; refetch form, validate exact version/item order/allowed options before trusting a draft. Save after each answer and navigation. Resume/discard controls appear only after login. Per-form draft erased only after successful server ACK; logout erases both. User can pause to home. Failed storage shows explicit warning; never falsely claim persisted. Retrying a failed submission reuses original requestId for idempotency.
DATA_PRIVACY: Browser localStorage values are unencrypted and may survive window closure. Never opt in by default. Do not use on shared devices. Same-origin/hostname separation; malicious scripts/extensions, physical browser access and cross-tab writes are residual risks. Expired records are removed lazily when accessed after seven days; browser clearing, private browsing and quota can remove them earlier. Cookies/credentials are not stored in draft records. User may discard each draft or logout to remove both.
OUT_OF_SCOPE: server-side draft records/accounts, syncing across devices/hostnames, offline guaranteed queues, encryption/key management, migrating records into Neon, catalog/version changes, item texts, psychometric interpretation, new paid APIs, main merge, PROD.
SHARED_HOTSPOTS: webapp/index.html, webapp/main.py for visible version, .github/workflows/ualp-postgres-ci.yml, tests/verify_draft_resume_ui.cjs. Existing real-Postgres save path, auth HMAC cookie and O*NET source SHA-lock untouched.
SCHEMA_IMPACT: NO PostgreSQL schema change; browser-local new key prefix ualp-owner-draft-v1: scoped by formKey. No database migration, no ID/relations/status change. Local drafts are disposable and version-fenced.
MIGRATION_PLAN: NONE for Neon. Local browser data has its own schema=1 and expiry; absent/incompatible/invalid or changed form returns no resume and is removed. Do not silently reinterpret old answers.
ACCEPTANCE: Opt-in OFF => no localStorage write. Opt-in ON => 60-item partial answers survive reload with restored radio choices/index and requestId. Work Values and RIASEC drafts independent. Resume requires consent and authentication, stale/incompatible inputs invalidated, same-form restart warns. Correct 60-answer submission clears only RIASEC draft after ACK, leaves Work Values draft; logout clears both. Real saved results/profile remain unchanged.
REQUIRED_EVIDENCE: inline JS syntax, existing full Python tests, synthetic local HTTPS Chromium interaction incl 21/60, ephemeral PostgreSQL integration, exact Vercel Preview source status and owner phone reload/resume acceptance. A browser-mocked API check is not real Neon persistence.
ROLLBACK: Revert only MVP-006 branch or return to prior PR #6 Preview exact commit; no Neon backup/restore needed. For privacy after rollback, delete abandoned local drafts in the newer UI before reverting, or clear site storage manually on affected device. Existing 21/60 submitted runs are untouched.
EXECUTOR_PERMISSION: current assistant only. PAID_API_BUDGET: 0. REPAIR_LIMIT: up to two focused cycles if CI reveals defects.
STOP_CONDITIONS: unexpected authorization bypass or privacy leak, missing required CI/Preview access, changed server catalog schema/IDs, owner business change, more than two focused repair cycles.
UNRESOLVED_DECISIONS: NONE for owner-only opt-in TEST. Cross-device sync and validated public use remain outside this block.
AUTHORIZATION_END: verified draft-only TEST candidate with exact receipt for owner acceptance, no automatic next module/main/PROD promotion.


### MVP-005.1 — owner remembered-login UX unblock on MVP-006 TEST lane (2026-11-16)

CAPABILITY_ID: UALP-MVP-005.1 / DEFAULT_PERSISTENT_OWNER_SESSION
WORKFLOW_MODE: PATCH_FIX. USER_RESULT: owner signs into the private app one final time on a stable Chrome TEST hostname and does not need to enter a lengthy owner key at every reopen for 30 days.
OWNER_REPORT: The owner explicitly reports repeated login-key entry despite MVP-005 existing. Prior mobile acceptance of saved RIASEC/profile did not establish acceptance of 30-day login.
ROOT_CAUSE_FROM_SOURCE: The existing persistent 30-day cookie requires selecting an unchecked \`remember\` checkbox; otherwise the browser receives only a session cookie. Every new Vercel branch Preview hostname also has independent host-bound cookies, and opening links from different webviews/browser contexts can partition cookie storage. We have not confirmed which of these conditions happened on the owner's phone; no hosted browser/runtime telemetry is available.
BASE_COMMIT: b31d2328b20d1d668a6e0d616b916a8418655883 (UALP MVP-006 Draft PR #7); parent PR #6 remains unchanged. OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test. Fixed TEST entry hostname: https://ualp-app-git-feature-ualp-mvp-006-draft-6b4814-vahram-sargsyan.vercel.app. Future acceptance links should continue using this exact branch hostname until another owner-approved release boundary.
SCOPE: Make 30-day remember checked by default for owner-only TEST; explain that storage is per browser and exact hostname, that Chrome home-screen shortcut avoids ChatGPT in-app temporary windows, and that shared devices must uncheck. Preserve opt-out browser-session cookie, existing 30-day HMAC expiry, Secure/HttpOnly/SameSite=Strict/host-only cookie, zero credentials in localStorage, key rotation/logout, session API. Allow browser-password-manager autocomplete (never force or store key).
FILES: webapp/index.html, tests/verify_owner_session_ui.cjs, this Build Packet, PR receipt.
OUT_OF_SCOPE: Neon/DB/auth key changes; server-side long-lived session registry; linking identities/cookies across different .vercel.app hosts; bypassing Vercel protection; converting Preview into PROD; new infrastructure, expense, paid API, extra executors. Vercel API connector cannot enumerate the Git-linked UALP project under the authorized account (404), so no custom alias is assigned. Cross-host persistent login requires separately approved identity/domain work.
SCHEMA / MIGRATION: NONE. Existing TEST data/results, form/question IDs, profile, cookie signing and draft localStorage schema unchanged.
RISK: L2 auth UX; 30-day persist is now the private-device default as explicitly requested. Sensitive device access risk disclosed; opt-out remains.
ACCEPTANCE: A fresh browser starts with remember checked, POST session includes remember=true, server confirms remembered=true, Secure HttpOnly SameSite=Strict cookie has ~30 day Max-Age and survives a browser-context restart on the same hostname, profile works, logout invalidates cookie. If user unchecks, cookie is session-only. Host mismatch and key rotation still fail closed. Owner manually opens exact branch Preview directly in Chrome once, signs in, closes/reopens using Chrome bookmark/home-screen shortcut, confirms profile opens without key. If the phone still loses auth on the same origin/browser, diagnose cookie/site-data policies; do not claim fixed without owner's test.
TEST_LEVEL: synthetic local HTTPS Chromium + existing Python/ephemeral PostgreSQL CI + Vercel build status; actual private authenticated Vercel mobile owner flow pending. Earlier tests did not cover the default remember checkbox.
ROLLBACK: revert scoped owner sign-in UX commit; no DB migration/restore. Existing saved test answers remain.
PAID_API_BUDGET: 0; EXECUTOR: current assistant only; REPAIR_LIMIT: up to two focused cycles; AUTHORIZATION_END: exact TEST candidate, receipt and owner acceptance; no main/PROD merge.


### MVP-005.2 — distinguish rejected login from failed cookie readback (owner screenshot 2026-11-16)

CAPABILITY_ID: UALP-MVP-005.2 / SESSION_LOGIN_FAILURE_FEEDBACK
MODE: PATCH_FIX, risk L2 authentication usability. BASE_COMMIT: dace0323dff6970a2848b8d1cef1963061568e39; branch feature/ualp-mvp-006-draft-resume-test (draft PR #7, no main or PROD).
USER_OBSERVED: Owner's phone screenshot shows a red message "Вход не выполнен или истёк. Введи ключ доступа ещё раз. Если авторизация исчезает ..." and disabled authenticated navigation. That wording occurs in the login click exception, and a 401 can arise either at the POST session-key check or at the post-login GET session-cookie check. The screenshot does not prove which operation failed; a host-/browser-specific cookie failure remains HYPOTHESIS, not CONFIRMED.
SOURCE_DEFECT: UI cleared the long input key before verifying the issued cookie by GET /api/session. A rejected GET forced unnecessary retyping. The generic auth error obscured login-request failure vs readback failure.
PATCH_BOUNDARY: Retain key in transient password input until the GET cookie readback succeeds; no persistence in localStorage, sessionStorage, cookies, source or logs. Display separate code SESSION_COOKIE_CHECK_FAILED when login POST succeeds but cookie GET fails, and LOGIN_REQUEST_FAILED when POST or remember confirmation fails; no misleading implication that the key was wrong. Preserve "signed in" only after GET 200. Existing secure signed 30-day HttpOnly cookie, server auth/security, no new credentials or bypass remain unchanged.
TEST: Synthetic local HTTPS Chromium injects rejected key and a 401 cookie readback after server-issued cookie, checks distinct messages, retained transient input, unauthenticated UI, then removes injection, retries login and verifies original full 30-day lifecycle. Full Python/JS/Chromium suite and isolated ephemeral PG CI run after source commit.
CANONICAL_DATA / MIGRATION: No DB/schema, test results, catalog, form IDs or source-content changes. Does not claim to fix the underlying actual Vercel 401 without observed status details. No PROD.
ROLLBACK: Revert two scoped UI/test commits to earlier stable candidate; no DB restore. Owner acceptance: exact branch Preview on same Chrome hostname, note whether error code is LOGIN_REQUEST_FAILED or SESSION_COOKIE_CHECK_FAILED, never share the actual key.
AUTHORIZATION_END: bounded diagnostic PATCH and TEST verification only; if live 401 remains, stop and request the one non-secret error-code screenshot rather than weakening authentication.


### MVP-007 — unified history for Work Values + RIASEC (2026-11-16)

CAPABILITY_ID: UALP-MVP-007 / UNIFIED_ASSESSMENT_HISTORY
USER_RESULT: The owner can open "История тестов", view the previously completed Work Values and RIASEC runs together, filter by method, page through older completions and reopen exact stored results without retaking a test.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 owner-only private read API and mobile UI.
OWNER_AUTHORIZATION: "Лучше продолжи разработку" — one bounded existing-app extension. Do not infer that unfinished questionnaire draft-resume MVP-006 is accepted. Existing login MVP-005.2 is owner accepted; keep its same stable Chrome hostname.
BASE_COMMIT: fd26c611156f4a42e4617a1358d056c2480ef993 (PR #7). OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test, same TEST Preview host; PR #7 remains DRAFT, dependent on PR #6. Do not create a new Preview hostname and make owner re-enter key, or merge main/PROD.
CANONICAL: Existing Neon TEST PostgreSQL ualp_assessment_runs, catalog forms and stored server scores. Read-only; earlier results are NOT rescaled or reinterpreted.
SCOPE: Existing GET /api/history expands with allowlisted query \`formKey=ALL|UALP_WV21_RU_LIKERT|ONET_SHORT_60_DIGITAL\`, preserving historical Work Values default when query absent. Query uses form_key=ANY(array of exact known keys), existing completed status fence, timestamp/run ID keyset cursor, limit 10+1, and returns formKey alongside existing metadata for each entry; no raw answer/option/score content is leaked in history response. Mobile history filter defaults ALL and names each method; old "История Work Values" buttons become "История тестов"; opens exact stored /api/runs result. Server-side scores, profile and results remain unchanged. Synthetic CI browser exercises both filters and back navigation.
OUT_OF_SCOPE: occupational recommendations, validated interpretation, ICAR-16 catalog/answers, multi-user permissions, account export, deletes, changed translations/score rules, new Neon migrations, PROD, new paid API or executor. Never publish private form text.
HOTSPOTS: webapp/main.py (history-only GET + version), webapp/index.html (mobile history), tests/test_real_postgres_integration.py (existing isolated CI), tests/verify_owner_session_ui.cjs (synthetic browser), governance and this packet.
SCHEMA_IMPACT / MIGRATION: NONE; API addition includes optional query param and response formKey. Default response remains Work Values-only for existing clients. No mutations or recalculation of persisted runs. No DB backup/restore.
ACCEPTANCE: Unauthenticated GET -> 401. Unknown method filter -> 422. Default GET -> only completed Work Values runs. ALL -> exactly both approved form keys, not unrelated synthetic catalog, deterministic 10-row paginated combined history. RIASEC -> only its historical runs. Test switching filters resets cursor and list, opens previously saved RIASEC stored result. No raw responses, secret fields or scoring keys in list. Full existing auth, save/retry, draft-resume and profile regressions preserved.
REQUIRED_EVIDENCE: Python/JS CI, isolated real PostgreSQL integration (approved keyspace and full pages, zero DB writes), synthetic local HTTPS Chromium browser, exact Vercel Preview build and owner phone smoke-test. Hosted authenticated E2E is separate and NOT_RUN without access; no claims of owner acceptance before owner check.
ROLLBACK: revert scoped MVP-007 commits to exact MVP-005.2 head \`fd26c611156f4a42e4617a1358d056c2480ef993\` on this private branch; all saved PostgreSQL scores, RIASEC and Work Values runs preserved. No files to install manually.
EXECUTOR_PERMISSION: current assistant only. PAID_API_BUDGET: 0. REPAIR_LIMIT: 2 focused cycles. STOP_CONDITIONS: failed auth data isolation, unexpected schema, any mutable catalog or PROD dependency, unresolvable CI failure, changed owner requirements.
UNRESOLVED_DECISIONS: NONE; existing owner-only TEST semantics apply.
AUTHORIZATION_END: exact CI-verified dependent TEST candidate, receipt, user acceptance instructions, STOP; no automatic next capability or PROD.


### MVP-008 — downloadable owner-only Android TEST wrapper (2026-11-17)

CAPABILITY_ID: UALP-MVP-008 / ANDROID_TEST_APK
USER_RESULT: The owner installs a TEST Android app instead of navigating ChatGPT/Chrome tabs. It always opens the same private UALP Vercel Preview origin, allows sign-in once inside the app, persists the browser-cookie session across screen transitions and Android process restarts within the 30-day server cap, and maintains the existing assessment experience.
WORKFLOW_MODE: IMPLEMENT_FEATURE with bounded installed-client UX repair; RISK: L3 owner-auth cookies in a new Android WebView container.
OWNER_REQUEST: "Сделай так чтобы я скачал этот апп и этого проблемы не были". Work on installed TEST packaging; no separate backend rewrite or PROD permission. Current assistant; existing free GitHub Actions Android build infrastructure permitted; paid API budget 0.
BASE_COMMIT: 7fc719003d83d65b42291b1cabb2661bbf375486 on feature/ualp-mvp-006-draft-resume-test / draft PR #7. No main merge.
CANONICAL: Existing private FastAPI+Neon TEST; no embedded respondents, secret, key or question text in Android sources or APK. UALP app continues to require network reachability and the existing owner access-key gate.
SCOPE: New android/ Gradle project and one temporary owner-only GitHub Actions debug-APK build+artifact workflow; fixed first-party origin is https://ualp-app-git-feature-ualp-mvp-006-draft-6b4814-vahram-sargsyan.vercel.app/; stable Android package ID am.ualp.privatepilot. No new backend/user/identity model. Restrict top-level WebView to exact https hostname; external HTTPS to browser, all other schemes denied. JavaScript and DOM storage enabled for current UALP, file/content/mixed-content/new-window access disabled; no JS bridge, no exported data API, Android allowBackup=false, Secure/HttpOnly cookies handled by WebView CookieManager with flush on pause/load. Back minimizes app on root; preserves cookie jar and in-page navigation. Debug APK used only as private single-owner TEST package.
OUT_OF_SCOPE: Independent offline data store, automatic password bypass, client-side password storage, multi-user login, public Play Store, permanent debug APK signing key, apps for iOS, new server/database environment, tests of psychometric validity.
SIGNING / UPDATES: CI assembles a debug-signed APK with a runner-local ephemeral key. A later APK build with a different signing cert may need uninstall/reinstall, losing local cookie/drafts; do not claim in-place Android native upgrades without an owner-approved protected stable signing-key process. Web UI changes on the same Vercel hostname do not require installing a new native APK.
CANONICAL_DATA / MIGRATION: ZERO schema changes. No new Neon reads/writes/migrations, same source-locked catalog, server sessions and 30-day signed host cookie; do not directly edit PROD.
ACCEPTANCE: Build android/app/build/outputs/apk/debug/app-debug.apk with declared Android build tools; verify APK ZIP CRC, package metadata and Android debug signature. Existing Python/JS+ephemeral PostgreSQL owner TEST CI must continue passing. On Android phone install APK, enter key once in this installed app (Chrome cookies cannot be imported); open profile -> "На главную" -> history -> "На главную", background/reopen app and verify profile without key. The Android OS/Chrome-internal URL must never change app host; explicit user Logout or 30-day expiry must still require sign-in.
NOT_RUN: Emulator/device execution until actual Android device available; build-only evidence cannot prove persistent cookies on real phone. If Android SDK build is unavailable, report exact blocker rather than distributing an unverified "APK".
ROLLBACK: Uninstall only UALP TEST APK; original Chrome bookmark, Neon/PostgreSQL data and Vercel Preview unchanged. No database restore. Do not delete owner records.
STOP_CONDITIONS: Any credential leak, insecure WebView navigation, unexpected paid service, Android compile failure beyond two evidence-based repairs, missing artifact access, cross-project changes. AUTHORIZATION_END: verified installable TEST artifact and owner instructions; no PROD/Play Store.


### MVP-008.1 — one-time preferences / Home navigation UX PATCH (2026-11-17)

CAPABILITY_ID: UALP-MVP-008.1 / HOME_NO_REPEATED_CONSENT
WORKFLOW_MODE: PATCH_FIX (owner-provided screenshot reproducing repeated onboarding), RISK_CLASS: L2 local privacy/consent UI.
USER_RESULT: Once owner confirms the TEST answer-storage consent and explicitly chooses whether incomplete answers can be stored on this device, "На главную", history/profile navigation and same-browser reload return to a compact authenticated dashboard without showing consent checkboxes again. The owner can modify choices in "Изменить настройки"; explicit Logout removes both local preferences and unfinished drafts.
ROOT_CAUSE: Previous webapp/index.html home() always ran el('consent').checked=false and exposed the welcome configuration on every navigation; the draft opt-in remained checked but the primary consent was cleared. This was a UI reset, not session expiry.
BASE_COMMIT: f71e28c069d056dd903c5f58535741e84d74c188; OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test / draft PR #7; stable Vercel owner TEST hostname retained (same Android wrapper).
CANONICAL: Existing Neon TEST runs/scores and server consent=true per submitted run; no schema, secret, cookie, server auth or canonical run mutation. Browser-local preferences key ualp-owner-settings-v1 stores only schema, consent=true, optional draftOptIn bool and fixed consent-policy version; **never** store access key, saved response choices, prompt text or score in the preferences record. Unfinished response drafts remain in independent existing localStorage slots and are removed at logout.
SCOPE: webapp/index.html, visible app version only, focused Chromium regression for home/reload/logout and draft resume, build packet and execution gate. Explicit one-time Save button requires affirmative TEST consent before tests are enabled. Save with draftOptIn off means **no** browser-draft persistence. Consent from a changed policy version is invalidated on next load; blocked localStorage shows a clear warning and does not claim long-term persistence.
OUT_OF_SCOPE: inferred consent from existing database records, consent on another device/browser/hostname, shared/public identity, blanket employment/psychometric validation, resetting completed runs, APK source rebuild/redistribution, PROD or merges. Existing downloaded APK uses the same hosted web page and gets this fix after Vercel Preview update; native reinstall should not be required.
ACCEPTANCE: First login with no stored device preferences shows one setup panel; both boxes are opt-in, user checks main consent and independently selects draft opt-in, presses "Сохранить настройки" once. Home from profile/history and result preserves choices while showing only compact dashboard with optional settings edit. Browser reload/new tab restoring signed cookie restores preferences. Editing changes them only when explicitly saved. Logout clears settings and drafts and resets onboarding for next login. Existing test form submission still sends consent=true only after approval. Unauthorized users cannot access results. All prior owner cookie and 21/60 draft regressions preserved.
REQUIRED_EVIDENCE: JS syntax, full Python tests, local HTTPS Chromium mobile owner test for navigation/reload/opt-out, 21/60 draft regression, isolated real PostgreSQL and exact Vercel Preview CI status; actual Android/WebView phone navigation remains owner acceptance NOT_RUN. Paid API budget 0; current assistant executor only; up to two evidence-based repairs.
ROLLBACK: Revert this scoped PATCH to exact f71e28c069d056dd903c5f58535741e84d74c188; local preferences may remain until next Logout/browser clearing, but obsolete UI ignores them. No Neon migration or backup/restore required; no PROD.
AUTHORIZATION_END: TEST patch technically verified and manual owner smoke test, no automatic additional feature.


### MVP-009 — read-only paired raw-score comparison (2026-11-17)

CAPABILITY_ID: UALP-MVP-009 / SAME_INSTRUMENT_REASSESSMENT_DELTA
USER_RESULT: In UALP's saved-history view, owner can select two completed runs of the same instrument and exactly matching form version + scoring algorithm, then display the two stored six-scale values and their arithmetic differences. Missing a second completion leaves the compare action disabled. Navigation back to history or Home preserves the previously accepted consent and session.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 privacy-sensitive owner-only historical raw score display, no recommendations.
AUTHORIZATION: Owner said "Все ок продолжаем" after accepting previous Home/consent fix. Their acceptance is local to MVP-008.1. One bounded read-only extension, not permission for ICAR-16 licensing, public psychometric interpretation or PROD.
BASE_COMMIT / OWNER_BRANCH: ac9f019b59450020409c2b6d454262d59a70b435 -> feature/ualp-mvp-006-draft-resume-test / draft PR #7, no main/PROD merge. Existing accepted Android APK continues to load same Preview hostname; no APK-source change.
SOURCE_OF_TRUTH: Existing PostgreSQL completed AssessmentRun and stored parent ScaleScores via authorized GET /api/history and GET /api/runs/{id}. No new SQL schema, scoring method, stored fields, writes or new endpoints. No outcome inferred beyond raw stored numbers.
SCOPE / HOTSPOTS: webapp/index.html UI only plus webapp/main.py visible TEST version, tests/verify_owner_session_ui.cjs synthetic local HTTPS Chromium scenario for two compatible Work Values runs, different-version rejection, RIASEC separation and filter change cleanup. Add one comparison panel and bounded selection of two. Select across existing loaded pages; filter change and Home clear selection. Read only a maximum of two existing run endpoints when owner explicitly clicks Compare. Require runId, scoring algorithm, exact 6 parent scales, matching canonical scaleIds, key and answeredCount, finite values within respective 0..4 / 0..40 ranges. If any mismatch do not display a misleading differential. A version mismatch is an error, not an automatic reinterpretation.
OUT_OF_SCOPE: ICAR catalog/rights, psychological/occupational interpretation, percentile/norms, cross-test scoring, trends outside two runs, data export, new backend identity, new migrations, new paid services, Android wrapper upgrades and PROD.
ACCEPTANCE / REQUIRED_EVIDENCE: Existing full Python / JS syntax CI; local HTTPS synthetic Chromium comparing two v1 Work Values runs (difference +0.50), rejects v2 alongside v1, RIASEC not mixed, clears selection on filter change, preserves login + Home/consent/draft regressions; existing real PostgreSQL integration PASS for immutable stored runs; Vercel exact commit Preview status SUCCESS; owner phone check that second-pass comparison is available only after two completions. Actual private authenticated Vercel browser and Android hardware runtime remain NOT_RUN until verified.
MIGRATION / ROLLBACK: NONE; revert MVP-009 UI/test/version commits to exact ac9f019b59450020409c2b6d454262d59a70b435. No database backup or installed APK needed. Historical runs preserved.
RISKS: experimental unvalidated RU translations, raw differences are not evidence of statistically meaningful growth; no numeric meaningful-change threshold; user sees a prominent explanatory warning. Version provenance is from existing catalog form version: prior data-model assumption of versioned immutable forms applies, migration is separately authorized if broken.
TEST_TARGET: same existing fixed owner Vercel branch Preview, no new domain/session. EXECUTOR: current assistant only. PAID_API_BUDGET: 0. REPAIR_LIMIT: 2 focused cycles. STOP_CONDITIONS: schema change, authority violation, privacy leak or repeated failure without evidence.
UNRESOLVED_DECISIONS: NONE within raw comparison UX. AUTHORIZATION_END: technically verified TEST candidate + owner handoff; no automatic next module or PROD.


### MVP-010 — owner-only profile report, explicit copy / manual fallback (2026-11-17)

CAPABILITY_ID: UALP-MVP-010 / PRIVATE_PROFILE_TEXT_SUMMARY
USER_RESULT: Owner can open already saved Profile and tap "Подготовить сводку" to see a concise raw Work Values and RIASEC text report, then copy it if explicitly desired for personal notes or analytical work. No new test or new backend record is created.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 privacy-sensitive personal assessment text being intentionally transferred to device clipboard.
OWNER_AUTHORIZATION: "Начни" after acceptance of MVP-009 UI. One bounded next product increment without adding new psychological claims or career recommendations.
BASE_COMMIT: 461f9812eba39d8944895aee9b5f0855464d5503; OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test; exact stable private Vercel TEST Preview hostname unchanged. PR #7 remains DRAFT.
CANONICAL: Existing owner-authenticated GET /api/profile backed by immutable persisted PostgreSQL ScaleScores, form/version/algorithm status and timestamps. No new API/SQL/migration, no use of raw Responses. UI generates plain text from profile data already read in the user's authenticated session. It never reads or stores access key, question text, draft answers or source scoring rules.
SCOPE / HOTSPOTS: webapp/index.html adds owner-initiated on-screen report, source validation for known two form keys and exactly six parent scales, experimental status, read-only report textarea, user-initiated clipboard copy with manual selection fallback if clipboard permission fails, hide/clear on Home/profile reload/logout. webapp/main.py visible TEST version only. tests/verify_owner_session_ui.cjs synthetic local HTTPS Chromium profile fixture, generation, privacy, clipboard success/denial, clear on navigation. Governance and this existing Build Packet.
OUT_OF_SCOPE: public sharing, automatic network export, PDF/email/third-party upload, ICAR-16 normative interpretation, IQ/job fit, psychological conclusions, scores across forms normalized to comparable units, client HTML print, Android DownloadManager, new data entities/storage, new APK signing, PROD.
ACCEPTANCE / EVIDENCE: Profile report hidden before explicit action; profile methods with known keys only, six finite scores in 0..4 / 0..40, parent scale ID/key/count validation; include form version, algorithm, validation status, latest date, completed runs. Unsupported future methodologies ignored rather than inferred. Report contains no secret, prompts or raw answers; no automatic clipboard write and no localStorage writes. Copy success shows acknowledgement; clipboard unavailable selects text for manual copying; hide/Home/logout clear transient report. Auth gate unchanged. Full Python/JS syntax, local HTTPS Chromium regression, isolated real PostgreSQL existing profile/history and source-lock tests, exact Vercel Preview build; owner in-browser/Android acceptance separate.
SCHEMA_IMPACT / MIGRATION: NONE. Existing 30-day session, saved device preferences, draft responses and scale scores unchanged. No additional retained personal data.
ROLLBACK: revert MVP-010 UI/test/visible-version edits to exact 461f9812eba39d8944895aee9b5f0855464d5503 on TEST branch. No DB backup, migration or APK reinstall; existing prior PR #7 behavior unaffected.
RESIDUAL_RISK: Pasting to another app/chat transfers private assessment scores under owner's control; platform clipboard can be observed or cleared by OS/app, so report contains an explicit warning. Android WebView may deny clipboard API; fallback visible selection provided. Report is raw numerical record only, not validated psychological output.
EXECUTOR_PERMISSION: current assistant. PAID_API_BUDGET: 0. REPAIR_LIMIT: max 2 evidence-based cycles. STOP_CONDITIONS: credential leak, required privacy guard failure, source drift, missing CI access, schema/score mutation, unauthorized PROD/expense. AUTHORIZATION_END: exact tested feature + owner TEST handoff; no automatic next module/main/PROD.


### MVP-011 — owner development route / verified progress overview (2026-11-17)

CAPABILITY_ID: UALP-MVP-011 / OWNER_DEVELOPMENT_ROUTE
USER_RESULT: From Home the owner can open "Мой маршрут", see which UALP pilot assessments have stored completed runs, whether an owner profile exists, whether at least two runs of one method exist for potential historical comparison, and which planned but unimplemented career-learning stages are not available. Owner may navigate to existing Profile, History or Home without new sign-in or consent.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 owner-only read profile summary, no persistent learning records/interpretations.
AUTHORIZATION: Owner said "Продолжай" immediately after MVP-010 technical candidate. MVP-010 remains AWAITING_USER_ACCEPTANCE; this permission covers one bounded following capability only and does not itself accept MVP-010 nor approve main/PROD.
BASE_COMMIT / OWNER_BRANCH / TEST: d9541034d299d1a2222e1076694da974c67db93d / feature/ualp-mvp-006-draft-resume-test, current draft PR #7; exact same existing Vercel Preview origin, Android wrapper unchanged.
CANONICAL: Existing authenticated GET /api/profile backed by actual completed PostgreSQL runs; derived status UI is not authority over respondents or learning assignments. Progress counts only the two running experimental pilot instruments: UALP_WV21_RU_LIKERT and ONET_SHORT_60_DIGITAL. ICAR-16 is not yet enabled in current owner user interface, and occupational matching, gap plans and learning assignments have not been implemented. Do not infer skill levels, job suitability, IQ, ability or validity from tests.
SCOPE: webapp/index.html Home button "Мой маршрут"; read-only Roadmap screen with 5 staged notices (pilot testing, stored profile, retake comparison availability, pending ICAR, pending career/learning system), link navigation Profile/History/Home. Pull /api/profile anew on owner-initiated open; no polling/caching, no new endpoints, fields, schema or server writer; safe DOM textContent only. Profile validation rejects malformed method/count payloads and duplicates; unknown future form keys ignored when counting two pilot instruments. State of two total runs is labelled only as potential comparison until exact formVersion/algorithm check in existing History logic.
OUT_OF_SCOPE: unvalidated automated recommendations, career Fit/Readiness/Opportunity scoring, learning assignments, role knowledge base licenses, new cognitive test sources, persisted manual goals, change to owner session/cookie, new data migration, API expenses, public release.
MIGRATION_PLAN / SCHEMA_IMPACT: NONE. Existing Neon TEST runs, saved results and local browser consent/drafts not changed. No new Android package release needed, same hosted source.
REQUIRED_EVIDENCE: full Python and JS syntax checks, synthetic local HTTPS Chromium with owner profile containing both methods and repeat runs, empty profile state, navigation to existing Profile, Home consent/session regression, 21/60 draft resume, real ephemeral PostgreSQL integration, Vercel exact TEST commit build status. Direct authenticated Vercel owner testing and native Android are separate NOT_RUN until observed.
ROLLBACK: revert MVP-011 UI/test/visible-version changes to exact d9541034d299d1a2222e1076694da974c67db93d, without DB rollback or file copying. No new protected data or credentials.
RESIDUAL_RISK: Process statuses represent availability of the application's pilot features, not respondent aptitude, and must not be interpreted as professional guidance. If a future form activates, its stage needs explicit scoped update. User preferences and session stay unchanged.
PAID_API_BUDGET: 0; EXECUTOR_PERMISSION: current assistant; REPAIR_LIMIT: two focused evidence-based cycles; STOP_CONDITIONS: stored data mismatch, privacy leak, validation bypass, missing required CI, out-of-scope architecture or PROD dependency. AUTHORIZATION_END: exact TEST candidate and owner acceptance handoff; no automatic next implementation.


### MVP-010.1 — transient private report cleanup across navigation (2026-11-17)

CAPABILITY_ID: UALP-MVP-010.1 / REPORT_DOM_CLEAR_ON_LEAVE
USER_RESULT: The report created by "Мой профиль → Подготовить сводку" must be cleared from the hidden page as soon as owner navigates to History or a saved Result; when returning to Profile the owner can explicitly regenerate it from already-authorized profile data.
WORKFLOW_MODE: PATCH_FIX; RISK_CLASS: L2 private owner score text remaining in hidden DOM. User's "Продолжай" authorizes bounded technical hardening of the previously created profile report; it does NOT constitute manual acceptance of MVP-010 or MVP-011.
BASE_COMMIT: b6c75183c36e5a3eccf792f626c6f5d2e7981628; OWNER_BRANCH: feature/ualp-mvp-006-draft-resume-test / DRAFT PR #7; same fixed Vercel TEST origin. Current owner-session Android wrapper and Neon TEST unchanged.
SOURCE_FINDING: Existing Home and Hide paths clear generated report. Navigation Profile→History or Profile→Saved Result hid the Profile section but left the report's private text in a hidden textarea, retaining more data than the UI promised. The same user can return to profile and explicitly regenerate.
SCOPE: webapp/index.html: common show(view) clears report textarea/visibility when leaving visible Profile; preserve authorized state.profileData for re-generation after returning from History or Result. Existing Home still clears all profile state. tests/verify_owner_session_ui.cjs adds synthetic local HTTPS Chromium regression covering Profile→History→Profile and Profile→Saved Result→Profile, empty hidden report and explicit safe regeneration.
OUT_OF_SCOPE: server report export, storing copies, changing clipboard permissions/OS clipboard, server auth/scoring, DB schema, draft policy, occupation recommendation, PROD, APK package/signing changes.
SCHEMA / MIGRATION: NONE. No canonical writes, IDs or saved answers changed. No personal data committed to repository; only synthetic test fixtures.
ACCEPTANCE: After report generation and leaving Profile via History or Result, reportPanel hidden and reportText empty, profile result still accessible; returning Profile lets owner generate the same raw report. Home / Logout unchanged. Existing login/cookie, consent, 21/60 drafts, route stages and saved history/compare regressions continue PASS. Full Python/JS/local HTTPS Chromium, isolated real-PG and exact Vercel source status needed; owner phone remains NOT_RUN.
ROLLBACK: revert small privacy patch to exact b6c75183c36e5a3eccf792f626c6f5d2e7981628; not a DB migration. Existing APK loads hosted UI from same origin; no reinstall needed.
PAID_API_BUDGET: 0. EXECUTOR_PERMISSION: current assistant only. REPAIR_LIMIT: 2 focused cycles. STOP_CONDITIONS: validation/privacy failure, unexpected schema impact, unavailable required CI, paid resource, PROD boundary.
AUTHORIZATION_END: TEST technical receipt; manual acceptance of both prior features still pending, no automatic third new product feature.


### MVP-011.1 — UALP batched acceptance QA / profile aggregate integrity (2026-11-17)

CAPABILITY_ID: UALP-MVP-011.1 / BATCHED_TEST_QA_PROFILE_TOTALS
USER_RESULT: Owner requested fewer interruptions ("Мое участие снизить до минимума. Пусть наберётся потом протестом"). Existing pending MVP-010/MVP-011 and this focused QA hardening are grouped into one later mobile UAT. A confirmation is not required after each sub-step; this does NOT convert pending features into USER_ACCEPTED or authorize indefinite next development.
WORKFLOW_MODE: PATCH_FIX / QA hardening of existing route; RISK_CLASS: L1 source validation + L2 mobile private-results QA.
BASE_COMMIT / OWNER_BRANCH: e0591f0b0b931022e69c114b75c353f6e9f18897 / feature/ualp-mvp-006-draft-resume-test; existing Draft PR #7 / stable fixed Vercel TEST hostname.
CANONICAL: Read-only authorized /api/profile from real saved PostgreSQL completions, with methodCount == displayed method list length, completedRuns == sum(method completedRuns). This is already backend behavior, so client must fail closed on inconsistency rather than displaying a fabricated state. Never change source data to make the check pass.
SCOPE / HOTSPOTS: webapp/index.html readRoadmapProgress() consistency check only; tests/verify_owner_session_ui.cjs adds mismatched aggregate negative checks; docs/qa/UALP_BATCH_ACCEPTANCE_TEST_20261117.md records one later owner-phone scenario. No new product screen or score interpretation, no new API/schema/Android native changes.
OUT_OF_SCOPE: career scoring or recommendations, ICAR-16 catalog, public survey, data edits, PROD, paid tools and additional executors. Further blocks must have their own scope and risk checks; owner batched UAT does not imply blanket permission.
SCHEMA_IMPACT / MIGRATION: NONE; rollback to exact e0591f0b0b931022e69c114b75c353f6e9f18897; no data migration, no files copied to device.
ACCEPTANCE: synthetic Chromium rejects a profile whose completedRuns or methodCount contradicts returned saved methods while a valid/empty owner profile still renders; all earlier cookie/Home/profile/report/history/21/60 draft tests PASS; real ephemeral PostgreSQL existing integration PASS, Vercel commit SUCCESS. Owner phone UAT explicitly DEFERRED_UNACCEPTED.
REQUIRED_EVIDENCE: commit SHA, Python/JS + Chromium CI, isolated real PostgreSQL, Vercel Preview exact source, remaining NOT_RUN; Android build if CI re-runs (native device NOT_RUN).
TEST_BUNDLE: MVP-010/010.1 owner report + MVP-011 route + MVP-011.1 aggregate validation; one short combined check after technical TEST checkpoints; see docs/qa/UALP_BATCH_ACCEPTANCE_TEST_20261117.md. Keep other user-acceptance gaps accurately flagged, no fabricated pass.
EXECUTOR_PERMISSION: current assistant, no Codex. PAID_API_BUDGET: 0. REPAIR_LIMIT: 2 evidence-based focused cycles.
STOP_CONDITIONS: source mismatch, broken owner session/cookie, invalid profile leak, missing essential TEST, PROD/business decisions/paid dependency.
AUTHORIZATION_END: verified TEST checkpoint with batched owner acceptance deferred, STOP. Does not authorize continuing asynchronously after this turn.


### MVP-012 — saved assessment provenance in result card (2026-11-17)

CAPABILITY_ID: UALP-MVP-012 / STORED_RESULT_PROVENANCE
USER_RESULT: Each existing Work Values/RIASEC saved result displays the actual form key/method name, version of the completed questionnaire, source-validated status and persisted record date alongside original score algorithm and six scores. Owner can distinguish a form/version from another without reopening History. No new assessment or recalculation.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 owner-only historical evidence read across existing PostgreSQL catalog/run tables and UI.
AUTHORIZATION: Owner said "Начни" after requesting deferred batched phone acceptance. This authorizes one bounded read-only addition; not a blanket mandate to create unvalidated career advice, change scores, install a new APK or merge to main/PROD.
BASE_COMMIT / BRANCH / TEST: 3f7c4612b47ed38d9f0f574629e3d27c40f3014e; feature/ualp-mvp-006-draft-resume-test / Draft PR #7; existing pinned Vercel Preview hostname unchanged, no PROD.
CANONICAL: ualp_assessment_runs (run_id/form_id/algorithm_version/status/created_at) plus ualp_catalog_forms (form_id/form_key/form_version/validation_status). stored_result() already reads stored six parent scale scores and is used for POST idempotency and GET history/profile. Augment its existing select with an inner join and only these non-secret source-version metadata fields. recordedAt is the persisted record created_at timestamp (not an invented completion duration); formatted locally by UI. Validation status stays exactly as returned by catalog; no inferred score norm or quality claims.
SCOPE / HOTSPOTS: webapp/main.py stored_result() return additive formKey, formVersion, validationStatus, recordedAt and visible test version; webapp/index.html new resultProvenance readonly display, strict allowlist for two method+algorithm combinations, COMPLETED status and basic metadata checks. Existing score display/calculation, source licensing, save/retry, owner authorization, history paging, profile and draft behavior unchanged. Existing browser fixtures updated to test this contract including unexpected form key rejection; ephemeral real PostgreSQL assertions for Work Values and owner RIASEC source/readback.
OUT_OF_SCOPE: new scoring, IQ/job-fit, product validation, different owner/user model, data export, migrations, new TEST domain, Android wrapper native changes, new item banks, PROD or public use.
SCHEMA_IMPACT / MIGRATION: NONE. Read-only join for existing keys, zero new writes/deletes. No migration or manual file copying. Existing stable owner TEST APK loads hosted web UI automatically; no APK reinstall required.
ACCEPTANCE / REQUIRED_EVIDENCE: exact source CI (Python/JS, local HTTPS Chromium with saved result and negative mismatched form, 21/60 draft + cookie/Home/history comparisons); ephemeral PostgreSQL integration including two form/version/status/date readbacks and unchanged POST retry equality; Vercel exact commit SUCCESS; Android build if automatically triggered. Owner phone UAT is intentionally DEFERRED_UNACCEPTED per docs/qa/UALP_BATCH_ACCEPTANCE_TEST_20261117.md. Neither GitHub build nor synthetic Chromium proves authenticated hosted user runtime.
ROLLBACK: Revert MVP-012 code and fixture additions to 3f7c4612b47ed38d9f0f574629e3d27c40f3014e in TEST branch, keep Neon data/old APK; no DB rollback.
RESIDUAL_RISK: Original user answers and unvalidated Russian translations are still research-only; returning "NOT_REVIEWED" is not quality certification. RIASEC historical results may use a different form version; the card must show actual version rather than guess. One owner-shared TEST key is not multi-tenant security.
EXECUTOR: current assistant only; PAID_API_BUDGET: 0; REPAIR_LIMIT: max two evidence-bearing cycles; STOP_CONDITIONS: security leak, unexpected source schema, CI fail beyond repair, cost, PROD or changed DB ownership. AUTHORIZATION_END: exact TEST-verified receipt and batched UAT note; STOP.


### MVP-013 — accessible raw score bars on saved result screen (2026-11-17)

CAPABILITY_ID: UALP-MVP-013 / RESULT_RAW_SCALE_BARS
USER_RESULT: On the individual saved result screen, show six mobile-readable labeled meter bars and the **exact** raw scale values for the two pilot forms, Work Values 0–4 and RIASEC 0–40. Make the result understandable at a glance without converting raw responses into normative percentages or occupations. Preserve readable numbers and the source/version passport.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L1 read-only client presentation with L2 owner privacy/security negative gate.
OWNER_AUTHORIZATION: "Продолжай" authorizes one bounded addition on prior draft TEST candidate. Owner asked to defer combined UAT; this is **not** acceptance of MVP-010, MVP-011, MVP-012 or MVP-013, nor permission to merge or publish.
BASE_COMMIT / OWNER_BRANCH / TEST_TARGET: 29f81fc2ec2287cedd1996121ee13cea0c4c60e3; feature/ualp-mvp-006-draft-resume-test / DRAFT PR #7; same fixed private Vercel Preview hostname and original Android TEST wrapper. Source from exact approved previous checkpoint.
CANONICAL / ALGORITHMS: Existing persisted \`GET /api/runs/{runId}\` or idempotent POST response. Work Values 6 parent means in 0..4, \`WORKVALUES-MEAN-v1\`. RIASEC 6 raw sums in 0..40, \`RIASEC-SUM-v1\`, expected whole numbers. Separate parent group metrics from source forms; do not combine or normalize interpretations. The native HTML \`meter\` element simply illustrates raw position against its own maximum; text labels and values remain the primary accessible evidence.
SCOPE / HOTSPOTS: webapp/index.html: one result-screen \`meter\` per saved parent scale, visible raw value with denominator, explanatory warning "not percent/norm", mobile-friendly text row. Validate saved result form/version/provenance, exactly six unique source scale keys and finite correct-range raw values **before** displaying results. webapp/main.py changes visible APP_VERSION only; tests/verify_owner_session_ui.cjs local HTTPS synthetic Chromium asserts six meters, max and value for both forms, rejection of forged 41/40 and unknown form key. No third-party charting, no new API or library. Existing profile card meters are unchanged.
OUT_OF_SCOPE: public sharing, psychometric norming, change to raw scores or their formulas, IQ/aptitude, new assessments, respondent data mutation, downloadable APK modifications, schema migration, versioned catalog changes, career recommendations, PROD.
SCHEMA_IMPACT / MIGRATION: NONE, no database read/write change beyond existing saved GET; no installed APK replacement. All original saved scores/profiles remain canonical. No secrets, real questions or data in GitHub.
REQUIRED_EVIDENCE / ACCEPTANCE: Python and JS syntax + full existing regressions including one-time consent, cookie, history/compare, local drafts, personal report, route; synthetic Chromium asserts correct meter count/bounds and numeric text and forged out-of-range source rejection; existing isolated real PostgreSQL suite PASS for original readback; Vercel exact-head success; optional Android APK CI build if automatically triggered. **Owner mobile UAT DEFERRED**; no claim of hosted authenticated runtime until tested.
ROLLBACK: Restore exact 29f81fc2ec2287cedd1996121ee13cea0c4c60e3 on TEST branch; no SQL or APK data rollback. Older frontend readable text/score list remains.
RESIDUAL_RISK: Results still from experimental methods and unreviewed Russian translations; visually appealing bars can be mistaken for normative scores, so explicit visible warning is mandatory. Numeric range-check gate does not constitute source validation or ability inference.
EXECUTOR_PERMISSION: current assistant only. PAID_API_BUDGET: 0. REPAIR_LIMIT: up to two focused evidence-based fixes. STOP_CONDITIONS: changed DB schema, leaked credentials, necessary paid tools, failed protected CI, main/PROD boundary. AUTHORIZATION_END: exact TEST verified checkpoint plus deferred acceptance bundle, STOP.


### MVP-014 — bounded historical raw-score timeline (2026-11-17)

CAPABILITY_ID: UALP-MVP-014 / BOUNDED_RAW_SCORE_TIMELINE
USER_RESULT: In saved History, once a method/version/algorithm has at least two compatible completed runs, the private owner may view up to six recent stored raw-score points for each of six parent scales, by recorded date. No re-assessment, database write or manual copy is required. The timeline uses small self-rendered SVG lines plus complete per-date numerical text; it does not claim statistical growth or job readiness. If there are only single runs, action is disabled with an explanation.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L2 bounded read-only owner score retrieval + L1 client display.
AUTHORIZATION: Owner said "Продолжай" and previously requested deferred bundled UAT; this permits one bounded TEST increment and its technical regression checks, not unlimited development, a new data owner, recommendation engine, migration or PROD.
BASE_COMMIT / OWNER_BRANCH / TEST_TARGET: 0d789ef1417b972b798f5ded7d0d94f90c167ebe; feature/ualp-mvp-006-draft-resume-test / DRAFT PR #7. Fixed existing Vercel Hobby Preview hostname as previous TEST, no domain/session rotation. Android wrapper code unchanged.
CANONICAL: Existing completed-run \`GET /api/history\` (keyset paginated, 10 entries/page) and authenticated \`GET /api/runs/{runId}\` returning six persisted parent ScaleScores and form/version/status/recordedAt. Client groups only \`COMPLETED\` items by exact \`formKey + formVersion + scoringAlgorithmVersion\`, requires 2+, chooses at most six of already loaded history entries, and reads at most six existing saved results when user explicitly taps "Показать динамику". It checks response run IDs, method/form version, algorithm, date parity, six identical stable scale IDs/keys/item counts and proper 0–4 or 0–40 range (integer RIASEC values) before rendering. No inferred user ID, no new service, no scores recomputed.
SCOPE / HOTSPOTS: webapp/index.html, version stamp in webapp/main.py, synthetic local HTTPS Chromium regression in tests/verify_owner_session_ui.cjs. One History dropdown listing compatible groups and one Trend button; read-only timeline screen with six scalable per-scale line charts and raw date:value text; navigation to History or Home clears its transient chart DOM. Existing two-run comparison, history filter/pagination, login/cookie, owner consent, drafts, personal report and roadmap remain unchanged. No external chart library, SVG strings from sources, or network resources.
OUT_OF_SCOPE: backend trend calculation/endpoint, multitenant identities, new data entities, canonical schema migration, trend slopes/predictions, validation/norms, psychological or hiring advice, joining across versions, unseen history auto-crawling, independent Android native release, PROD.
SCHEMA_IMPACT / MIGRATION: NONE. No new SQL, no writes to Neon, no changes to saved assessment scoring or dataset. Rollback restores exact 0d789ef1417b972b798f5ded7d0d94f90c167ebe on TEST candidate; no DB restore or phone reinstall.
ACCEPTANCE / REQUIRED_EVIDENCE: JS syntax + Python full tests and synthetic mobile HTTPS Chromium, including v1 Work Values 2-run timeline, exclusion of incompatible v2/other method, six SVG lines/twelve points, exact raw text and mixed-version rejection, safe failure for forged 9/4, disabled action on one RIASEC completion, no hidden chart retention after leaving Trend; existing history/compare/profile/route/drafts regressions PASS; separate isolated ephemeral PostgreSQL real DB integration PASS; exact Vercel branch Preview SUCCESS; Android APK build if automatically triggered. Owner actual phone UAT remains DEFERRED_NOT_ACCEPTED in docs/qa/UALP_BATCH_ACCEPTANCE_TEST_20261117.md.
ROLLBACK: TEST source-only revert to exact BASE_COMMIT, no existing records or APK changed.
RISKS: Reassessment variability is not proof of growth. Sample selection is limited to already-loaded completed runs (show "Показать ещё" for older entries), at most six per plot. Client uses same owner TEST key access boundary, no authorization widening. Show both raw numeric timeline and visible experimental disclaimer to reduce metric confusion.
EXECUTOR_PERMISSION: current assistant only; no Codex/other agents. PAID_API_BUDGET: 0. REPAIR_LIMIT: 2 evidence-based focused fixes. STOP_CONDITIONS: source schema change, auth leak, CI failure beyond repair, paid service, PROD boundary, new substantial business decision. AUTHORIZATION_END: exact TEST-verified PR receipt and deferred owner bundle, STOP. Manual acceptance is not implied by automation.


## UALP-CAREER-KB-001 — Source/Data Contract Foundation (2026-11-18)

CAPABILITY_ID: UALP-CAREER-KB-001 / CAREER_ROLE_KB_FOUNDATION
USER_RESULT: A small, testable and source-aware design for occupation/role requirements and competencies, which can later support evidence-based career learning without interpreting RIASEC/Work Values raw scores as job readiness.
WORKFLOW_MODE: ECOSYSTEM_PLANNING / bounded design with synthetic contract tests; RISK_CLASS: L1 for documentation and isolated synthetic test only.
BASE_COMMIT: 3cf3378ce8b3256fc18e0e6bf8303cd21cc15a25
OWNER_BRANCH: feature/ualp-career-role-kb-foundation-docs (separate docs candidate; existing owner Vercel TEST branch and Draft PR #7 remain frozen).
OWNER / TEST: Vahram; no TEST deployment in this block. PAID_API_BUDGET: 0; EXECUTOR: current assistant only.
SCOPE: inspect current accepted UALP PostgreSQL and profile contracts; verify official O*NET Database 31.0 metadata/licensing; write proposed versioned occupation/competency/source/provenance contract; add fully synthetic fixture and source-free negative tests.
OUT_OF_SCOPE: real O*NET dataset ingest, new SQL tables, Neon writes, UI/API implementation, ranking/matching, inferred skills, career percentages, ICAR activation, personal data, PROD/main merge, paid tools.
CANONICAL / SHARED_HOTSPOTS: docs/architecture/CAREER_ROLE_KB_CONTRACT.md is proposal only; existing runtime authority remains docs/architecture/DATA_CONTRACT.md and migrations/001_initial_postgres_test.sql. Shared hotspots future: profile endpoint, external taxonomy/version, schema, provenance, license; NONE changed now.
SCHEMA_IMPACT: NONE. MIGRATION_PLAN: NOT_REQUIRED_NOW; future role/skill storage must have separately approved additive migration+backup+rollback and real PostgreSQL checks.
REQUIRED_EVIDENCE: official source/licence references; synthetically verified FK/version/scale/unknown guards; path/readback checks; legacy runtime unchanged. Full CI/Vercel/Neon/Android runtime is NOT_RUN for this isolated design and not a claim of real integration.
ROLLBACK: revert docs-only commit (or leave proposed branch unmerged); original owner TEST head 3cf3378ce8b3256fc18e0e6bf8303cd21cc15a25 remains untouched; no database restore.
STOP_CONDITIONS: source/license ambiguity, production data changes, new migrations, unapproved public release or automated career inference.
NEXT_BOUNDARY: offline verified O*NET 31.0 source-lock and reader only after separate instruction, then a distinct migration authorization if needed.
AUTHORIZATION_END: contract/synthetic fixture verification receipt and report; STOP.


### UALP-CAREER-KB-002 — source lock and offline reader (2026-11-18)
CAPABILITY_ID: UALP-CAREER-KB-002 / CAREER_KB_SOURCE_LOCK_AND_OFFLINE_READER
USER_RESULT: Offline reader for a bounded O*NET 31.0 occupation/essential-skill subset, verified on synthetic fixtures and designed to fail-closed on source drift; real-source import pending exact official files.
WORKFLOW_MODE: IMPLEMENT_FEATURE (isolated offline developer tool), RISK_CLASS: L2 provenance/ingestion safety; no runtime changes.
BASE_COMMIT: 8e98b8c38227ff6e4397a35daca4d3b7ce95f7b8
OWNER_BRANCH: feature/ualp-career-kb-offline-reader-test (new branch; unaccepted owner UALP TEST branch untouched).
SOURCE: Official O*NET Database 31.0 CSV release and dictionary; precise source acquisition blocked by network environment; do not treat the accompanying pseudo-manifest as an actual source lock.
SCOPE: career_kb/offline_reader.py; tests/test_career_kb_offline_reader.py; direct source URLs/documentation; source-lock receipt. Explicitly no actual O*NET records, ratings or licenses imported into SQL or public app.
SHARED_HOTSPOTS: Future role KB schema and assessment profile bridge only; current webapp, migrations, user data, scoring, Android and Vercel not changed.
CANONICAL / SCHEMA_IMPACT: NONE. No new tables, IDs, statuses or personal scores. MIGRATION_PLAN: NOT_REQUIRED for isolated offline reader; any real database import demands separate backup, additive migration, rollback and owner authorization.
REQUIRED_EVIDENCE: official source page and dictionary, 12 local synthetic pytest checks PASS, Python compile PASS; official CSV acquisition/hash/real-data readback NOT_RUN/BLOCKED. Read back exact GitHub commit.
TEST_TARGET: LOCAL_ONLY; existing Neon/Vercel owner TEST untouched. No hosted candidate for this change.
ROLLBACK: revert docs and isolated Python module/test; TEST owner head stays 3cf3378ce8b3256fc18e0e6bf8303cd21cc15a25.
PAID_API_BUDGET: 0; EXECUTOR_PERMISSION: current assistant only; no Codex/CI-triggering PR/other executors.
STOP_CONDITIONS: missing official source bytes; unknown license or provenance; migration/PROD needs; altered acceptance gate.
STATUS: PARTIAL / LOCAL_TESTED / OFFICIAL_SOURCE_BYTES_BLOCKED.
NEXT_BOUNDARY: independently acquire official CSV files, establish SHA256 and row readback, and run real offline subset; no PostgreSQL migration without separate permission.
AUTHORIZATION_END: file/commit receipt and report, STOP.


### UALP-CAREER-KB-003 — one-shot GitHub Actions real O*NET source lock (2026-11-18)
CAPABILITY_ID: UALP-CAREER-KB-003 / ONET31_ONE_SHOT_SOURCE_VERIFICATION
USER_RESULT: Obtain original official O*NET 31.0 CSV bytes from isolated GitHub-hosted Actions, create exact SHA-256 source lock and run existing offline reader on two actual occupations.
WORKFLOW_MODE: IMPLEMENT_FEATURE / source acquisition unblock and runtime-on-GitHub QA; RISK_CLASS: L2 provenance gate.
OWNER_AUTHORIZATION: "Да разрешаю" replying to explicit one-time GitHub Actions download/hash/reader proposal; no Codex, paid API, main, PROD or migrations.
BASE_COMMIT: a2b060a0295f612aca3127fdd6753b8304e5815a; OWNER_BRANCH: feature/ualp-onet-31-source-lock-once ; TEST_TARGET: disposable hosted GitHub Actions runner only.
SCOPE: one read-only GitHub Actions workflow, offline CI source download helper, receipt and artifact, with exact source release and source integrity validation.
OUT_OF_SCOPE: cloud TEST app changes, Neon writer or schema, assessment instruments/keys, job matching, automated role scoring, public UALP respondent, user data, PR #7, Android, Vercel release, merges.
CANONICAL / SCHEMA_IMPACT / MIGRATION_PLAN: Existing DB/IDs and production untouched; no migration or rollback of stored data; source artifact immutable by SHA and time stamped for research only.
DEPENDENCIES / RISK: official www.onetcenter.org HTTPS reachable from GitHub-hosted runner, existing locked offline reader; no mirrors allowed. If official bytes cannot be acquired or schema differs, FAIL CLOSED.
ACCEPTANCE / REQUIRED_EVIDENCE: exact GitHub SHA and run ID, job completion, SHA256 and row readback for 3 files, two real occupation names and source-backed skill rows. Generated artifact retained 7 days; review in current conversation. Static YAML check alone is not source verification.
ROLLBACK: remove/revert isolated workflow branch (leave user TEST unmodified).
PAID_API_BUDGET: 0; current assistant only. GitHub Actions single owner-approved run. REPAIR_LIMIT: max two focused evidence-producing fixes if required.
STOP_CONDITIONS: lack of repo permissions, unknown paid spend, unsafe redirect, invalid source provenance or source schema, missing runner evidence.
AUTHORIZATION_END: source receipt and concrete final report; no automatic next block.


#### UALP-CAREER-KB-003 — final GitHub Actions evidence receipt (2026-11-18)

SOURCE_VERIFICATION: **PASS**; exact initial workflow commit `1171ece481fde70a7493ddf581fb0a54d9f6fa68`; run `44322510909`, attempt 1, SUCCESS, job `134864896990`.
Official O*NET Database 31.0 direct HTTPS: occupation_data.csv 1016, essential_skills.csv 18200, scales_reference.csv 33; file SHA256 frozen in docs/research/UALP_ONET_31_REAL_SOURCE_LOCK_20261118.json and read back from archived artifact.
REAL_OFFLINE_READER: PASS — BI Analysts 15-2051.01; Data Scientists 15-2051.00; 40 source-skill observations, 39 observed and 1 suppressed/null. No career fit/proficiency inference.
ARTIFACT `14435511727`: ZIP checksum `4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d`, expires **2026-11-25 14:16 UTC**. Preserve source ZIP externally before expiration for reproducibility.
EVIDENCE: GitHub run/steps/logs, exact 3 CSV digest and independent recipient ZIP CRC/hash/row readback.
NOT_RUN: Neon/PostgreSQL writes, webapp/Android UI, owner UAT, PROD. Expected because zero runtime files or schema changed.
ROLLBACK: separate documentation experiment only; owner TEST PR #7 unchanged; no migration.
AUTHORIZATION_END: this run/verification source-lock block finished; STOP, no automatic database import or migration.


### UALP-CAREER-KB-004 — proposed PostgreSQL source catalog import (2026-11-18)

CAPABILITY_ID: UALP-CAREER-KB-004 / CAREER_KB_SAFE_IMPORT_DESIGN
USER_RESULT: Additive source-backed PostgreSQL Career KB schema candidate and deterministic offline real-source import plan for two verified O*NET occupations, without touching existing respondent data or online TEST.
WORKFLOW_MODE: IMPLEMENT_FEATURE (offline planner) + migration design only; RISK_CLASS: L2 offline source/provenance, L3 FUTURE schema execution (NOT AUTHORIZED / NOT_RUN).
BASE_COMMIT: b9d5c438c2f14e3136c88d778e393f3c5995f1eb
OWNER_BRANCH: feature/ualp-career-kb-import-plan-only; OWNER / TEST: Vahram, local source-locked isolated files; active Draft PR #7 remains separate.
CANONICAL: frozen O*NET Database 31.0 official CSV artifact run 44322510909 and github source_lock.json; 1016 occupation, 18200 essential-skills, 33 scales source records.
SCOPE: read-only career_kb/import_plan.py, focused local tests, two gated candidate SQL files under docs/migration_candidates, migration design documentation, Build Packet entry. No real source ZIP committed publicly.
OUT_OF_SCOPE: APPLY_SCHEMA, PostgreSQL writer/data ingestion, Neon TEST/PROD mutation, Vercel/Android, new endpoint, RIASEC/ICAR scoring, user profiles, job Fit/Readiness and Armenia market inference, extra CI/GitHub Actions.
SHARED_HOTSPOTS: existing migrations/001_initial_postgres_test.sql and runtime /api/profile remain untouched; new proposed career_ tables are isolated.
SQL/MIGRATION: candidate SQL not automatically runnable. Requires explicitly armed disposable-test-only session gate, backup and separate approval. Rollback script also gated and refuses nonempty tables. A populated Neon TEST import requires independently approved additive migration with backup, transactional idempotency and specific rollback.
SOURCE_READBACK: real original ZIP SHA256 4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d; exact source manifest with three SHA256 values confirmed. Readonly import JSON plan SHA256 78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d.
EXPECTED_SOURCE_ROWS: 2 occupations, 10 unique Essential Skills, 2 source scales (IM and LV), 40 requirements = 39 observed + 1 suppressed/null. Row-level source updatedAt 08/2024 or 08/2026 preserved.
ACCEPTANCE_EVIDENCE: 23 focused local pytest PASS (existing offline reader 12 + import planner 11 including original artifact); Python compile PASS; real source SHA/CRC/readback PASS. SQL structural guard check PASS; SQL execution against real PostgreSQL NOT_RUN. No direct mobile or authenticated TEST runtime checks.
ROLLBACK_THIS_BLOCK: revert isolated commit only, no persisted data changes. Candidate rollback SQL is test-only and unexecuted.
PAID_API_BUDGET: 0; EXECUTOR: current assistant; no additional executors; no GitHub Actions triggered under previous one-time approval.
REPAIR_LIMIT: up to 2 focused cycles. STOP_CONDITIONS: new DB/scheme ownership, migration or full import, paid infra, explicit end of scope, source mismatch, unverified runtime.
AUTHORIZATION_END: commit/receipt, STOP. NEXT_BOUNDARY: separately authorized ephemeral PostgreSQL migration/rollback rehearsal then separate Neon TEST approval, not automatic.


### UALP-CAREER-KB-005 — disposable PostgreSQL DDL/rollback rehearsal (2026-11-18)

CAPABILITY_ID: UALP-CAREER-KB-005 / DISPOSABLE_POSTGRES_SCHEMA_ROLLBACK_TEST
USER_RESULT: Prove the proposed Career KB SQL installs on a fresh PostgreSQL 18 service, protects an existing seeded AssessmentRun/Response/Score, rejects wrong-source and invalid ratings, refuses unsafe rollback, and safely removes only empty Career KB tables under a disposable-test-only gate.
WORKFLOW_MODE: STRESS_TEST_ONLY (bounded real database integration rehearsal); RISK_CLASS: L3 migration/schema testing only, without changes to candidate SQL files or hosted TEST.
BASE_COMMIT: c1d68bcd5ced1c739651169df48f2ca4c9866c96
OWNER_BRANCH: feature/ualp-career-kb-postgres-rehearsal-once
TEST_TARGET: One ephemeral public-repository GitHub Actions postgres:18 service, fixed 127.0.0.1:5432/ualp_ci, no remote credentials or paid services.
SCOPE: isolated tests/test_career_kb_pg_rehearsal.py, one-shot path/branch-scoped Actions workflow and receipt; existing staged migration SQL/rollback are read without changes.
OUT_OF_SCOPE: any Neon TEST/PROD schema/data write, real user data, stored scoring changes, Vercel/Android, migration promotion, public career APIs, role recommendations, source CSV ingestion, application run.
SHARED_HOTSPOTS: exactly docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql and UALP_CAREER_KB_004_SCHEMA_ROLLBACK_DISPOSABLE_ONLY.sql, existing migrations/001_initial_postgres_test.sql; no changes to any of these files.
CANONICAL / SCHEMA_IMPACT / MIGRATION_PLAN: no persistent schema impact. All SQL statements restricted to disposable postgres with explicit session gate; synthetic legacy baseline SHA256 before and after provides preservation evidence. No backup or migration of Neon authorized. SQL rollback drops only empty career tables.
ACCEPTANCE: exact source SHA + one Actions run + real DB test receipt, 7 added tables, negative FK/check/unique tests, nonempty rollback refusal, empty rollback PASS, unchanged assessment baseline, no second run. Any failure requires focused repair or BLOCKED receipt.
ROLLBACK_THIS_BLOCK: revert isolated GitHub branch; service container disposable and destroyed on job exit; no runtime rollback required.
PAID_API_BUDGET: 0. EXECUTOR_PERMISSION: current assistant, one GitHub Actions job for the explicitly requested ephemeral PostgreSQL check; no Codex or other parallel executor.
REPAIR_LIMIT: at most two evidence-based cycles; no unrelated reruns.
STOP_CONDITIONS: source/branch drift, non-local DB target, unexpected running actions, failure beyond bounded fixes, any need for Neon migration or paid API.
AUTHORIZATION_END: GitHub runtime receipt / safe fail report then STOP. Successful PostgreSQL test is not Neon TEST deployment acceptance.


#### UALP-CAREER-KB-005 — final source-locked disposable PostgreSQL receipt (2026-11-18)
EXACT_COMMIT_TESTED: `0b755dd24a46505a376e666135af99bc4a6fa69e`
RUN_ID: `44333540471`; JOB `134903969574`, SUCCESS.
TEST_LEVEL: REAL_DISPOSABLE_POSTGRESQL_18_E2E; pytest 1 passed, 12 targeted negative SQL checks; 7 Career KB tables installed and removed on real PG 18; 40 synthetic records (39 observed, 1 suppressed/null); baseline original 10 tables sha256 unchanged `d2a16a519f28d3822364e329021eb3af21a8ef42b0396c16e5c8ddc0ec8f8922`.
UNIQUE/FK_TARGETED: PASS — scale composite FK and source-record uniqueness checked by exact SQL constraint names, along with source/metadata/null bounds and cross-snapshot FK.
ROLLBACK: missing session gate DENIED, nonempty DENIED, empty after explicit synthetic cleanup PASS; no real data deleted. Candidate SQL files unchanged.
ARTIFACT: 14439678097 expires 2026-11-25 15:16 UTC; receipt SHA `464224c4e427b454360023548c765e9edf682faca201dbc644733dd0598b81d7`. Details: docs/research/UALP_CAREER_KB_005_PG_REHEARSAL_RECEIPT.md.
REPAIRS: initial YAML job context fixed; then negative tests strengthened; at most 2 meaningful repair cycles, no further run required.
NOT_RUN: real source writer, Neon TEST/schema, backup/restore, Vercel, owner UAT, Android, PROD. STOP. No automatic permission to progress.


### UALP-CAREER-KB-006 — Exact-source transactional Career KB importer, isolated PostgreSQL E2E (2026-11-18)
CAPABILITY_ID: UALP-CAREER-KB-006 / FROZEN_SOURCE_TRANSACTIONAL_IMPORT
USER_RESULT: A deterministic, fail-closed writer for the frozen 2026-11-18 O*NET 31.0 two-occupation subset (40 real source-skill measurements), with atomic failure behavior, concurrent idempotence and pre-existing data preservation in disposable PostgreSQL only.
WORKFLOW_MODE: IMPLEMENT_FEATURE; RISK_CLASS: L3 (SQL writes confined to authorized disposable E2E instance only).
BASE_COMMIT: 7d18fd3f0042de9ec57041dcdb14a068afd43bbb
OWNER_BRANCH: feature/ualp-career-kb-transactional-import-once; TEST_TARGET: isolated one-time GitHub-hosted PostgreSQL 18 service on localhost.
OWNER / TEST: Vahram, validation with no mobile UAT this block.
AUTHORIZATION: user's "Начнем" in response to the explicit next bounded transactional-importer block, **not** authorization for Neon TEST, PROD, migration promotion, Codex or other paid services.
SCOPE: career_kb/transactional_import.py; tests/test_career_kb_transactional_import.py; path-scoped one-run PostgreSQL Actions workflow; source-less integrity/receipt report; existing Build Packet extension.
SHARED_HOTSPOTS: docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql, disposable rollback SQL and existing migrations/001_initial_postgres_test.sql are read unchanged, not deployed to Neon; the current Assessment/Owner TEST and PR #7 remain untouched.
CANONICAL: verified exact O*NET Database 31.0 CSV hashes/receipt at run 44322510909; plan SHA256 78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d; original source archive is retrieved through read-only Actions artifact token, expires Nov25.
MIGRATION_PLAN: no mutation of any persistent DB; proposed additive SQL tested only on fresh disposable PostgreSQL 18, with synthetic legacy baseline, explicit session gates, and guarded rollback after clearing disposable data. Neon TEST rollout is a separate permission, with backup/restore and exact checked commit.
EXPECTED_EVIDENCE: official-source artifact readback, exact plan SHA validation, seeded real values 1 snapshot / 2 roles / 10 skills / 2 scales / 40 requirements (39 observed + 1 suppressed/null), 3 injected transaction failures leave 0 new records, concurrent first writes yield one INSERTED + one NOOP, conflicting existing record rejected, existing 10 assessment tables checksum unchanged, rollback disallows populated tables and removes empty ones. CI/job/receipt exact IDs must be recorded after execution.
OUT_OF_SCOPE: public app endpoints, personal career suitability/skill inference, Armenian job-market extrapolation, source ZIP commit, Neon/TEST/PROD writes, Vercel/Android, main merge, package deployment.
ROLLBACK: isolated branch revert; disposable PostgreSQL container destroyed after job, guarded cleanup only on disposable instance. No remote database restore required.
PAID_API_BUDGET: 0; current assistant and one scoped GitHub Actions run only; additional executors prohibited. REPAIR_LIMIT: at most two evidence-producing repair cycles.
STOP_CONDITIONS: upstream SHA drift, unsupported artifact permissions or expiry, source hash mismatch, SQL E2E fail, remote connection need, paid services, any new business decision.
AUTHORIZATION_END: real-source transactional importer E2E receipt and checkpoint; STOP, future Neon TEST decision separate.


#### UALP-CAREER-KB-006 — transactional O*NET import real PostgreSQL E2E receipt (2026-11-18)

STATUS: **PASS**, exact tested commit `e15a6f17de92ab0a5af3f377c577b788d6470209`, GitHub run [44349260235](https://github.com/VahramSargsyan/ualp-app/actions/runs/44349260235), job `134960064293`; 2 pytest PASS on ephemeral PostgreSQL 18.
SOURCE_PLAN_SHA256: `78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`, original O*NET Database 31.0 artifact 14435511727/44322510909; 1 snapshot, 2 real US occupation versions, 10 skills, 2 scales, 40 requirements (39 OBSERVED, 1 SUPPRESSED/null) read back.
TRANSACTIONAL: three injected mid-operation failures leave 0 source rows; parallel first writes -> INSERTED + NOOP; re-run NOOP; existing altered row -> REJECTED not overwritten; remote DB fence DENIED; guarded empty-only rollback PASS; legacy 10-table digest unchanged `aba3cd983d6e99924c58a404924b60ccb87119c7215b25d4f4ea244d8114a251`.
EVIDENCE: GitHub artifact 14446618590 expires 2026-11-25 16:37 UTC. JSON ZIP SHA `ee5a257c69ef63fdbe0ad0981996ccdb988977e2808c3c86974028c21e334671`, CRC and receipt readback PASS. First run failed only test regex capitalization; one focused repair to test/CI comment -> final PASS.
NOT_RUN: Neon TEST migration, backup/restore real user data, authenticated Vercel/Android runtime, owner UAT, PROD. Neither code in owner PR #7 nor main changed; no hosted TEST URL for this isolated block.
NEXT_BOUNDARY: separately authorized Neon TEST backup+guarded migration+owner acceptance; STOP.
