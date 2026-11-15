# UALP-MVP-001 — TEST installation and evidence

CAPABILITY_ID: UALP-MVP-001
WORKFLOW_MODE: BUILD_NEW_APP
RISK_CLASS: L2 business feature (unaccepted, fresh runtime schema)
BASE_COMMIT: 2387d9759e834b42432fcfacf31a53215e4e11fc
OWNER_BRANCH: feature/ualp-mvp-001-assessment-runtime
TEST_TARGET: Owner-only Google Apps Script TEST; NOT_DEPLOYED
PROD: NOT_CONFIGURED / NOT_AUTHORIZED
PAID_API_BUDGET: 0; no Codex or additional executors used
TEST_LEVEL: CI deterministic GAS mock; Apps Script runtime NOT_RUN

## Contract and data authority

Implementation follows UALP_MVP_001_BUILD_PACKET.md and does not replace it.

- The Assessment Library Google Sheet remains canonical for items, translations, response options, score links, scoring rules and provenance.
- A separate Runtime DB Google Sheet stores Users, AssessmentRuns, Responses, ScaleScores, RequestDedup, EntityRowIndex, ErrorLog and RuntimeSchema.
- The repository is public, but the TEST web app MUST be accessible only by the owner.
- No content bank, credentials, private spreadsheet identifiers, user responses or profiles may be committed.
- Career matching, jobs, learning paths, production, public psychometric claims and PostgreSQL integration are out of scope.
- The client receives only questions and display option IDs, never answer keys or scoring weights.

## First-time setup — owner-only TEST

Never execute the installer on existing production spreadsheets.

1. Identify the canonical UALP Assessment Library Google Sheet with the sheets and headers from docs/architecture/DATA_CONTRACT.md. The uploaded XLSX is a design snapshot, not proof of a live connected Google Sheet.
2. Create a NEW EMPTY TEST spreadsheet for Runtime DB; do not reuse the content library or VBOS/ЖЭК databases.
3. Create an independent Google Apps Script TEST project. Copy apps-script/Code.gs as Code.gs and apps-script/Index.html as Index.html. Use apps-script/appsscript.json as the manifest.
4. In Apps Script Script Properties only (NEVER in GitHub), set:

   | Property | Value |
   |---|---|
   | UALP_ENV | TEST |
   | UALP_OWNER_EMAIL | Owner's Google account email |
   | UALP_DEV_USER_ID | Stable private dev user ID |
   | UALP_ENABLED_FORM_KEY | UALP_WV21_RU_LIKERT |
   | UALP_ASSESSMENT_LIBRARY_ID | Canonical library spreadsheet ID |
   | UALP_RUNTIME_DB_ID | New TEST runtime spreadsheet ID |

5. As owner, run ualpDiagnostics() to check configuration and show missing Runtime DB tables. Then run ualpTestRuntimeInstaller() once, confirming 8 runtime tables. The installer preflights existing headers and never changes the canonical content DB.
6. Deploy as Web app: execute as owner, access Only myself. Never choose Anyone. If Session.getActiveUser().getEmail() is blank or differs from UALP_OWNER_EMAIL the app denies access; do not bypass this gate.
7. Record exact TEST URL, source commit, Runtime DB schema marker and active library version before acceptance.

## Real TEST acceptance scenario (NOT_RUN)

1. Open on phone as owner: Russian pilot notice visible, start disabled without explicit consent.
2. Start Work Values: exactly 21 items, five choices each, navigation working.
3. Required unanswered items and invalid option IDs are rejected; no partial run is committed as completed.
4. Complete all 21 items: expect one COMPLETED AssessmentRuns record, 21 Responses rows, and with current v0.7 canonical rules 27 ScaleScores (six work-value domains plus 21 facets).
5. Retry same clientRequestId: same response/result, no duplicate rows. Confirm the Assessment Library remains unchanged.
6. Run diagnostics: no runtime header drift.
7. Verify user without owner identity is rejected. Keep deployment private.

## Completed and not completed

- CI deterministic test: syntax, RIASEC SUM, Work Values MEAN, simulated ICAR correct/incorrect, safe payload, negative input, draft/blocked key protection, idempotent submit, and no write to Assessment Library.
- REAL Apps Script/Google Sheets runtime: NOT_RUN.
- Owner identity in live Apps Script web app: NOT_RUN.
- Mobile browser UX, sheet sharing, performance and exact live content readback: NOT_RUN.
- ICAR-16 is not enabled for runtime until source key/visual asset checks are approved.
- Work Values draft Russian items are not psychometrically validated. Pilot results cannot be used for hiring or high-stakes assessment.

## Rollback / residual risk

Main and existing production sheets remain unchanged. Rollback: close TEST deployment, archive/discard only the new isolated TEST runtime DB after checking retention needs, revert/delete the feature branch. Never delete or modify the canonical Assessment Library.

Risks: real content sheet ID/location and sharing are not verified, true Apps Script behavior remains untested, ScriptProperties must remain private, and multi-sheet writes are recoverable by idempotent retry but are not database-atomic transactions.

Next bounded step: owner-only Apps Script TEST install, live readback and exact deploy receipt. Separate permission required for PROD or a database-platform migration.
