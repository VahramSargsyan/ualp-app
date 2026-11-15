# UALP — Universal Assessment & Learning Platform

Product loop: Assessment → Profile → Career/Role Fit → Learning Path → Practice → Reassessment → Growth.

## Current PostgreSQL candidate

**Owner decision (2026-11-15): use a normal PostgreSQL database and free infrastructure, not Google Apps Script.**

This branch is a bounded private TEST implementation (not accepted into main or PROD).
- `webapp/main.py` — FastAPI server, PostgreSQL data access, 21-answer validation, server-only deterministic scores, atomic writes, idempotent retry.
- `webapp/index.html` — mobile-first Russian Work Values research pilot.
- `migrations/001_initial_postgres_test.sql` — additive schema for an empty independent TEST database.
- `tests/` — deterministic Python safety/scoring checks.
- `render.yaml` — free Python web service template (not yet deployed).
- `docs/build/UALP_MVP_001_BUILD_PACKET.md` — scope and gates.

Dedicated Neon Free TEST project: `ualp-postgres-test` (project `snowy-leaf-35157339`, database `ualp_test`). This is separate from VBOS and ЖЭК. Current import is **DRAFT Work Values only**: 21 questions, 5 options, 27 scales, 42 links, 27 rules. The source content was imported directly into private Neon TEST and **is not published in GitHub**.

There is no Apps Script, Sheets backend, external API or payment service in the candidate. Source `UALP_Project_v0.7.zip` remains an immutable provenance reference. No formal psychometric validation or public respondent use has been approved.

## Local code checks

```sh
pip install -r requirements-dev.txt
python -m compileall -q webapp
pytest -q
```

## Free TEST deployment boundary

A new Render Free Python web service may use this branch with `render.yaml`. Set `UALP_ENV=TEST`, `DATABASE_URL` from this new Neon project and a long random `UALP_ACCESS_KEY` as **private Render environment variables**, never in GitHub. Run `uvicorn webapp.main:app --host 0.0.0.0 --port $PORT`. The web service itself is not yet deployed.

**Access:** the service is internet-addressable but API requires the private TEST key; it is owner-only pilot behavior, not multi-user authentication. Do not send the key to anyone or enter third-party responses.

**Limitations:** Neon Free has monthly compute/storage quotas; Render Free cold-starts after idle and can exhaust workspace free hours/bandwidth. Free hosting is not a production availability guarantee.

## Safety and what is not ready

- No user logins/roles, automatic backups, consent retention/deletion controls, validated translations, career matching or IQ conversion.
- The source content and any responses/credentials must not be checked into this public repository.
- Never deploy into existing VBOS/ЖЭК/PROD databases; this is an isolated TEST.
- TEST web deployment and full HTTP → PostgreSQL integration have **NOT_RUN** status. No user-acceptance or PROD release claimed.
