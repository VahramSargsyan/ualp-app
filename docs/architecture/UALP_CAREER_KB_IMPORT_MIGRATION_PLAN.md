# UALP-CAREER-KB-004 — safe PostgreSQL import design, not execution

**Date:** 2026-11-18  
**Status:** `CANDIDATE / OFFLINE_SOURCE_PLAN_VALIDATED / POSTGRESQL_MIGRATION_NOT_RUN`  
**Base commit:** `b9d5c438c2f14e3136c88d778e393f3c5995f1eb`  
**Owner lane:** separate development branch; owner-only PR #7 remains in deferred UAT  
**Mode:** `IMPLEMENT_FEATURE` (offline planning tool + proposed SQL, not an applied DB feature)  
**Risk:** L2 bounded source import; L3 schema migration *not authorized for execution*

## 1. Outcome and data boundary

A repeatable **read-only import plan** for two source-backed O*NET Database 31.0 occupations, plus additive PostgreSQL DDL and an isolated-only guarded rollback candidate. It helps reviewers inspect exactly what could be imported *before any schema or data mutation*. It does not create a career API, evaluate users, or run an import.

Canonical existing assessment tables (forms, items, response runs, raw scores) are untouched. Source files remain external to public GitHub, with their exact verified SHA-256 in [`UALP_ONET_31_REAL_SOURCE_LOCK_20261118.json`](../research/UALP_ONET_31_REAL_SOURCE_LOCK_20261118.json). The source ZIP is GitHub Actions artifact `14435511727` (run `44322510909`, expires **2026-11-25 14:16 UTC**) or a locally saved copy. No private respondent data or unreleased assessment keys are present.

**Pilot scope:** `15-2051.00` Data Scientists, `15-2051.01` Business Intelligence Analysts; O*NET United States classification, English source labels only. These selections are for **technical source-integrity testing**, not an owner-approved ranked career shortlist or local Armenian labour-market conclusion.

## 2. Verified exact-source readback

Frozen release: O*NET Database **31.0** (August 2026), CC BY 4.0; credit **O*NET Database 31.0, U.S. Department of Labor / Employment and Training Administration**, provide licence link, identify UALP selection/transformation, and do not imply governmental endorsement. The occupational database is **not** the separately licensed O*NET Interest Profiler questionnaire.

| CSV | SHA-256 | Total records (excluding header) |
|---|---|---:|
| occupation_data.csv | `a09eae1d6609686e44e05b7290993a1c8b523d8ca224bc0eedc194c855c3ee02` | 1016 |
| essential_skills.csv | `68c4d31d8c55077238395dca40cc4e6d32e6a608b5474bb8264b1f98ae415bd7` | 18200 |
| scales_reference.csv | `bcba23858ce21ecaacbde303a8993e35d46724b4afb8c9ec2b10e04f42adcfc9` | 33 |

These 3 hashes were confirmed from the original GitHub Actions artifact ZIP. The full-source read is required even for a two-role subset. Output plan sha256 (over canonical sorted JSON, excluding its own hash) is **`78d8aed89a505bf04d4d5d73e609b327bede800694a89a15bab50965a6ec449d`**. The two occupations contain 10 distinct skills × two source scales, 40 rows (39 OBSERVED, one SUPPRESSED/null). One occupation has `08/2024` source ratings and the other has `08/2026`, despite both being included in 31.0. Preserve **row-level original Date**, never rewrite to release month.

Source-level 2 scale definitions: `IM` importance 1–5, `LV` level 0–7. Raw values are source occupational descriptors, **not competence, personal aptitude, readiness, percentages or career fit**.

## 3. Proposed six+one table additive schema (design only)

Reference DDL: `docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql`.

| Table | Versioning and integrity |
|---|---|
| `ualp_career_snapshots` | One source release manifest and frozen file SHA-256, licence, capture time, geography; primary snapshot ID. |
| `ualp_career_occupations` | Stable UALP-owned ID and external taxonomy/code. Codes do not imply identity across future taxonomy changes. |
| `ualp_career_occupation_versions` | Immutable snapshot-specific title and description; composite FK to snapshot on every requirement. |
| `ualp_career_competencies` | Stable skill identity, distinct from knowledge/tasks/abilities; current pilot ESSENTIAL_SKILL only. |
| `ualp_career_competency_versions` | Snapshot-specific label and source ID, never overwrite historical meaning. |
| `ualp_career_scales` | Explicit source scale ID and numeric min/max per snapshot. |
| `ualp_career_requirements` | Immutable source-row composite key and FKs linking *same snapshot* occupation + competency + scale. Value, evidence status, row-level updatedAt, domainSource. SQL constraints preserve null status and scale bounds. |

**No FK to existing assessment tables** and no write into `ualp_schema_version`: Career KB is separately versioned until a migration is approved. No recommendation, RoleGap, manual skill evidence, job-market opportunity or auth tables are created.

The proposed SQL deliberately raises an exception unless a reviewer explicitly sets a **disposable-test-only** session gate. The rollback script also raises unless independently armed, and fails on *any* nonempty Career KB table. Neither file should be installed by an automated migration walker.

## 4. Deterministic import plan

`career_kb/import_plan.py` reuses `career_kb/offline_reader.py`. It takes the **complete three exact source files**, verified `source_lock.json` and optional GitHub Actions `acquisition_receipt.json`, plus an explicit allowlist of at most two pre-reviewed codes. It emits JSON only to a previously absent path. It never makes a network call, opens a DB, touches `webapp`, imports user profiles or calculates any user score.

Stable IDs are **separate** from titles. Occupation and competency IDs remain stable for this taxonomy version; snapshot-scoped version IDs and source-row IDs include 31.0. Any future taxonomy crosswalk is a separate reviewed product decision. `NOT_RELEVANT`, `SUPPRESSED` and `NOT_REPORTED` must remain null, never zero.

Example (run only with existing official source files, not by downloading during import):

```bash
python -m career_kb.import_plan \
  --source-dir /path/to/verified-csv \
  --manifest /path/to/source_lock.json \
  --receipt /path/to/acquisition_receipt.json \
  --occupation-code 15-2051.00 \
  --occupation-code 15-2051.01 \
  --output /path/to/new-import-plan.json
```

The plan includes both the raw source values and exact source provenance, with `readOnly: true`, `mutationAuthorized: false`, `personalData: false`, and `careerFitCalculated: false`. This is an **input proposal** only, not an importer/writer.

## 5. Separate future migration and guarded import phases

**P0: Freeze exact base.** Read actual current TEST schema and existing counts of `ualp_assessment_runs`, `ualp_responses`, and `ualp_scale_scores`, plus source refs and exact app deployment commit. Do not rely on this proposal as a deployment manifest. Confirm no active shared TEST acceptance is overwritten.

**P1: Backup and disposable test.** Under a separately authorized migration block, use a new isolated disposable PostgreSQL instance, snapshot/backup, and replay the existing `migrations/001_initial_postgres_test.sql`. This is not licensed to create an extra paid DB. Use the guarded DDL candidate after explicit review. Prove all existing tables unchanged.

**P2: Implement transaction-scoped import runner only after approval.** Lock exact source release hashes + acquisition evidence; compare plan hash; restrict to 2 codes and the 40 expected rows. Insert tables in parent→child FK order; verify 1 snapshot, 2 roles, 2 role versions, 10 skills, 10 skill versions, 2 scales, 40 requirements. Read back exact row IDs/raw values, 39 observed + 1 suppressed. Reject duplicates with divergent payload, stale manifest, unexpected source codes or missing file. Repeat exact import must be idempotent **NOOP**, no overwrites. A failed/half import must roll back atomically.

**P3: Negative / preservation gates.** Check wrong role/snapshot FK, unmatched source scale bounds, duplicate composite source-record key, missingness coerced to zero, tampered SHA, out-of-range value, changed title and forbidden public profile bridges. Verify assessment `POST /api/runs`, `GET /api/profile`, history and saved raw score result behaviour is unchanged. None of these runtime checks has been run yet.

**P4: Accept isolated migration only, then separate guarded Neon TEST decision.** Exact migration commit, backup location/restore test, real PostgreSQL E2E results, read-back digest, rollback evidence, TEST URL and owner acceptance are mandatory. No Neon TEST schema edit or deployment has been authorized by this block. PROD remains prohibited.

## 6. Rollback and preservation

No changes to database occurred **in this block**; rollback is simply reverting the candidate branch. For future isolated migration: transaction abort for any failed import; the draft schema rollback requires empty tables and explicit test gate. Once imported, **do not DROP live tables**. A populated target requires a separately reviewed targeted snapshot deletion (children before parents) with no consumers and verified backup/restore, or retention of the immutable snapshot pending further approval. A rollback test against a real disposable Postgres instance is **NOT_RUN**.

## 7. Evidence, risks and next authorization boundary

Completed: real ZIP CRC; exact source file hashes; whole-dataset row counts; deterministic JSON planning for two actual occupations; 11 focused local pytest cases including one real-source case; Python compilation and source-preservation checks. *SQL has not been executed on a PostgreSQL server.* No local `postgres`, `initdb`, `psql`, Docker or Podman binary was available for a PostgreSQL rehearsal. Do not label static SQL tests as runtime E2E.

Remaining: SQL syntax/DDL execution, FK/constraint negatives in real PostgreSQL, migration and rollback rehearsal, source writer implementation, Neon TEST, Vercel, Android, human UAT — all `NOT_RUN` under current scope. Risk: career source covers US occupation classifications; Armenia demand, titles, salaries, regulatory licensing and user skill evidence need separate sources and decisions. O*NET 31.0 has row dates from 2024 and 2026; these are not evaluation outcomes.

**Next bounded gate:** owner separately approves isolated ephemeral PostgreSQL DDL+rollback validation, then (only if requested) distinct guarded Neon TEST rollout. Do not interpret this report as acceptance of a migration or job-matching model.
