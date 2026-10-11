# UALP Product Blueprint

## Product goal

Build a reusable assessment-and-development platform that turns measured evidence into a profile, compares that profile with role requirements, assigns development work, and verifies change through reassessment.

Primary loop:
`ASSESSMENT -> PROFILE -> CAREER/ROLE FIT -> LEARNING PATH -> PRACTICE -> REASSESSMENT -> GROWTH`

## Initial users

First pilot user: project owner / self-discovery use.
Later: additional consenting users. Employment use remains a stricter future mode with human-in-loop controls.

## First MVP

The first useful product does not require career matching yet.

MVP-001:
1. open one assessment form;
2. render localized questions/options;
3. start an AssessmentRun;
4. collect complete responses;
5. score server-side using versioned rules from the canonical Assessment Library;
6. persist Responses and ScaleScores in a separate Runtime DB;
7. show a transparent exploratory result.

## First battery

- `ONET_SHORT_60_DIGITAL` — RIASEC
- `UALP_WV21_RU_LIKERT` — Work Values pilot
- `ICAR16_DIGITAL` — Cognitive Core anchor

The runtime must not assume these are the only future assessment types.

## Canonical data

Assessment Library Google Sheet is authoritative for:
- Assessments / versions / forms
- items and localization layers
- response sets/options
- item-specific options
- scale links
- form scoring rules
- assets/provenance/license metadata

Runtime DB is authoritative for:
- Users
- AssessmentRuns
- Responses
- ScaleScores
- idempotency/dedup state
- runtime errors

## Result semantics

Keep separate:
- Raw measurement
- Derived profile
- Recommendation

Do not map an individual item directly to a job.
Do not convert ICAR-16 to IQ/percentile without a validated norm/model.
Do not present draft translations or pilot scales as validated high-stakes diagnostics.

## Later capabilities

- combined profile across assessment families
- role/occupation knowledge base
- separate Fit / Readiness / Opportunity / LearningPotential / Confidence / Coverage outputs
- RoleGapProfile
- LearningAssignment
- reassessment and profile change

## Success criterion for MVP-001

Same form version + same responses + same algorithm version => same scores; stored result is reproducible and no scoring key is exposed to the client.
