# UALP Project Governance — PostgreSQL candidate overlay

GOVERNANCE_VERSION: VAHRAM_APP_GOVERNANCE v1.1.0
CANONICAL_SOURCE: VahramSargsyan/vbos-app/docs/governance/VAHRAM_APP_UNIVERSAL_GOVERNANCE_v1.1.0.md
BOUNDED_CONTRACT: VahramSargsyan/vbos-app/docs/governance/BOUNDED_CHAT_WORK_CONTRACT_v1.1.0.md
LOCAL_PROFILE: STABLE_MAIN; proposed runtime remains in a feature branch.
LAST_DECISION: 2026-11-15 — owner explicitly rejected Apps Script and selected normal database at zero cost.

## Local authority
- docs/product/UALP_PRODUCT_BLUEPRINT.md
- docs/build/UALP_MVP_001_BUILD_PACKET.md
- docs/architecture/DATA_CONTRACT.md
- docs/architecture/ASSESSMENT_RUNTIME.md

## P0
- Only FREE infrastructure; no paid API/credits.
- No Google Apps Script or Google Sheets runtime in the UALP candidate.
- Public repo: no credentials, DB URLs, private IDs, respondent records, source item bank or unreleased scoring keys.
- A new independent Neon PostgreSQL TEST project; do not touch VBOS/ЖЭК/PROD DB.
- Draft instruments are exploratory, not validated for high-stakes/hiring decisions.
- Atomic persisted answers/scores, reproducible versioned scoring and retry idempotency.
- Schema migration+rollback for later changes, no resetting real user data.
- No PROD or public respondent access without separate explicit authorization.
- Deployment gates: local tests => real Neon TEST => exact Render TEST => human acceptance.

CURRENT_MODE: BUILD_NEW_APP
CURRENT_CAPABILITY: UALP-MVP-001
CURRENT_BOUNDARY: one owner + one Work Values form + persisted score
TEST_DATABASE: Neon Free project snowy-leaf-35157339 / ualp_test
PROD: NOT_CONFIGURED / NOT_AUTHORIZED
TEST_APP: NOT_DEPLOYED
