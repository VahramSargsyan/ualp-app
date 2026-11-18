# UALP Career / Role Knowledge Base — proposed source and data contract v0.1

STATUS: DESIGN_CANDIDATE / NOT_RUNTIME / NO_SCHEMA_MIGRATION
CAPABILITY: UALP-CAREER-KB-001
BASE: 3cf3378ce8b3256fc18e0e6bf8303cd21cc15a25
DATE: 2026-11-18
OWNER: Vahram / future owner-only TEST
AUTHORITY: docs/product/UALP_PRODUCT_BLUEPRINT.md; docs/architecture/DATA_CONTRACT.md; docs/architecture/ASSESSMENT_RUNTIME.md
BOUNDARY: No score computation, career ranking, learner assessment, API route, database write or deployment.

## 1. Intended product outcome

Connect *versioned evidence about an occupation* to *explicitly evidenced skills* so that a future learner can choose a role, see source-backed requirements, identify unknowns, and plan verifiable practice. This design does NOT equate interests/values/cognitive test scores to proficiency.

`ASSESSMENT -> PROFILE (context only) -> ROLE EXPLORATION -> VERIFIED SKILL EVIDENCE -> GAP REVIEW -> LEARNING PRACTICE -> REASSESSMENT`

No employer selection, diagnosis, IQ scores, percentiles or job-suitability percentages.

## 2. Authority boundaries

- Assessment canonical store: existing PostgreSQL `ualp_catalog_*`, `ualp_assessment_runs`, `ualp_responses`, `ualp_scale_scores`. Their IDs, sources and scoring are immutable under this block.
- Proposed Career KB source: separately versioned, attributed, frozen occupation/competency source snapshots. **Not** the O*NET Interest Profiler instrument or the original UALP Assessment Library workbook.
- Proposed career KB tables are NOT part of existing `migrations/001_initial_postgres_test.sql`; no database structure changes in this stage.
- Future learner skill evidence is a separate consented record and must never be inferred from survey answers.
- The existing owner-only `GET /api/profile` is a source of saved assessment context only. Its raw scales may be shown alongside career exploration with exact method/version/algorithm attribution, never silently converted into skill ratings.

## 3. Logical entities (proposed only; names/fields not yet physical SQL)

| Entity | Identity / keys | Required content and invariant |
|---|---|---|
| `CareerSourceSnapshot` | `snapshotId` | Provider; release; source URL; retrievedAt UTC; licence URI; source hash when actual bytes are acquired; geography; taxonomy version; review status. Immutable after acceptance. |
| `CareerOccupation` | `occupationId` | Stable internal ID; source taxonomy and external code as *versioned attributes*, title/locale; status. External codes are not the internal ID. |
| `CareerOccupationVersion` | `occupationVersionId` FK to `occupationId`, `snapshotId` | Human-readable label and description at a frozen source release; historical identity must remain readable. |
| `CareerCompetency` | `competencyId` | `kind` SKILL / KNOWLEDGE / TASK / ABILITY, label, source element ID + taxonomy version; translation locale/status. Do not collapse knowledge, skills and abilities. |
| `CareerRoleRequirement` | `requirementId` FK to occupation-version + competency | Source-backed `measureKind` and `sourceScaleId`, `value` and exact source scale bounds, `evidenceStatus` OBSERVED / NOT_REPORTED, snapshot + source-record provenance. Numeric measures must not be compared across incompatible scales. |
| `LearnerSkillEvidence` (future, out of scope) | `evidenceId` FK to competency and learner | Skill claim or completed task; verification level, date, link to actual work/artefact, owner consent; never auto-populated by RIASEC/Work Values or ICAR. |
| `RoleGapReview` (future derived, out of scope) | `reviewId` + role/version and learner evidence watermark | Requirement-by-requirement state: EVIDENCED / NEEDS_REVIEW / UNKNOWN, with explanation and provenance. **UNKNOWN does not mean deficit**. |
| `LearningAssignment` (future, out of scope) | stable assignment ID | Role/competency, action, expected evidence, human review, completion evidence, reassessment date. |

Provenance resolution for each actual sourced requirement: `requirement -> occupationVersion -> sourceSnapshot`, plus `sourceRecordId` and `sourceScaleId`. No unversioned JOIN to the latest occupation record for historical results.

## 4. Source field mapping (not an import)

Candidate offline source is O*NET Database 31.0 (August 2026); see source-gate memo. Potential source files: Occupation Data, Skills, Knowledge, Abilities, Task Statements, Content Model Reference and Scales. Adopt only fields with explicit source definitions. Actual O*NET source IDs/codes and numeric ratings must be read and checksum-locked from the downloaded release before import. No invented occupation-to-skill values.

Suggested adapter mapping:
- `O*NET-SOC Code` -> version-specific `externalCode`, `taxonomyVersion`; internal ID remains UALP-owned.
- `Element ID` + descriptor family -> `competencyId` through a reviewed crosswalk (never by label similarity).
- `Scale ID` + source scale min/max + `Data Value` -> `measureKind`/`sourceScaleId`/`value`; preserve missing/suppressed metadata and source date.
- Task statements are descriptive work evidence, NOT a psychometric measurement or a skill score.

Never assume US labour-market conditions, licensing, education or opportunity are valid for Armenia. Opportunity/employment demand is a separate geo/time source; current pilot has NONE.

## 5. Profile bridge: read-only and interpretation-safe

Input candidate: existing authenticated `GET /api/profile`, which yields completed methods and persisted parent raw scores. Explicit allowlist of assessment evidence: `formKey`, `formVersion`, `algorithmVersion`, `completedRuns`, original raw-scale IDs and values (when present).

Bridge contract:
- `profileContext`: user-visible background only, with source/version and `NOT_VALIDATED_FOR_CAREER_FIT`.
- `verifiedSkillEvidence`: empty unless separately submitted, consented and reviewed in a future feature.
- `roleRequirements`: independent, versioned occupation source data.
- `gaps`: NOT_COMPUTED now. A missing measurement or missing learner evidence is UNKNOWN, not zero or poor fit.
- No client-side or server-side `profile x role` numerical multiplication, ranking or score normalization in v0.1.
- No storage of personal scores or copies of respondent answers in the Career KB.
- If a form/version/scale lacks a reviewed crosswalk, no interpretation is permitted. A future crosswalk cannot itself validate a draft instrument.

## 6. Fixture and acceptance invariants

`tests/fixtures/career_role_kb_synthetic_v0_1.json` is 100% fabricated and explicitly NOT the O*NET Database. Its purpose is to demonstrate 2 roles, 3 competencies, 4 requirements, immutable source provenance, distinct measurement scales and an unknown measurement. The fixture contains no personal data, psychometric score or copyrighted source item.

Validation must reject:
1. duplicate internal IDs, orphan occupation/competency/source refs;
2. missing version/provenance or wrong snapshot reference;
3. numeric out-of-range / non-finite measurements and status/value contradiction;
4. coercing `NOT_REPORTED`/null to zero;
5. external source claim for fabricated rows or any nonempty personal/assessment-to-skill scoring map;
6. accidental reuse of the same ID with different semantics across snapshots.

## 7. Boundaries for the future authorized implementation

Before creating new tables or importing actual source:
- Independently download/pin one full source release, hashes, exact field dictionary and licence/attribution receipt.
- Define additive migration with SQL dry-run on disposable PostgreSQL containing existing Work Values and RIASEC fixtures, backup, negative tests, idempotency and rehearsed rollback.
- Preserve existing owner data and prior runtime, and create no new public routes without security review.
- Establish user-facing geography/translation scope and a first role selection before building matching.
- Publish no fabricated occupation scores or career suitability percentages.

NEXT_BLOCK (separately authorized): `CAREER_KB_SOURCE_LOCK_AND_OFFLINE_READER` — independently verify and parse a small, source-locked O*NET 31.0 occupation/competency subset locally, with source metadata and no Neon write, then plan migration separately.

## 8. Rollback and deployment

This capability is documentation + synthetic fixture + isolated validator only on a new docs branch, not the owner TEST branch. No schema migration; no TEST URL change; no Vercel, Neon, Android or PROD action authorized. Rollback is revert of this docs-only commit; original TEST HEAD remains `3cf3378ce8b3256fc18e0e6bf8303cd21cc15a25`.
