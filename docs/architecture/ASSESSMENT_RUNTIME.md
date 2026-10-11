# Assessment Runtime Architecture

## Main flow

`getAssessmentForm(formKey, locale)`
-> read canonical form metadata
-> resolve ordered form items
-> resolve localized prompt/options/assets
-> sanitize client payload

`startAssessment(input)`
-> validate config/form
-> idempotency check
-> create AssessmentRun STARTED
-> return runId + safe form payload

`submitAssessment(input)`
-> validate run and full response set
-> load server-only scoring material
-> compute deterministic scale scores
-> idempotency check under minimal lock
-> persist Responses + ScaleScores
-> mark run COMPLETED
-> return user-safe result

## Performance shape

For MVP, each request performs bounded batch reads by required sheet/range and filters in memory. Request-local header/table caches prevent repeated metadata reads inside one request.

Scale-dependent row indexes/cache are introduced only where measurement justifies them. Runtime run lookup already has a narrow `EntityRowIndex` contract so normal known-run lookup does not require a full AssessmentRuns scan.

## Failure model

- Validation happens before writes whenever possible.
- Submit uses explicit run states: `STARTED -> SUBMITTING -> COMPLETED`.
- Failed mid-commit remains diagnosable as `SUBMITTING`; retry uses clientRequestId and existing persisted rows rather than creating a second logical submission.
- Content DB is never mutated by assessment-taking APIs.

## Security / test integrity

Correct answers and scoring internals stay server-side. Browser source must not reveal ICAR keys.

## Result labeling

Pilot UI must label results as exploratory while localization/human review/pilot validation remain incomplete.
