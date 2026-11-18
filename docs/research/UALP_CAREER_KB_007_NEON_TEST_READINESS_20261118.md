# UALP-CAREER-KB-007 — Neon TEST release preparation checkpoint
Date: 2026-11-18
MODE: IMPLEMENT_FEATURE / GUARDED_TEST_MIGRATION_PREPARATION
STATUS: PREFLIGHT_PASS / BACKUP_READBACK_PASS / NEON_TEST_SCHEMA_NOT_APPLIED
BASE_GITHUB_COMMIT: c92bce785f3a66ff164ea89bd6be1ed768dda84b
GITHUB_BRANCH: feature/ualp-career-kb-neon-test-schema-guard
SOURCE: UALP Career KB-006 exact proven PostgreSQL 18 import commit e15a6f17de92ab0a5af3f377c577b788d6470209, run 44349260235 (2 PASS). Backward-compatible with existing UALP-MVP-001 SQL schema; no app/Neon writer integration.
OWNER: Vahram. USER_REQUEST: "Начнем" after separately identified guarded Neon TEST boundary. No PROD/main merge/PR #7 edits authorized.

## Live TEST preflight (Neon read-only)
- Existing Neon Free project for UALP verified; named DB `ualp_test`, postgres 18.7; default branch `main` is *TEST*, not PROD.
- Exactly 10 original UALP tables, `UALP-POSTGRES-TEST-v0.1` schema version, zero Career KB tables.
- Aggregate row counts (no user values exposed): schema version 1, forms 2, items 81, options 10, scales 33, links 102, scoring rules 33, assessment runs 2, responses 81, scale scores 33.
- **Fresh owner TEST backup branch created inside the same free Neon project**. A new branch containing the same `ualp_test` database and the same 10 tables is ready.
- **Backup readback:** row counts and content-equality digests for every one of the original 10 tables match the active TEST source **10/10** immediately after branching; no individual response rows or hashes are published.
- **Restore replacing owner TEST:** NOT_RUN / intentionally forbidden at preflight. A COW backup with matching readback is not a tested destructive restoration.
- Existing GitHub Draft PR #7 remains at its own source commit; this source-only block has no Vercel TEST release.
- Free plan capacity: branch copy, no paid service/API or manual paid snapshot. Avoid creating a billed snapshot.

## Known blocker and bounded fix
- Existing 004 candidate SQL explicitly guards `APPROVED_DISPOSABLE_TEST` and must never be re-used to migrate hosted Neon TEST.
- Existing 006 importer explicitly refuses non-local PostgreSQL, even a trusted Neon TEST DSN. Do not weaken that safe fence or smuggle Neon credentials into GitHub logs.
- **New 007 schema candidate** retains exactly the seven previously exercised PostgreSQL table definitions and one index; changes only the prefatory guard for exact database/role/schema and an additional approved session gate `APPROVED_UALP_NEON_TEST_ADD_ONLY_007`.
- The 007 SQL is under `docs/migration_candidates/` and is not automatically executed. Any source edits after verification invalidate the gate.
- The source-select, transactionally idempotent hosted import executor will require an independently guarded TEST-only transport or SQL adapter; the 006 local writer cannot be used as-is.

## Controlled migration acceptance sequence
1. Confirm owner TEST/source unchanged; ensure the fresh backup branch and 10-table checks still match current TEST before any hosted write. If active data changed after backup, create a fresh backup rather than using an old point.
2. Independently review the 007 exact-source SQL gate and seven-table DDL. Never use the 004 `APPROVED_DISPOSABLE_TEST` override on Neon.
3. Dry-run equivalent guarded 007 DDL against a disposable clone of TEST and verify that original 10 tables remain byte-for-byte consistent, zero existing assessment rows mutated, and 7 new empty Career KB tables exist. Verify the guard denies wrong databases/roles/unarmed sessions.
4. **Only with the exact separately approved migration action:** run the gated source on the active `ualp_test`, with direct unpooled DB/connector and a single atomic transaction, then confirm 17 expected tables and unchanged 10 legacy readback digests. Do not apply migration to PROD or any other projects.
5. Source import of 2 technical pilot professions, 40 source skill ratings (39 OBSERVED, 1 SUPPRESSED/null), must occur only through a separate authenticated TEST-only, exact-plan-hash guard that preserves 006's localhost deny rule.
6. For rollback: abort the transaction if migration not committed; once committed, **do not DROP populated tables**. Retain new empty schema or use a separately guarded rollback with known-empty tables and verified backup; a restore replacing a populated branch is destructive and needs explicit owner approval.

## STOP / remaining
- Primary TEST schema changes, import into Neon, restore replacement, public career APIs, Vercel deployment and user acceptance are all NOT_RUN.
- New candidate SQL has only static equivalence verification until it executes on a disposable PostgreSQL 18 test branch; do not claim hosted PG E2E from 006 applies to this new authorization header.
- User TEST is not a blank scratch space (2 completed assessment runs with associated responses and scores).
- Next gate: dry-run 007 candidate on an isolated Neon branch, prove tested restore/rollback; after exact-source approval decide whether to apply the migration and subsequently import public O*NET source data.
