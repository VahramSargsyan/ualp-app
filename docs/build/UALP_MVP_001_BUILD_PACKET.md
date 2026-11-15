# UALP-MVP-001 Build Packet — PostgreSQL private TEST revision

DECISION_SOURCE: Owner on 2026-11-15 explicitly rejected Apps Script and requested a normal database at zero cost. This change supersedes the earlier Apps Script technology choice for the NEW UALP implementation. Main remains unchanged until review.

CAPABILITY_ID: UALP-MVP-001
USER_RESULT: One owner completes a 21-item draft Work Values assessment on mobile or desktop; answers and reproducible 6 parent / 27 total scale scores persist atomically in PostgreSQL.
WORKFLOW_MODE: BUILD_NEW_APP
RISK_CLASS: L3 (new persisted data schema; isolated TEST only)
BASE_COMMIT: 2387d9759e834b42432fcfacf31a53215e4e11fc
OWNER_BRANCH: feature/ualp-mvp-001-postgres-test
TEST_TARGET: Neon Free project snowy-leaf-35157339 (ualp-postgres-test), database ualp_test; Render Free TEST after code readiness.
PROD: NOT_AUTHORIZED / NOT_CONFIGURED
PAID_API_BUDGET: 0
EXECUTOR_PERMISSION: current assistant only; no Codex.

CANONICAL_SOURCE_OF_TRUTH:
- Candidate assessment source v0.7 is a provenance reference, not a silently updated live dependency. After approved one-time source-reviewed import, PostgreSQL holds versioned assessment content and runtime state in separated tables.
- Google Sheets/Apps Script must not be a production or runtime dependency. Never upload unreviewed item bank contents, objective answer keys, participant responses, credentials or secrets to public GitHub.

SCOPE: Standalone Python/FastAPI browser interface, PostgreSQL schema, initial development-only Work Values pilot, server-side scoring, strict 21-answer validation, explicit consent, atomic response/score commit, idempotency, TEST authentication, tests and free-hosting configuration.
OUT_OF_SCOPE: 13 remaining modules, live employer/hiring decisions, public respondent signup, role matching, learning engine, PROD, payments and paid services.
MODULES: app/, tests/, migrations/, render.yaml, requirements.txt, docs/.
SHARED_HOTSPOTS: imported canonical IDs, scoring algorithm, database schema version, source-license/translation status, private data boundary.
DO_NOT_TOUCH: VBOS, ЖЭК, existing Neon proud-hat project, any production app, canonical assessment workbook/source.

SCHEMA_IMPACT: Dedicated NEW PostgreSQL database only, no existing user data migrated. New ualp_ namespace tables; no destructive migration. Once accepted, any change requires versioned MIGRATION_PLAN and rollback.
MIGRATION_PLAN: One-time, content-reviewed import from v0.7 source into new isolated tables; source snapshot remains immutable. Never auto-reset or overwrite saved answer data. Initial empty database install is additive.
DEPENDENCIES: Python 3.11+, FastAPI, SQLAlchemy, psycopg 3, Neon Free PostgreSQL 18, Render Free if workspace authorization permits.
ACCEPTANCE: 21 questions/5 options; scoring 0–4 raw MEAN by 6 domains and 21 facets; 21 responses and 27 scores committed per run; duplicate retry creates no second run; conflicting retry rejected; incomplete/invalid content rejected; private TEST gate; accessible mobile page; live Neon readback.
REQUIRED_EVIDENCE: local deterministic tests, actual PostgreSQL TEST integration, server health, deployed TEST smoke, exact commit/URL, privacy and duplicate retry negative tests.
ROLLBACK: Stop isolated Render TEST; preserve DB before schema changes; fresh empty TEST can be discarded separately if authorized; revert feature branch without altering main.
UNRESOLVED_DECISIONS: Source workbook rights and public reuse, future user account model, formal content validation and production privacy policy. These block publication/hiring, not a private single-owner pilot.
AUTHORIZATION_END: report this bounded block; no PROD or next feature implied.
