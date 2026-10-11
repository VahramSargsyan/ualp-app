# UALP maintainer entrypoint

Universal baseline: **VAHRAM_APP_GOVERNANCE v1.1.0**.
Canonical source: `VahramSargsyan/vbos-app/docs/governance/VAHRAM_APP_UNIVERSAL_GOVERNANCE_v1.1.0.md`.
Bounded execution contract: `VahramSargsyan/vbos-app/docs/governance/BOUNDED_CHAT_WORK_CONTRACT_v1.1.0.md`.

Read `PROJECT_GOVERNANCE.md` before changes.

UALP is a new application, but its assessment content already has a canonical Google Sheets database. Do not duplicate the live item bank into this repository.

Core rules:
1. Select a workflow mode before edits.
2. No Codex/additional executors/paid APIs without explicit current permission.
3. Google Sheets is the canonical assessment-content database for the MVP.
4. This repository owns runtime code, schema contracts, tests, migration logic and documentation — not the live item bank.
5. Never commit assessment responses, personal profiles, OAuth state, tokens, Script Properties or private exports.
6. Do not expose objective answer keys, `isCorrect`, `scoreValue` or scoring internals to browser payloads.
7. Persisted schema/ID/relation changes require a migration plan and rollback after the first runtime schema is accepted.
8. Runtime writes go to a separate Runtime DB, not the canonical Assessment Library sheet.
9. Static/local tests are not Apps Script runtime proof.
10. Keep the first vertical slice bounded: one user -> one assessment run -> responses -> scale scores -> stored result.
