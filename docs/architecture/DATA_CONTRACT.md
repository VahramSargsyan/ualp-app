# UALP Data Contract

## Database split

### Assessment Library — read-mostly canonical content DB
Runtime reads these tables by header name, never by hard-coded column index:
- AssessmentForms
- AssessmentFormItems
- Items
- ItemTranslations
- ResponseSets
- ResponseOptions
- ResponseOptionTranslations
- ItemOptions
- ItemOptionTranslations
- ItemScaleLinks
- FormScoringRules
- Scales
- EntityTranslations
- Assets
- ItemAssets

### Runtime DB — user state
Fresh MVP schema:

#### Users
`userId, displayName, locale, status, createdAt, updatedAt`

#### AssessmentRuns
`assessmentRunId, userId, assessmentFormId, formKey, formVersion, locale, status, startedAt, submittedAt, algorithmVersion, clientStartRequestId, clientSubmitRequestId, contentSchemaVersion, createdAt, updatedAt`

#### Responses
`responseId, assessmentRunId, itemId, responseOptionId, itemOptionId, responseValue, answeredAt, createdAt`

#### ScaleScores
`scaleScoreId, assessmentRunId, scaleId, rawScore, answeredItems, expectedItems, algorithmVersion, createdAt`

#### RequestDedup
`clientRequestId, operation, entityType, entityId, status, responseJson, createdAt, updatedAt`

#### EntityRowIndex
`entityType, entityId, sheetName, rowNumber, updatedAt`

#### ErrorLog
`errorId, operation, code, message, contextJson, createdAt`

#### RuntimeSchema
`schemaKey, schemaVersion, installedAt, environment`

## Stable identifiers

Use server-generated UUID-backed identifiers. IDs never encode mutable labels.
Relations use IDs only.

## Client boundary

Browser payload may contain:
- itemId
- displayOrder
- localized prompt
- safe option ID/key/label
- required flag
- display asset URI if approved for development

Browser payload must never contain:
- `isCorrect`
- scoring weights
- scoreValue
- correct option IDs
- full FormScoringRules
- private provenance/admin notes not needed by UI

## Missing localization

Fallback order:
requested locale -> canonical language.
The payload reports whether fallback occurred so pilot results are interpretable.
