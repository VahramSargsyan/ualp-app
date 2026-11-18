-- UALP-CAREER-KB-007 / OWNER-APPROVAL-GATED NEON TEST SQL CANDIDATE.
-- THIS IS NOT AN AUTOMATIC MIGRATION. DO NOT EXECUTE IN ANY PROD OR NON-UALP DB.
-- Separate from disposable-only migration 004; 7 CREATE TABLEs copied without DDL changes.
-- Requires owner-approved exact TEST release and fresh independently verified branch backup.
-- Validated from committed source on exact UALP TEST branch only; not auto-loaded by app.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
DO $ualp_gate$
BEGIN
  IF current_database() IS DISTINCT FROM 'ualp_test'
     OR current_user IS DISTINCT FROM 'ualp_test_owner'
     OR current_setting('ualp.career_neon_test_schema_gate', true)
          IS DISTINCT FROM 'APPROVED_UALP_NEON_TEST_ADD_ONLY_007'
     OR (SELECT count(*) FROM information_schema.tables
         WHERE table_schema='public' AND table_type='BASE TABLE'
           AND table_name LIKE 'ualp_%' AND table_name NOT LIKE 'ualp_career_%') <> 10
     OR (SELECT count(*) FROM information_schema.tables
         WHERE table_schema='public' AND table_type='BASE TABLE'
           AND table_name LIKE 'ualp_career_%') <> 0
     OR (SELECT count(*) FROM public.ualp_schema_version
         WHERE version_key='runtime_schema' AND version_value='UALP-POSTGRES-TEST-v0.1') <> 1 THEN
       RAISE EXCEPTION 'UALP-CAREER-KB-007: Neon TEST release gate denied';
  END IF;
END
$ualp_gate$;

CREATE TABLE ualp_career_snapshots (
    snapshot_id text PRIMARY KEY,
    provider text NOT NULL CHECK (provider = 'O*NET Database'),
    release text NOT NULL,
    license_url text NOT NULL,
    geography text NOT NULL,
    manifest_sha256 char(64) NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    file_checks jsonb NOT NULL CHECK (jsonb_typeof(file_checks) = 'object'),
    acquired_at timestamptz NOT NULL,
    UNIQUE(provider,release,manifest_sha256)
);
CREATE TABLE ualp_career_occupations (
    occupation_id text PRIMARY KEY,
    taxonomy text NOT NULL,
    source_external_code text NOT NULL,
    UNIQUE(taxonomy, source_external_code)
);
CREATE TABLE ualp_career_occupation_versions (
    occupation_version_id text PRIMARY KEY,
    occupation_id text NOT NULL REFERENCES ualp_career_occupations(occupation_id) ON DELETE RESTRICT,
    snapshot_id text NOT NULL REFERENCES ualp_career_snapshots(snapshot_id) ON DELETE RESTRICT,
    source_external_code text NOT NULL CHECK (source_external_code ~ '^[0-9]{2}-[0-9]{4}[.][0-9]{2}$'),
    source_locale text NOT NULL CHECK (source_locale = 'en'),
    title text NOT NULL CHECK (length(btrim(title)) > 0),
    description text NOT NULL CHECK (length(btrim(description)) > 0),
    UNIQUE(occupation_id,snapshot_id),
    UNIQUE(occupation_version_id,snapshot_id)
);
CREATE TABLE ualp_career_competencies (
    competency_id text PRIMARY KEY,
    kind text NOT NULL CHECK (kind = 'ESSENTIAL_SKILL'),
    provider_element_id text NOT NULL,
    UNIQUE(kind,provider_element_id)
);
CREATE TABLE ualp_career_competency_versions (
    competency_version_id text PRIMARY KEY,
    competency_id text NOT NULL REFERENCES ualp_career_competencies(competency_id) ON DELETE RESTRICT,
    snapshot_id text NOT NULL REFERENCES ualp_career_snapshots(snapshot_id) ON DELETE RESTRICT,
    source_locale text NOT NULL CHECK (source_locale = 'en'),
    label text NOT NULL CHECK (length(btrim(label)) > 0),
    UNIQUE(competency_id,snapshot_id),
    UNIQUE(competency_version_id,snapshot_id)
);
CREATE TABLE ualp_career_scales (
    snapshot_id text NOT NULL REFERENCES ualp_career_snapshots(snapshot_id) ON DELETE RESTRICT,
    scale_id text NOT NULL,
    label text NOT NULL CHECK (length(btrim(label)) > 0),
    minimum numeric(10,4) NOT NULL,
    maximum numeric(10,4) NOT NULL,
    PRIMARY KEY(snapshot_id,scale_id),
    UNIQUE(snapshot_id,scale_id,minimum,maximum),
    CHECK(minimum < maximum)
);
CREATE TABLE ualp_career_requirements (
    requirement_id text PRIMARY KEY,
    snapshot_id text NOT NULL REFERENCES ualp_career_snapshots(snapshot_id) ON DELETE RESTRICT,
    occupation_version_id text NOT NULL,
    competency_version_id text NOT NULL,
    source_record_id text NOT NULL,
    scale_id text NOT NULL,
    scale_minimum numeric(10,4) NOT NULL,
    scale_maximum numeric(10,4) NOT NULL,
    raw_value numeric(10,4),
    evidence_status text NOT NULL CHECK (evidence_status IN
        ('OBSERVED','SUPPRESSED','NOT_RELEVANT','NOT_REPORTED')),
    source_updated_at text NOT NULL CHECK (source_updated_at ~ '^[0-9]{2}/[0-9]{4}$'),
    domain_source text NOT NULL CHECK (length(btrim(domain_source)) > 0),
    FOREIGN KEY (occupation_version_id,snapshot_id)
       REFERENCES ualp_career_occupation_versions(occupation_version_id,snapshot_id)
       ON DELETE RESTRICT,
    FOREIGN KEY (competency_version_id,snapshot_id)
       REFERENCES ualp_career_competency_versions(competency_version_id,snapshot_id)
       ON DELETE RESTRICT,
    FOREIGN KEY (snapshot_id,scale_id,scale_minimum,scale_maximum)
       REFERENCES ualp_career_scales(snapshot_id,scale_id,minimum,maximum)
       ON DELETE RESTRICT,
    UNIQUE(snapshot_id,occupation_version_id,competency_version_id,scale_id),
    UNIQUE(snapshot_id,source_record_id),
    CHECK (
       (evidence_status = 'OBSERVED' AND raw_value IS NOT NULL
         AND raw_value BETWEEN scale_minimum AND scale_maximum)
       OR
       (evidence_status <> 'OBSERVED' AND raw_value IS NULL)
    )
);
CREATE INDEX ualp_career_requirement_role_idx
    ON ualp_career_requirements(occupation_version_id,scale_id);
COMMIT;
