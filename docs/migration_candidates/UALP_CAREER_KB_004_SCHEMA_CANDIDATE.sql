-- REVIEW-ONLY CANDIDATE: never run against Neon, TEST, or PROD without a separate
-- approved MIGRATION_PLAN, fresh backup and authenticated exact-source TEST gate.
-- No runtime code imports or invokes this document. It is not a migration receipt.
-- Candidate additive PostgreSQL 18 schema for O*NET 31.0 snapshot-backed roles.
BEGIN;
DO $$
BEGIN
  IF current_setting('ualp.career_migration_gate', true) IS DISTINCT FROM 'APPROVED_DISPOSABLE_TEST' THEN
    RAISE EXCEPTION 'UALP Career KB migration is NOT authorized in this session';
  END IF;
END
$$;

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
