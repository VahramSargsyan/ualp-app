# UALP-CAREER-KB-006 — frozen-source transactional writer E2E

STATUS: REAL_O_NET31_PLAN_TRANSACTIONAL_IMPORT_PASS
DATE: 2026-11-18
BASE: 7d18fd3f0042de9ec57041dcdb14a068afd43bbb
OWNER_BRANCH: feature/ualp-career-kb-transactional-import-once
PRIMARY_MODE: IMPLEMENT_FEATURE (test-only writer, no application runtime wiring)
TEST_ENV: GitHub-hosted disposable PostgreSQL 18 service, 127.0.0.1:5432/ualp_ci

## Objective

Implement a self-contained Python writer that consumes **only** the exact,
previously source-verified O*NET Database 31.0 plan with SHA256
`78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`.
The writer refuses all remote/Neon database connection parameters and never
imports human respondent data or computes career fit, qualifications or skill evidence.

The entire source ZIP remains in the prior short-lived GitHub artifact
`14435511727`, workflow run `44322510909`; the new CI job **retrieves** it using
scoped read-only Actions token, validates its three locked CSVs and exact
receipt via the existing offline reader and import planner; it never commits
real CSV or raw plan to this public repository.

## Gates and invariants

- Explicit CI mode + exact `127.0.0.1` service target and `postgres` account.
- Exactly one snapshot ID, version 31.0, 2 US occupation codes, 10 skills, 2 scales, 40 source rows (39 observed, 1 suppressed/null).
- Exact source manifest, CSV SHA256 and original acquisition timestamp and commit.
- SQL files from stage 004: existing additive DDL candidate and guarded empty-only rollback; neither modified.
- Transaction-level advisory lock serializes first imports and replays.
- Source mismatch / missing table / PK collision / changed prior record / partial source snapshot => **FAIL CLOSED**, not overwrite.
- Injected faults after multiple insertion stages must roll back every Career KB row; existing AssessmentRun/Response/Score and schema unchanged.
- A second exactly equivalent import returns `NOOP`, not a new source version.
- Repeated concurrent import must produce exactly one `INSERTED` and one `NOOP`.
- Rollback of nonempty tables remains refused; after explicit **disposable-test-only** cleanup, guarded rollback can remove 7 tables while preserving 10 base tables.

## Test and migration boundary

REQUIRED: log of actual GitHub Actions job, SHA and artifact receipt, total counts, 3 injected transaction aborts, exact source, concurrency, corruption checks, legacy baseline digest before/after, and rollback readback. A green CI check without database evidence does not count.

NOT AUTHORIZED: any Neon TEST schema/data mutation, PROD, Vercel/Android deployment, main merge, new career service endpoint or scoring/matching logic, premium APIs or additional Codex executor. Real O*NET occupation records are **US-only** and do not establish Armenian job demand.

Rollback of this scope: leave branch unmerged / revert code-only commit. CI PostgreSQL container is deleted after the job. A later hosted Neon TEST migration needs a separately approved plan, backup, exact verified commit and owner acceptance.


## Actual test execution and immutable readback — PASS

- **Final exact E2E source commit:** `e15a6f17de92ab0a5af3f377c577b788d6470209`.
- **Successful GitHub Actions run:** [44349260235](https://github.com/VahramSargsyan/ualp-app/actions/runs/44349260235), job `134960064293`, `SUCCESS`; PostgreSQL 18 ephemeral service, target `127.0.0.1:5432/ualp_ci`.
- **Test result:** `2 passed in 0.34s`, source-plan generation and checksum validation PASS; `REAL_DISPOSABLE_POSTGRESQL_18_E2E`.
- **Exact source plan SHA256:** `78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`. Downloaded prior official 31.0 artifact 14435511727 from run 44322510909; exact source plan regenerated, no full raw CSV files committed.
- **Database readback:** 1 source snapshot, 2 stable occupation IDs + 2 versions, 10 competencies + 10 versions, 2 explicit scales, **40 real O*NET requirements** including 39 `OBSERVED` and 1 `SUPPRESSED` with `NULL`. All seven source tables verified against frozen plan; not user skill evidence or career fit.
- **Three atomic rollbacks:** injected errors after `snapshots`, `occupation_versions`, and `requirements`, each left **zero** new Career KB rows.
- **Concurrency + retry:** 2 simultaneous initial imports yielded exactly `INSERTED` and `NOOP`; subsequent exact replay yielded `NOOP`.
- **Existing data conflict:** altered stored requirement value correctly refused without rewriting. Restored original source-backed value within disposable test, then exact replay `NOOP`.
- **P0 network fence:** remote DB URL rejected before connection; source hash/tampering/foreign fields rejected in source-validation tests.
- **Rollback:** unauthorized and populated-table rollback refused; after deleting only disposable rows in reverse FK order, guarded rollback removed 7 Career KB tables. All **10** original assessment tables retained their synthetic sample rows unchanged.
- **Legacy digest before/after:** `aba3cd983d6e99924c58a404924b60ccb87119c7215b25d4f4ea244d8114a251`.
- **Receipt artifact:** [GitHub artifact 14446618590](https://github.com/VahramSargsyan/ualp-app/actions/runs/44349260235/artifacts/14446618590), name `ualp-career-kb-006-transactional-import-e2e-receipt`, expires **2026-11-25 16:37 UTC**. Downloaded ZIP `SHA256=ee5a257c69ef63fdbe0ad0981996ccdb988977e2808c3c86974028c21e334671`; independent ZIP CRC/JSON readback PASS.
- **One repair cycle:** initial run [44348632557](https://github.com/VahramSargsyan/ualp-app/actions/runs/44348632557) failed on a case-sensitive pytest regex check (`only` vs `Only`) after successful source import, atomic fault tests, concurrency and conflict detection. Only test expectation and non-functional workflow comment changed; **writer, source hashes, schema, SQL, CI database target unchanged**. Final run PASS.
- **Code changes:** `career_kb/transactional_import.py`, `tests/test_career_kb_transactional_import.py` and one path/branch-scoped workflow only; this receipt and Build Packet appended afterward.
- **NOT_RUN:** hosted Neon TEST migration or real user data backup/restore; Vercel/Android authenticated runtime; owner UAT, PROD; no main/PR #7 merge. There is **no new hosted TEST URL** from this isolated source-only test.
- **Rollback:** revert this isolated GitHub branch. CI service was ephemeral and removed after the job; no remote DB or PROD rollback.
- **NEXT_BOUNDARY:** a separately authorized guarded Neon TEST migration release, only after current TEST checkpoint / backup and verified restore, actual schema state and owner consent. No automatic promotion.
