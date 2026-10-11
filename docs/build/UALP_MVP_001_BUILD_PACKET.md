# UALP-MVP-001 Build Packet

CAPABILITY_ID: UALP-MVP-001
USER_RESULT: A user can load one configured assessment, answer every item, submit once, and receive a reproducible stored score result.
WORKFLOW_MODE: BUILD_NEW_APP
RISK_CLASS: L2 now; runtime schema acceptance becomes L3 if persisted contract changes after adoption.
BASE_COMMIT: EMPTY_REPO_BOOTSTRAP
OWNER_BRANCH: main for documentation/bootstrap; runtime work should move to a feature branch once remote access is available.
TEST_TARGET: Apps Script TEST deployment — NOT_CREATED.

SCOPE:
- Apps Script runtime foundation
- canonical content reader
- public-safe form payload
- deterministic server-side scoring core
- fresh runtime schema contract/installer
- idempotent run/submit design
- diagnostics and local deterministic tests
- GitHub Actions static CI for deterministic tests and Apps Script syntax

OUT_OF_SCOPE:
- career matching
- occupation ingestion
- learning engine
- authentication/roles beyond a development user identity
- production release
- public validation claims
- automatic deployment / release workflows

CANONICAL_SOURCE_OF_TRUTH:
- Assessment content: designated UALP Assessment Library Google Sheet
- Runtime records: separate Runtime DB Google Sheet

SCHEMA_IMPACT:
- Existing Assessment Library: none
- New Runtime DB: fresh schema only; no migration of existing user data

MIGRATION_PLAN: NOT_REQUIRED for first empty Runtime DB. Future changes to accepted runtime columns/semantics require versioned migration + rollback.

DEPENDENCIES:
- Google Apps Script
- Google Sheets service
- Script Properties for content/runtime spreadsheet IDs and environment

SHARED_HOTSPOTS:
- scoring contract
- form payload contract
- runtime persisted schema

ACCEPTANCE:
1. form loader never returns `isCorrect` or scoring values;
2. RIASEC SUM scoring deterministic;
3. Work Values MEAN scoring deterministic;
4. ICAR binary objective scoring deterministic;
5. incomplete required form rejected;
6. duplicate submit request is idempotent by clientRequestId;
7. runtime writes never touch Assessment Library;
8. diagnostics report missing config/sheets without mutating content DB.

ROLLBACK:
- no PROD exists;
- discard TEST Runtime DB and revert candidate commit.

REQUIRED_EVIDENCE:
- LOCAL_TESTED pure scoring/security tests
- CI_VALIDATED deterministic tests + Apps Script syntax once GitHub Actions is green
- STATIC_ONLY Apps Script runtime semantics until deployed
- TEST_RUNTIME_VERIFIED required before user acceptance of runtime

UNRESOLVED_DECISIONS: NONE for foundation block.
