# UALP-CAREER-KB-010 — Russian labels and compact O*NET source scales

DATE: 2026-11-20
MODE: IMPLEMENT_FEATURE
STATUS: UI_SOURCE_VERIFIED / LOCAL_NODE_SMOKE_PASS / EXACT_VERCEL_BUILD_SUCCESS / HOSTED_HTTP_UAT_NOT_RUN
BASE_COMMIT: `4d162cf7d97a36bbe28a2666382886a99c8bcd9f`
FEATURE_COMMIT: `05fe79dcd062a64a8bf6bc17c1a51b461c25b48b`
BRANCH: `feature/ualp-career-kb-010-ru-compact-ui`
RUNTIME_VERSION: `0.5.2-career-kb-ru-compact-test`
OWNER / TEST: Vahram, one-owner Vercel Hobby Preview only; PROD not configured or permitted.

## Outcome and scope

Only the existing Career KB presentation changed. Ten source-identified English O*NET skill labels are still visible and remain unchanged in Neon and the API; each has a separate Russian UALP display translation pinned to the original `2.A.*` element ID and exact English source name. This translation is **not** an official O*NET localization. Numeric source values are preserved with full precision in PostgreSQL and API. The UI displays two decimals using Russian comma punctuation; native HTML `<meter>` bars use the original scale bounds, `Importance` 1–5 and `Level` 0–7, with distinct styling and accessible labels. `SUPPRESSED/null` displays an explicit absence-of-publication message and **no meter**. Skill cards are a two-column compact mobile grid, falling back to one column on extremely narrow screens. No comparisons across scales, career fit or inferred learner proficiency.

## Exact changed files

- `webapp/index.html`: update only embedded 009 UI snippet, its career-specific CSS, and visible version/comment.
- `webapp/main.py`: TEST `APP_VERSION` string from `0.5.1` to `0.5.2`; no change to routes, authentication or database access.
- `tests/verify_career_kb_ui.cjs`: source-backed English-label fixtures, translation assertions, meter min/max/value, source-value formatting, SUPPRESSED/no meter, unauthorized access and source drift negatives.
- This receipt and a bounded Build Packet appendix are documentation-only.

## Real checks and boundaries

- Local Node 22: `node --check` of the updated source: **PASS**.
- Local synthetic browser-API/DOM smoke against the new UI source and a marker-wrapped HTML source: **PASS** (`CAREER_KB_UI_RU_COMPACT_SYNTHETIC_SMOKE_PASS`). No credentials or network accessed by that test.
- Independent read-only Neon UALP TEST source inventory: exactly 10 original skill labels and IDs, matching the display allowlist: **PASS**.
- GitHub exact-commit file readback of new inline JS (10 translated IDs), CSS and both version locations: **PASS**.
- GitHub/Vercel status for feature commit `05fe79...`: `success`, `Deployment has completed` (build receipt, not user HTTP acceptance); source dashboard: https://vercel.com/vahram-sargsyan/ualp-app/ETu1XQhodxaGyF3xwFJBwrSk2spW.
- Vercel feedback check provides Preview hostname: `ualp-app-git-feature-ualp-career-kb-010-32ee15-vahram-sargsyan.vercel.app`. This URL was **not** successfully fetched from the external assistant environment. Do not treat its HTTP endpoints, cookie session or visual Android UI as verified.
- **NOT_RUN:** actual protected Preview HTTP, owner Android Chrome UAT, complete assessment regression suite, PostgreSQL E2E and production. No GitHub Actions, other agents, Codex or paid API started.

## Data protection and rollback

No Neon writes, schema changes, new IDs or versioned source migrations. O*NET release 31.0, metadata, source values, status, 40 requirements, and user responses/scores remain in existing TEST database. GitHub main and original Draft PR #7 remain unchanged. The previous `0.5.1` Preview remains the safe UI fallback. Roll back the isolated branch or use the exact older Preview; no database rollback or manual file copying needed.

## Owner acceptance

Open only the feature branch Preview. Confirm footer `UALP 0.5.2-career-kb-ru-compact-test`, sign in with existing owner key and open Career KB. Check `Понимание прочитанного` plus original `Reading Comprehension`, `4,00 / 5` and `4,25 / 7` on Data Scientists; check that a `SUPPRESSED` measurement has no meter. Ensure the other role and existing profile/history remain usable. Acceptance is deferred until the owner's real browser confirmation.

NEXT_BOUNDARY: Await owner visual acceptance of the revised TEST Preview; do not proceed to career matching, Armenia labor market estimates, wider translation inventory or PROD without distinct authorization.
