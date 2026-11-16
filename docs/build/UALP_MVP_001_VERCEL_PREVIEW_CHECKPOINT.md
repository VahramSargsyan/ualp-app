# UALP-MVP-001 / Vercel Hobby Preview checkpoint — 2026-11-15

WORKFLOW_MODE: BUILD_NEW_APP (bounded hosting migration)
CAPABILITY_ID: UALP-MVP-001
SOURCE_BRANCH: feature/ualp-mvp-001-vercel-test
BASE_COMMIT: 630593b410edc5ae9da9e6d5a056a516d09c8f1e
TARGET: Vercel Hobby Preview ONLY, not Production.
NO_PAID_API: true
NO_PROD: true

## Change
- Added root app.py adapter that exports the unchanged webapp.main FastAPI app.
- Added .python-version (3.12) and regression tests for root and API access gate.
- Reused existing Neon Free project snowy-leaf-35157339 / ualp_test unchanged.
- No direct modification to VBOS, ЖЭК, or their data/deployments.
- Existing Render UALP shell is superseded but NOT stopped/deleted (no authorized stop tool available).
- Existing Build Packet and governance updated only on the candidate branch; main not changed.

## Actual checks
- GitHub Actions run 43726940311: SUCCESS on SHA 40e4a29030755fe5c11389f3bd358f3c0ccbb4d6.
- FastAPI root adapter tested with deterministic TestClient assertions.
- Vercel team context: 'Vahram Sargsyan' (team_xKUoy41vYqdwGQvHisGbpcao) plan=hobby.
- Vercel has 0 pre-existing projects under this team at inspection.
- Vercel create_project with explicit Hobby team + FastAPI: **403 forbidden, no permission to create project**.
- Local CLI fallback: no installed authenticated vercel CLI or local Vercel auth directory; no attempt to bypass permission.
- Vercel create/deploy and runtime HTTP tests: **NOT_RUN — ACCESS BLOCKED**.
- Vercel preview URL: **NOT_AVAILABLE**.

## Security and cost
- No database URL or UALP access key placed in Git or Vercel.
- Personal, non-commercial Hobby preview only; owner still must create/select project under their own account.
- Never publish private credentials, pilot responses or source workbook in this public repo.
- Work Values content remains DRAFT/not validated.
- No Vercel PROD, no public-user rollout, and no additional paid resource.

## Owner unblock
On Vercel dashboard, use the authenticated Hobby account to create a project named ualp-private-test from GitHub repository VahramSargsyan/ualp-app. **Do not deploy the default main branch to Production**: first review Production Branch/automatic production deployment settings and configure the separate feature/ualp-mvp-001-vercel-test Preview lane. If the UI does not offer a safe Preview-only path, stop before importing/deploying and return with a screenshot of the configuration screen. Do not enter DATABASE_URL or UALP_ACCESS_KEY until Preview-only target and secret handling are confirmed.

## Resume
1. Verify project ownership/plan and Git connection.
2. Verify exact HEAD and CI for feature/ualp-mvp-001-vercel-test.
3. Set UALP_ENV=TEST and the Neon ualp_test DATABASE_URL plus private UALP_ACCESS_KEY **only** for Preview branch, via protected environment configuration.
4. Deploy exact commit as Preview; verify build, full form GET, negative unauthorized access, atomic POST, dedup/retry, database readback and mobile UI.
5. Once Vercel TEST has passed, stop only the separate UALP Render service; preserve VBOS services and data.
6. Report exact preview URL/SHA, actual checks/NOT_RUN and ask for owner acceptance. Main and PROD are separate future permissions.

ROLLBACK: revert feature branch, leave Neon and VBOS unchanged; cancel/remove only the new unaccepted Vercel Preview after appropriate confirmation. No DB migration.
STATUS: CANDIDATE_CI_PASS / VERCEL_CREATE_403_BLOCKED.


## 2026-11-16 Preview environment setup and controlled redeploy

The owner reported that `UALP_ENV=TEST`, `DATABASE_URL` and `UALP_ACCESS_KEY` were saved in Vercel Preview environment using the dashboard. This is OWNER_REPORTED; actual variable metadata and values have NOT been independently verified because the connected Vercel project API returns 404 and deployment listing returns 403 for the confirmed project. Do not store credentials in this repository.

A **documentation-only** commit records this checkpoint and intentionally triggers Vercel Git integration to generate a new Preview deployment for branch `feature/ualp-mvp-001-vercel-test` with newly saved Preview environment. Its exact commit identity, Vercel status and runtime result must be read back separately before claiming success.

The prior Preview `c0f001bc579df30238f8992088581abeb249ccba` had GitHub status SUCCESS and Vercel PR comment READY at:
https://ualp-app-git-feature-ualp-mvp-001-vercel-test-vahram-sargsyan.vercel.app

Live authenticated HTTP, Neon connection, persisted 21-answer run, duplicate retry and mobile usability remain NOT_RUN until verified. Do not modify VBOS or the old Render UALP service during this gate.
