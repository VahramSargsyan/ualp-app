# UALP-CAREER-KB-008 — exact source-backed Neon TEST import receipt

Date: 2026-11-18
MODE: IMPLEMENT_FEATURE / GUARDED_NEON_TEST_IMPORT
STATUS: SOURCE_VERIFIED / ADAPTER_LOCAL_TEST_13_PASS / NEON_CLONE_AND_ACTIVE_TEST_PENDING
SOURCE_CHECKPOINT: GitHub branch `feature/ualp-career-kb-neon-test-schema-guard`, commit `1aecc24f7fb97b3702ed49fd3473e2f1f2ea8052`.
OWNER_AUTHORIZATION: owner's “Начни” responding to the specific next bounded block “защищённый импорт двух технических пилотных профессий и 40 требований ... в уже созданные таблицы”.

## Scope, immutable source, TEST destination
- Official O*NET Database 31.0 raw archive acquired from www.onetcenter.org in run 44322510909. ZIP SHA256 `4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d`; CRC PASS; all three individual CSV SHA256 match source lock.
- Frozen two-role import JSON plan SHA256 `78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`; generated from official CSVs with acquisition receipt. This is the *logical plan hash*, not a claim about the bytewise pretty-printed JSON file hash.
- UALP Free Neon project `snowy-leaf-35157339`, database `ualp_test`, PostgreSQL 18.7. Neon `main` is owner TEST, NOT PROD.
- Existing 10 legacy tables and 7 empty Career KB tables from approved schema 007. Prior receipt 007 confirmed unchanged legacy 10/10 and kept a source backup branch and schema rehearsal branch.
- This block must not alter any assessment answer, score, identity, or original schema, PR #7, GitHub main, Vercel or Android.

## New guarded adapter
- `career_kb/neon_test_import_adapter.py` generates exactly 19 SQL operations for **one** atomic `run_sql_transaction` on the exact UALP Neon TEST branch. It does not connect to Postgres, bypass/reconfigure the 006 localhost-only CI writer, or edit SQL schema 007.
- In-process original 006 `validate_frozen_plan`, source ZIP SHA/CRC, all original file hashes and acquisition receipt are revalidated before SQL generation. The exact 2 occupations, 10 skill categories, 2 scales, 40 original skill measurements are not widened.
- SQL uses session-local lock and timeout, advisory transaction lock, a separate `APPROVED_UALP_NEON_TEST_IMPORT_EXACT_008` gate, exact database/role/schema/version/snapshot hash allowlist, and temporary JSONB payload that disappears on commit. No DROP/DELETE/TRUNCATE/UPDATE on TEST.
- The transaction rejects partial/new source snapshots, uses `ON CONFLICT DO NOTHING`, and compares **each actual row/column of all seven source tables** with the frozen typed payload. Full exact replay is NOOP, any divergent stored row is fail-closed with the whole transaction rolled back.
- Expected source rows: 1 snapshot, 2 occupations, 2 occupation versions, 10 competencies, 10 competency versions, 2 scales, 40 requirements (39 OBSERVED, 1 SUPPRESSED with NULL). These are descriptive U.S. occupation skills, **not learner skill measurement or Armenian local labor demand**.
- Before active TEST write: rehearse on the existing isolated Neon schema clone. Prove unarmed gate refusal, mid-transaction failure rollback, success + bytewise complete source readback, exact replay NOOP, conflict rejection, and 10/10 legacy data conservation. Recheck active TEST and pre-import backup just before actual change.

## Checks and safety boundary
- LOCAL: 13 targeted Python unit tests PASS, including damaged ZIP, altered plan/field/digest, seven-table match and deny-list checks. No local PostgreSQL service.
- PENDING: actual Neon clone PostgreSQL 18 E2E, targeted negative tests, exact Neon TEST import, postflight row/hash readback and legacy table preservation. Do not mark these PASS from static tests alone.
- BACKUP: preserve immutable pre-import Neon branch separate from 007 baseline; never replace active branch or exercise destructive restore during this block.
- ROLLBACK: transaction abort before commit; after successful additive import, preserve immutable snapshot and separate backup. Any explicit removal of populated tables requires separately reviewed guarded row-level rollback with dependency audit and explicit owner approval. Original disposable-only DROP SQL is forbidden in Neon TEST.
- NOT_RUN: Vercel/Android runtime, owner UAT, public API exposure, PROD, GitHub main/PR #7, destructive TEST branch restore or migration to another database.
- COST: Neon Free and existing connectors only, zero paid API, no Codex/subagents, no GitHub Actions required.
- STOP after import verification and final GitHub receipt; any unexpected target, plan, or conflict is a hard blocker.
