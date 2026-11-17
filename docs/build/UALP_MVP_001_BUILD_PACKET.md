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
