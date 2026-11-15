-- UALP-MVP-001 | additive install on a NEW EMPTY isolated Neon TEST database ONLY.
-- No PROD, legacy, VBOS, or ЖЭК database may run this script.
-- Migrating a populated schema requires a separate approved migration and backup.
BEGIN;
CREATE TABLE ualp_schema_version (
    version_key text PRIMARY KEY,
    version_value text NOT NULL,
    installed_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO ualp_schema_version(version_key,version_value)
VALUES ('runtime_schema','UALP-POSTGRES-TEST-v0.1');

CREATE TABLE ualp_catalog_forms (
    form_id text PRIMARY KEY,
    form_key text NOT NULL UNIQUE,
    form_version text NOT NULL,
    locale text NOT NULL,
    status text NOT NULL CHECK(status IN ('DRAFT','RELEASED','ARCHIVED')),
    validation_status text NOT NULL,
    item_count integer NOT NULL CHECK (item_count BETWEEN 1 AND 100),
    algorithm_version text NOT NULL
);
CREATE TABLE ualp_catalog_items (
    item_id text PRIMARY KEY,
    form_id text NOT NULL REFERENCES ualp_catalog_forms(form_id),
    prompt text NOT NULL CHECK (length(prompt)>0),
    display_order integer NOT NULL,
    required boolean NOT NULL DEFAULT true,
    UNIQUE(form_id,display_order)
);
CREATE INDEX ualp_items_form_idx ON ualp_catalog_items(form_id,display_order);
CREATE TABLE ualp_catalog_options (
    form_id text NOT NULL REFERENCES ualp_catalog_forms(form_id),
    option_key text NOT NULL,
    label text NOT NULL,
    score_value numeric(8,4) NOT NULL CHECK(score_value>=0 AND score_value<=4),
    display_order integer NOT NULL,
    PRIMARY KEY(form_id,option_key),
    UNIQUE(form_id,display_order)
);
CREATE TABLE ualp_catalog_scales (
    scale_id text PRIMARY KEY,
    form_id text NOT NULL REFERENCES ualp_catalog_forms(form_id),
    scale_key text NOT NULL,
    label text NOT NULL,
    is_parent boolean NOT NULL,
    UNIQUE(form_id,scale_key)
);
CREATE TABLE ualp_catalog_links (
    item_id text NOT NULL REFERENCES ualp_catalog_items(item_id),
    scale_id text NOT NULL REFERENCES ualp_catalog_scales(scale_id),
    weight numeric(8,4) NOT NULL DEFAULT 1,
    direction text NOT NULL DEFAULT 'POSITIVE',
    PRIMARY KEY(item_id,scale_id)
);
CREATE INDEX ualp_links_scale_idx ON ualp_catalog_links(scale_id);
CREATE TABLE ualp_catalog_scoring_rules (
    form_id text NOT NULL REFERENCES ualp_catalog_forms(form_id),
    scale_id text NOT NULL REFERENCES ualp_catalog_scales(scale_id),
    method text NOT NULL,
    min_items integer NOT NULL CHECK(min_items>0),
    algorithm_version text NOT NULL,
    status text NOT NULL,
    PRIMARY KEY(form_id,scale_id)
);
CREATE TABLE ualp_assessment_runs (
    run_id uuid PRIMARY KEY,
    request_id uuid NOT NULL UNIQUE,
    form_id text NOT NULL REFERENCES ualp_catalog_forms(form_id),
    payload_sha256 char(64) NOT NULL,
    consent boolean NOT NULL CHECK (consent = true),
    status text NOT NULL CHECK(status IN ('COMPLETED')),
    algorithm_version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ualp_runs_form_time_idx ON ualp_assessment_runs(form_id,created_at DESC);
CREATE TABLE ualp_responses (
    run_id uuid NOT NULL REFERENCES ualp_assessment_runs(run_id),
    item_id text NOT NULL REFERENCES ualp_catalog_items(item_id),
    option_key text NOT NULL,
    PRIMARY KEY(run_id,item_id)
);
CREATE TABLE ualp_scale_scores (
    run_id uuid NOT NULL REFERENCES ualp_assessment_runs(run_id),
    scale_id text NOT NULL REFERENCES ualp_catalog_scales(scale_id),
    raw_score numeric(8,4) NOT NULL,
    answered_count integer NOT NULL CHECK (answered_count>0),
    algorithm_version text NOT NULL,
    PRIMARY KEY(run_id,scale_id)
);
COMMIT;
