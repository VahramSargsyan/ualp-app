# UALP Assessment Runtime — Python/PostgreSQL private TEST

Flow:
1. Browser loads a static mobile-friendly interface hosted by the FastAPI server.
2. Owner supplies TEST access key; server checks secret constant-time and returns only approved draft form/questions and visible options.
3. Browser submits the full 21-item answer set with explicit consent and a UUID requestId.
4. FastAPI validates form/version/response completeness; server loads immutable scale link/rules from PostgreSQL.
5. PostgreSQL transaction stores one AssessmentRun, 21 Responses and 27 ScaleScores atomically.
6. Successful reply returns six parent raw mean results, source/algorithm version and pilot disclaimer.
7. Identical retry returns stored result; conflicting payload with the same requestId returns HTTP 409.

Deployment: Neon Free PostgreSQL is the unchanged TEST data authority; Vercel Hobby Preview provides the Python/FastAPI ASGI function. Existing routes and scoring unchanged. Vercel Hobby is for personal, non-commercial work and has function quotas/duration limits. Preview is not PROD. The old Render shell is superseded and must not consume shared VBOS hours once switched.

Security: public GitHub code != public assessment service. Do not commit workbook contents or answer keys without a rights review. Shared TEST access key is not a future account/role system. Production launch requires proper individual authentication, consent/retention policies and content validation.

Observability and safety: /health returns limited TEST status, no secrets. Local SQLite can test correctness but does NOT count as PostgreSQL TEST runtime. No Apps Script or Sheets integration.
