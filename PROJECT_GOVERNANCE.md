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
- Deployment gates: local tests => isolated Neon TEST => exact Vercel Hobby Preview runtime => human acceptance. Vercel PROD is not authorized.

CURRENT_MODE: IMPLEMENT_FEATURE
CURRENT_CAPABILITY: UALP-MVP-008 / ANDROID_TEST_APK (candidate; owner explicitly requested installable app)
CURRENT_BOUNDARY: installable single-owner Android WebView TEST packaging on the exact existing Vercel Preview hostname. The existing FastAPI session, assessment data, unified history and drafts remain unchanged. Owner acceptance of MVP-006/007 remains pending.
TEST_DATABASE: Neon Free project snowy-leaf-35157339 / ualp_test
PROD: NOT_CONFIGURED / NOT_AUTHORIZED
TEST_APP: preceding private Vercel branch Preview (PR #6) stays available as baseline; MVP-006 is a distinct dependent TEST candidate branch, not main/PROD. No automatic deployment/promotion authorization beyond owner-only Preview. See latest Build Packet section and PR receipt for exact candidate/checks. The earlier Render Free shell remains superseded.

