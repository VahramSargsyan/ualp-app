-- REVIEW-ONLY rollback plan. DANGEROUS / NEVER RUN ON POPULATED Neon TEST OR PROD.
-- Only for independently authorized *disposable* PostgreSQL rehearsal.
-- Refuses any nonempty Career KB table; requires separate explicit session gate.
-- For a populated system, back out only an exact, unreferenced source snapshot
-- using an approved row-level rollback and verified backup; NOT this script.
BEGIN;
DO $$
BEGIN
  IF current_setting('ualp.career_rollback_gate', true) IS DISTINCT FROM 'APPROVED_DISPOSABLE_TEST' THEN
    RAISE EXCEPTION 'Career KB rollback is not authorized';
  END IF;
  IF EXISTS (SELECT 1 FROM ualp_career_requirements LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_competency_versions LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_occupation_versions LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_competencies LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_occupations LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_scales LIMIT 1)
    OR EXISTS (SELECT 1 FROM ualp_career_snapshots LIMIT 1) THEN
    RAISE EXCEPTION 'Career KB rollback refused: nonempty tables';
  END IF;
END
$$;
DROP TABLE ualp_career_requirements;
DROP TABLE ualp_career_scales;
DROP TABLE ualp_career_competency_versions;
DROP TABLE ualp_career_competencies;
DROP TABLE ualp_career_occupation_versions;
DROP TABLE ualp_career_occupations;
DROP TABLE ualp_career_snapshots;
COMMIT;
