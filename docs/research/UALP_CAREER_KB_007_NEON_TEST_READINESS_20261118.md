# UALP-CAREER-KB-007 — Neon TEST release preparation checkpoint
Date: 2026-11-18
MODE: IMPLEMENT_FEATURE / GUARDED_TEST_MIGRATION_PREPARATION
STATUS: NEON_TEST_SCHEMA_APPLIED / LIVE_READBACK_PASS
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


## Exact execution receipt — Neon UALP TEST, 2026-11-18
**STATUS: NEON_TEST_SCHEMA_APPLIED / LIVE_READBACK_PASS**

### Source and test
- GitHub exact SQL source commit: `affa7e1334a412e2141bae2d1e8b69349b04551c`, file `docs/migration_candidates/UALP_CAREER_KB_007_NEON_TEST_SCHEMA_GUARDED.sql`, Git blob SHA `d1ed0224ce402f197ca88b8b2929b557b2bcc1be`.
- Seven `CREATE TABLE` definitions and the one index from Career KB 004 verified **textually identical** to original approved disposable schema body. The difference is the separate Neon TEST-only authorization gate.
- Owner authorized beginning the protected Neon TEST migration after the independently verified 006 real PostgreSQL E2E. Target: UALP-only Neon Free `ualp_test` database, current default branch `main` (this is UALP TEST, not PROD).
- TEST active before: 10 legacy base tables, 0 Career KB tables, `UALP-POSTGRES-TEST-v0.1`.
- Fresh copy-on-write backup branch: `ualp-career-kb-007-pre-migration-backup-20261118` with 10 tables. Table-by-table legacy row counts and content digests **10/10 MATCH** both just after copying and after hosted migration. The backup is retained, not merged and not modified.
- Dedicated rehearsal clone (derived from backup): `ualp-career-kb-007-schema-rehearsal-20261118`. Before authorization, exact `DO` gate rejected with SQLSTATE `P0001`; afterward, one Neon transaction installed 7 Career KB tables + index with zero legacy data changes.
- Postflight rehearsal clone: 17 tables, 7 Career KB, 10 legacy table digests identical to active TEST/backup; no Career KB source rows inserted.
- Active Neon TEST installation: **one successful atomic 12-statement transaction**, explicit session-only `ualp.career_neon_test_schema_gate=APPROVED_UALP_NEON_TEST_ADD_ONLY_007`, verified DB/role/schema, lock timeout, statement timeout, 7 CREATE TABLE and 1 CREATE INDEX. No DROP/DELETE/UPDATE/INSERT statements on user data.
- Active postflight: **17 total tables, 7 Career KB tables (all EMPTY)**. Exactly 10 original legacy row counts and content digests unchanged compared with the fresh backup.
- Active original aggregate rows: schema version 1, forms 2, items 81, options 10, scales 33, links 102, scoring rules 33, assessment runs 2, responses 81, saved scale scores 33. No personal content or credentials copied to GitHub.
- Active Career KB constraints: PostgreSQL catalog reports primary keys, source unique constraints, FKs, and CHECK constraints for the new tables; explicit source index installed. Legacy schema not altered.
- Branch schema diff against backup confirms additive new Career KB definitions only, consistent with exact source SQL.

### Security, recovery and remaining gate
- **No imported O*NET rows in Neon TEST yet.** Current 006 transactional importer explicitly permits localhost-only CI; its network restriction was NOT weakened and has not been used on Neon. Any hosted 40-row source import requires a newly guarded TEST-specific transfer/SQL adapter, direct source digest and separate readback gate.
- No PROD, GitHub main, PR #7, Vercel deployment, Android runtime, public career API, scoring or career-fit feature.
- Rollback for the schema: it is additive and empty. Do **not** run the 004 disposable-only DROP script on Neon. Retaining empty additive tables is the safest recovery until a specifically authorized cleanup. A separate restored-branch replacement requires explicit owner approval.
- **Backup copy/readback: PASS.** Actual destructive recovery replacing TEST from the backup: **NOT_RUN**. Do not represent matched branch readback as a completed recovery drill.
- New app TEST URL: **NOT_APPLICABLE**; existing owner Vercel Preview unchanged. End-to-end app/owner UAT is **NOT_RUN**.
- Free resources: one COW backup branch and one clone used, existing Free project, no paid API or new paid service; temporary rehearsal branch intentionally retained pending future authorized cleanup.
- NEXT_BOUNDARY: import only the 2 frozen O*NET technical pilot professions and 40 source measurements into the **7 existing empty Neon TEST tables** through a TEST-only allowlisted source importer with atomic/idempotent readback, not by bypassing the localhost-only CI writer. Confirm whether the technical pilot should be exposed to the product UI separately.
- AUTHORIZATION_END: guarded Neon TEST schema installation and postflight evidence, STOP.
