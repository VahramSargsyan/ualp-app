# UALP Data Contract — PostgreSQL TEST candidate

Status: proposed technology correction on feature/ualp-mvp-001-postgres-test; main has the earlier Sheets draft.
Source evidence: UALP Assessment Library Master v0.7. Preserve provenance, immutable IDs, item/version/status metadata and score-rule versions.

## Source of truth

One dedicated PostgreSQL TEST project. No Google Apps Script or Google Sheets service calls in the application runtime.

Versioned immutable catalog entities:
- ualp_assessments; ualp_assessment_versions; ualp_assessment_forms
- ualp_items, ualp_form_items; ualp_response_options
- ualp_scales, ualp_item_scale_links, ualp_form_scoring_rules

Runtime entities:
- ualp_assessment_runs; ualp_responses; ualp_scale_scores

Initial pilot uses FORM-000004, ASSESS-002, ASSESSVER-000002 from the supplied v0.7 snapshot, marked DRAFT/NOT_REVIEWED. Data import must verify all 21 items, five options, 42 links and 27 scoring rules before enabling the form. All other research assessments remain unavailable until validation and licensing gates pass.

## Invariants

- Primary IDs are immutable; relations are foreign keys; no human-readable titles as relation IDs.
- One requestId maps to one payloadHash/run (unique); retries return the same result and conflicting payloads fail.
- One response per (runId,itemId); one score per (runId,scaleId).
- Writes of run+21 responses+27 scores occur in one transaction; rollback prevents partial results.
- Scoring executes on server using versioned, stored rules, not client-provided score or answer key.
- Public form payload is a whitelist; objective correct answers and private provenance remain server-only.
- No simulated IQ, percentile, validated diagnoses or career-fit judgments from draft Work Values.
- Runtime secrets (DATABASE_URL, access key) are environment variables only, excluded from GitHub.
- Auth is a single shared-key owner TEST gate, NOT suitable for production multi-user access. No real-person data beyond owner until separate security/retention design.
- Source workbook remains unchanged; no destructive catalog overwrite, no import of respondent records.
- PostgreSQL migration/rollback required when accepted schema is modified.
