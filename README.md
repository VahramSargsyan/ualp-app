# UALP — Universal Assessment & Learning Platform

UALP is designed around a closed growth loop:

`Assessment -> Profile -> Career/Role Fit -> Learning Path -> Practice -> Reassessment -> Growth`

## Current state

This repository is the runtime/code home for the UALP MVP. The canonical assessment-content database is a separate Google Sheet and is intentionally **not copied into this repository**.

Initial assessment battery:
- RIASEC vocational interests — 60-item digital form
- Work Values — 21-item pilot
- Cognitive Core — ICAR-16 anchor

The first runtime milestone is deliberately smaller than the full product:

`one user -> one assessment run -> responses -> deterministic scale scores -> stored result`

Career matching, learning assignment and reassessment feedback are later bounded capabilities.

## Data boundary

Repository:
- Apps Script runtime source
- HTML UI
- schema contracts
- migrations/installers
- deterministic tests
- architecture/product docs

Google Sheets:
- canonical assessment content
- separate runtime database for users/runs/responses/scores

Never commit:
- user responses or profiles
- OAuth credentials / `.clasprc.json`
- Script Properties
- private exports
- copied objective answer keys in client code

## Status

Bootstrap line: `0.1.0-dev`
Runtime candidate: `feature/ualp-mvp-001-assessment-runtime` (not merged)
Modules: `apps-script/Code.gs`, `apps-script/Index.html`, `apps-script/appsscript.json`
Verification: `npm test` (Node VM + mocked Google Apps Script services)
Installation and real acceptance: `docs/build/UALP_MVP_001_INSTALL_AND_TEST.md`
TEST deployment: NOT_RUN
PROD: NOT_CONFIGURED

**Security:** public repository does not mean public assessment service. The Apps Script web app MUST remain owner-only. Store sheet IDs and owner email in Script Properties, not GitHub. Never upload the source workbook, objective answer keys or personal assessment answers as repository data.

**Technology boundary:** UALP-MVP-001 uses the already adopted Google Sheets Assessment Library + separate Google Sheets Runtime DB. An earlier standalone Python/SQL prototype is not the authority for this repository; adopting PostgreSQL requires a separately approved data-contract change.
