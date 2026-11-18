# UALP-CAREER-KB-005 — Disposable PostgreSQL DDL and rollback rehearsal

DATE: 2026-11-18
CAPABILITY_ID: UALP-CAREER-KB-005 / DISPOSABLE_POSTGRES_SCHEMA_ROLLBACK_TEST
STATUS: PENDING_GITHUB_ACTIONS_RUNTIME_CHECK
BASE_COMMIT: `c1d68bcd5ced1c739651169df48f2ca4c9866c96`
OWNER_BRANCH: `feature/ualp-career-kb-postgres-rehearsal-once`
MODE: STRESS_TEST_ONLY (bounded functional integration rehearsal) — no persistent repo production edits or Neon writes
RISK: L3 — schema creation/removal confined to a disposable PostgreSQL 18 service.

## Scope and live data firewall

Only CI service container `postgres:18`, localhost `127.0.0.1:5432`, DB `ualp_ci`, synthetic assessment and Career KB rows. No Neon host, credentials, DB connection, public service, Render or Vercel. PostgreSQL is destroyed at end of the one-shot GitHub Actions job. The existing `migrations/001_initial_postgres_test.sql` and two unaltered SQL candidate files are read by the Python test from the exact source commit.

A gated schema execution *in this disposable DB only* is authorized by the user request to start the next ephemeral PostgreSQL rehearsal. **No permission for Neon TEST schema migration or launch** is inferred. PR #7 and owner's UAT candidate are not touched. This is not a production/TEST release.

## Expected checks

1. Verify localhost-only connection, PostgreSQL 18, freshly empty public schema.
2. Install existing base assessment schema unchanged and seed one fully synthetic completed run, response and raw score.
3. Record SHA256 of all 10 original table contents and row counts.
4. Attempt the proposed Career KB DDL without its session gate: MUST REJECT, no partial table creation.
5. Apply guarded candidate DDL once: 7 new tables, no changes to 10 legacy tables.
6. Reapply DDL: MUST REJECT without overwriting data or partially mutating schema.
7. Attempt Career KB rollback without its independent session gate: MUST REJECT.
8. Seed 1 synthetic source snapshot, 2 synthetic roles, 2 versions, 10 skills, 10 versions, 2 scales and 40 synthetic requirements (39 observed, 1 suppressed/null).
9. Verify real FK, check and unique constraints reject orphan skill, out-of-range number, observed/null, suppressed/zero, wrong scale bounds, duplicate source record, cross-snapshot relationship and deleting referenced snapshot.
10. Attempt gated rollback while tables contain data: MUST REJECT. Verify 40 requirements survive.
11. Clean up data explicitly in FK-safe order within the **disposable** database only; rollback guarded empty schema: expect 7 tables removed.
12. Verify the exact original 10 tables and their row-count and SHA256 baseline are unchanged.

## CI plan and evidence

Workflow: `.github/workflows/ualp-career-kb-postgres-rehearsal-once.yml`, `on: push` restricted to its exact branch **and this one workflow path**. One runner, no schedule or manual repeated trigger, no alternate paid services. Base deps `requirements-dev.txt` include psycopg3. Test source: `tests/test_career_kb_pg_rehearsal.py`. Expected run receipt artifact `ualp-career-kb-005-disposable-pg-receipt` (7-day retention) with sanitized JSON containing no connection secret or respondent records.

Only job logs and the resulting receipt may certify PostgreSQL runtime. YAML parse, Python syntax and successful Git push do **not** certify real E2E. On any failure, inspect the exact run and use no more than two evidence-based focused repair attempts; no repeat-run storms. Preserve precise failure details if blocked.

Potential runtime failure is NOT_RUN until the GitHub Actions run finishes. Local container has no PostgreSQL binaries/Docker and has no psycopg, so local execution was not attempted against any database.

## Rollback and future boundary

The CI service is disposable. Revert this isolated branch to delete the test harness. The SQL rollback candidate refuses nonempty tables and must never be used on populated Neon. There is no actual backup of real Neon data, no migration receipts for Neon and no target TEST installation. Successful disposable rehearsal allows a **separate** planning/approval decision for a real Neon migration with backup/restore and owner acceptance, not automatic deployment.
