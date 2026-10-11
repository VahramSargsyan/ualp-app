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
TEST deployment: NOT_RUN
PROD: NOT_CONFIGURED
