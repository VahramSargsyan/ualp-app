# UALP-MVP-004 — RIASEC RU desk review and additive TEST readiness

**Date:** 2026-11-16  
**Mode:** DIAGNOSTIC_ONLY for source/translation assessment, with separately permitted synthetic PostgreSQL CI preparation.  
**Source:** Owner-private UALP Assessment Library — CANONICAL DB / v0.7; source item texts/translated bank are intentionally NOT copied here.  
**Source entities:** ASSESS-001; FORM-000001 / ONET_SHORT_60_DIGITAL; ASSESSVER-000001; SCALE-000001..000006; RESPSET-000001.  
**Status:** PRELIMINARY DESK REVIEW ONLY — NOT independent translation validation, NOT qualified human review, NOT licence-compliant publication approval, NOT psychometric validation.

## 1. Official reference and developer licence

- Original 60 activities: O*NET Interest Profiler Short Form PDF (paper form, binary response format), https://www.onetcenter.org/dl_tools/ipsf/Interest_Profiler.pdf .
- Official digital form metadata, 1–5 API answer transport and six interest areas: https://services.onetcenter.org/reference/mnm/ip/ip_questions .
- English original verbatim and Russian adapted material require **different licence consideration**: https://www.onetcenter.org/license_tools.html and https://www.onetcenter.org/license_toolsdev.html .
- Developer License s.3(a), 3(b) requires attribution/modification disclosure, validation appropriate to the new product and intended purpose before introduction of modified content, and a visible notice for intended audiences; internal technical scoring prep is not an adapted-questionnaire release.
- Do not represent USDOL/ETA as having validated, endorsed or tested this translation. Developer registration is described as **optional**. Keep English paper-form binary scoring distinct from digital five-level SUM scoring.

## 2. Canonical structural evidence (live read, read-only)

| Invariant | Observed |
|---|---|
| FORM-000001 member IDs and source indexes | 60 distinct items; indexes 1..60 continuous |
| ItemTranslations locale=ru, ASSESS-001 item IDs | 60/60 non-empty; 60 unique IDs exactly match form |
| Translation statuses | 60/60 NOT_REVIEWED; 0 independently approved |
| Assessment scale links | 60 links; 10 each R/I/A/S/E/C; all POSITIVE and weight 1 |
| FormScoringRules | 6 SUM rules, min 10 items/scale, RIASEC-SUM-v1 |
| Digital response choices | 5 options mapped to integer scores 0,1,2,3,4 |
| RU response labels | 5 drafts; 5 HUMAN_REVIEW_REQUIRED |
| Canonical ValidationRuns | Source/scale-balance PASS; RU semantic-equivalence and release BLOCKED |

Reference: private [UALP canonical library](https://docs.google.com/spreadsheets/d/1WDLyR3A1qwg-r8gcw28dd2hvm2F0pu9rw3ueblWc4-4/edit). Source audit used read-only tab/range queries; did not update the Google Sheet.

## 3. Targeted translation issues for a bilingual reviewer

This section lists *review flags*, not detected definitive translation errors. Item references are SOURCE FORM display indexes and stable ITEM IDs. Exact copyrighted source prompts and full RU text remain in the private library.

| Source index / itemId | Preliminary review risk | What an independent bilingual reviewer should check |
|---|---|---|
| 04 / ITEM-000005 | MEDIUM | Specificity of a hatchery versus a general aquaculture/fish-farm setting |
| 09 / ITEM-000010 | MEDIUM | Whether "machines" was inadvertently narrowed to industrial machine tools |
| 24 / ITEM-000024 | LOW | Whether the broad Russian activity verb retains the original act of creating pictures |
| 26 / ITEM-000026 | MEDIUM | Distinguish painting theatrical scenery from more general set decoration/design |
| 28 / ITEM-000028 | MEDIUM | Natural and culturally comprehensible phrasing of the two dance types |
| 34 / ITEM-000034 | LOW | Whether the professional therapy terminology is understood without unintended competence/qualification framing |
| 39 / ITEM-000039 | LOW | Comprehensibility of the child day-care setting |
| 43 / ITEM-000043 | MEDIUM | "Operate" a business versus "manage" it; preserve original intent |
| 49 / ITEM-000049 | MEDIUM | Contemporary comprehension of the retail department-store setting |
| 60 / ITEM-000060 | LOW | Missing organizational work-context nuance of postal processing |
| Response level 3 / RESPOPT-000003 | MEDIUM | The "Unsure" midpoint: user may interpret as uncertain about *the answer* versus neutral/undecided *interest*. Confirm response instruction and labels together |

**Other items:** no obvious high-risk semantic divergence found during this limited desk comparison of the 60 activities against the paper form. This is NOT a PASS for any item: every RU draft remains NOT_REVIEWED until independent review. The bilingual reviewer must independently check all 60, not just the flagged items, and review the five response labels and respondent instructions. Recommended evidence: item-level verdict, reviewer credentials/independence, change log, comprehension pilot and fit-for-purpose validation.

## 4. Technical integration boundary and rehearsal

- Pure scorer: webapp/riasec_scoring.py; exact 60 unique items, 10/scale, five scores 0..4, result six unnormed totals 0..40. This module is dormant; no RIASEC POST route.
- PostgreSQL synthetic CI rehearsal (test_07 in tests/test_real_postgres_integration.py): populate a synthetic 60-item second form in an *empty disposable localhost-only CI database already seeded with synthetic Work Values*; verify six score sums and 60 responses; owner profile reports both methods independently; existing Work Values runs and scores unchanged; existing FastAPI form and submission endpoints still deny the synthetic RIASEC form.
- The rehearsal does **not** import private item texts, enable a new respondent test, prove translation validity, or authorize migration to Neon.
- No new schema required for the six unnormed SUM scores in current tables, as indicated by the synthetic-only integration rehearsal. Actual additive import still requires its own exact source ID/version manifest, checksum, backup, safe rollback, approved reviewer/validation gate and runtime adapter.

## 5. Release gates still not passed

1. Independent human bilingual semantic review for all 60 RU questions, the five answer labels and administration instructions, with evidence; do not turn AI review into an accepted human-review receipt.
2. An appropriately scoped validation study or documented professional determination that satisfies the intended adapted-product/licence release conditions. Do not label draft pilot results validated, and do not use for employment decisions.
3. Exact content-source and translation-version manifest (private storage), reviewed additive migration to populated Neon TEST, backup/rollback, readback of existing Work Values 1 run / 21 responses / 27 scores, and separately tested form-specific runtime.
4. Owner confirmation of adapted-language TEST rollout after the above gates. No automatic PROD/public launch, main merge, new paid tool or external executor.

**Rollback now:** revert synthetic CI preparation and this review note. No live database, questionnaire or production change was made.
