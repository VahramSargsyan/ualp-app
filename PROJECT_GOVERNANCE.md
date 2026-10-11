# UALP Project Governance

GOVERNANCE_VERSION: VAHRAM_APP_GOVERNANCE v1.1.0
CANONICAL_SOURCE: VahramSargsyan/vbos-app/docs/governance/VAHRAM_APP_UNIVERSAL_GOVERNANCE_v1.1.0.md
BOUNDED_CONTRACT: VahramSargsyan/vbos-app/docs/governance/BOUNDED_CHAT_WORK_CONTRACT_v1.1.0.md
LOCAL_PROFILE: STABLE_MAIN (initial default; no PROD path exists yet)
LAST_SYNC: 2026-10-11

## Local authority

- `docs/product/UALP_PRODUCT_BLUEPRINT.md`
- `docs/build/UALP_MVP_001_BUILD_PACKET.md`
- `docs/architecture/DATA_CONTRACT.md`
- `docs/architecture/ASSESSMENT_RUNTIME.md`

## Local P0 additions

- The canonical assessment item bank remains outside GitHub in the designated Google Sheet.
- Public repository visibility must never expose personal responses or private Google identifiers/config values unnecessarily.
- Objective assessment answer keys are server-only.
- Career matching is out of scope until the base assessment runtime persists deterministic results correctly.
- Employment/high-stakes use is not authorized by an exploratory pilot result.

## Current execution gate

CURRENT_MODE: BUILD_NEW_APP
CURRENT_CAPABILITY: UALP-MVP-001
CURRENT_BOUNDARY: Assessment runtime foundation only
PROD: NOT_CONFIGURED / NOT_AUTHORIZED
TEST: NOT_DEPLOYED
ACTIONS: STATIC_CI_ALLOWED; deployment workflow NOT_CONFIGURED
