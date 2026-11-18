# UALP-CAREER-KB-006 — frozen-source transactional writer E2E

STATUS: PREPARED / TEST_RUN_PENDING
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
