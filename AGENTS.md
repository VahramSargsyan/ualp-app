# UALP maintainer entrypoint — PostgreSQL candidate

Read PROJECT_GOVERNANCE.md and the accepted Universal Governance v1.1.0 and BOUNDED_CHAT_WORK_CONTRACT v1.1.0 from VahramSargsyan/vbos-app/main before edits.

Current owner decision 2026-11-15: a normal PostgreSQL database and standalone web app, zero paid cost; NO Apps Script or Google Sheets dependency. This project is in a non-merged feature branch, not PROD.

Architecture: one TEST-only Python/FastAPI application, one isolated Neon Free PostgreSQL project for runtime and approved versioned assessment content, Render Free only when workspace/configuration gates allow. The original attached UALP v0.7 workbook is source/reference; never commit private or unreviewed content to public GitHub.

Never copy keys, secrets, access tokens, DB URLs, participant answers, profiles, objective item keys or private exports into source control. No Codex/additional executors/paid APIs without explicit permission. Testing one form != validated vocational guidance. Preserve source IDs, versions and statuses. Keep initial scope one user, one assessment, full response set, deterministic scores, idempotent persisted result. No PROD launch.
