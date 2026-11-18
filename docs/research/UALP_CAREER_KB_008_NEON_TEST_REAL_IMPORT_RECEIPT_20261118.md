# UALP-CAREER-KB-008 — exact source-backed Neon TEST import receipt

Date: 2026-11-18
MODE: IMPLEMENT_FEATURE / GUARDED_NEON_TEST_IMPORT
STATUS: REAL_NEON_TEST_ONET31_IMPORT_PASS / IDPOTENT_REPLAY_NOOP
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


## Final exact execution evidence — 2026-11-18
**STATUS: NEON_TEST_REAL_ONET31_SOURCE_IMPORT_PASS / BACKUP_AND_LEGACY_PRESERVED**

### Proven source and build
- Exact, independently read-back source code commit: `26248f300c614be0d979bb6f3c067b1969d8a907` (GitHub branch `feature/ualp-career-kb-008-neon-test-import`).
- `career_kb/neon_test_import_adapter.py` Git blob SHA: `2a853de972f5fc13f5b90dffe37e686f4fc1d0f1`; unit tests Git blob SHA `db325a62e33802414cbd65205ef85f7de8e10bee`.
- Original source ZIP SHA256 `4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d` and all three O*NET 31.0 CSV hashes validated locally; source plan SHA256 `78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`.
- Generated transaction statements: 19. Source data were transferred directly through the authorised Neon SQL connector; no raw CSV/plan/SQL payload committed to public GitHub, no DB URL or password embedded in the repository.
- Local targeted Python pytest: **13 PASS / 0 FAIL**; compileall PASS. No new GitHub Actions run (source code and DB verified via connector instead).

### Isolated Neon PostgreSQL 18 E2E (the already-existing 007 rehearsal clone)
- Clone before: 17 total tables / seven empty Career KB tables; original 10 UALP legacy tables unchanged.
- Unarmed separate 008 gate: **DENIED** with SQLSTATE `P0001`.
- Deliberately injected errors after snapshots insertion and after all requirements insertion: both transactions **ROLLED BACK**, post-error source row counts zero.
- Exact original 19-step import transaction: `INSERTED`; all seven typed table payloads compared against actual SQL rows within transaction; `EXACT_SOURCE_READBACK_PASS`.
- Identical 19-step replay: `NOOP` with exact readback PASS.
- Conflict test: within one aborting clone-only transaction, attempted a changed original requirement numeric value; full-table source check **REJECTED**, transaction rolled back, original 3.8800 value preserved. The existing localhost-only 006 CI writer remains completely unchanged.
- Legacy original data hash/readback: **10/10 identical** across rehearsal, active TEST and 007 backup before release.

### Fresh pre-import protected evidence copy
- New copy-on-write Neon branch `ualp-career-kb-008-pre-import-backup-20261118`, branched from active UALP TEST just before writing.
- `ualp_test` database on this branch has 17 tables, seven Career KB tables empty; user data and assessment results present.
- 10/10 legacy table counts and content equality digests match the active TEST immediately before the source import.
- The branch remains available and is not modified or renamed. An actual destructive restoration/swap was **NOT_RUN**.

### Active Neon TEST import
- Exact destination existing UALP Free Neon project, database `ualp_test`, default Neon `main` branch (which is **TEST**, not PROD); logged-in role `ualp_test_owner`, PostgreSQL 18.
- Preflight: 17 tables / seven Career KB empty, 2 assessments, 81 saved responses, 33 saved scale scores. Fresh backup ready, exact expected GitHub source and unchanged owner PR #7 head.
- One **atomic 19-step SQL transaction** through Neon `run_sql_transaction` with session-local exact source SHA and TEST-only gate. Decision `INSERTED`; independent in-transaction seven-table typed full-content readback `EXACT_SOURCE_READBACK_PASS`.
- Results: one source snapshot, 2 occupations, 2 occupation versions, 10 competencies, 10 competency versions, 2 scales, **40** real public O*NET occupational ratings — **39 OBSERVED, 1 SUPPRESSED/null**.
- **Independent postflight** (separate read-only SQL after commit): all **7/7 Career KB table row counts and content digests identical** to the validated isolated Neon rehearsal, including metadata, provenance and numeric values.
- **Independent legacy preservation**: all **10/10** original UALP table counts and content digests identical to fresh 008 preimport backup: catalog and 2 completed assessment runs / 81 responses / 33 saved scores unchanged.
- Fresh backup's Career KB seven tables confirmed still **EMPTY** after release, demonstrating it remains an unmodified pre-import recovery point.
- **Idempotent replay on active Neon TEST**: complete exact 19-step transaction returns `NOOP`, source full-readback still PASS; no duplicates or overwritten values.
- No SQL migration, table DROP, legacy UPDATE, schema rewrite, app rollout, user responses export or PROD deployment in this block.

### Recovery, limitations, next boundary
- Transactional failures before commit revert automatically. After this successful import the Career KB tables are intentionally populated. **Do not run the 004 disposable-only DROP SQL on Neon**, and do not overwrite/swap restored branches without explicit owner approval. Pre-import backup available for a separately authorized recovery decision.
- This is a database/source import; it does not prove the user-facing FastAPI/Vercel runtime, Android, career matching, labor demand or user UAT. No new hosted TEST URL for Career KB. Existing Draft PR #7 and GitHub main remain unchanged.
- The data reflect U.S. O*NET occupational descriptions and its CC BY 4.0 license, **not a user's measured competence**.
- NOT_RUN: destructive branch restore, public API/role UI, authenticated Vercel/Android UAT, PROD release.
- No paid APIs/services, no additional executor/Codex or GitHub Actions.
- **AUTHORIZATION_END: verified Career KB 008 Neon TEST import; STOP.** Future read-only API/owner UI integration and career-suitability algorithms require their own business/engineering decision.
