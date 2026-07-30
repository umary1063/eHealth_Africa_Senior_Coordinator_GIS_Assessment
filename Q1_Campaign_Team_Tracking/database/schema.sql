-- Q1 Campaign Team Tracking and Coverage Reconciliation
-- PostgreSQL/PostGIS logical schema. This file creates no data and applies no QA rules.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS processed;
CREATE SCHEMA IF NOT EXISTS audit;

-- Reference layer: administrative geography supplied in boundaries.gpkg.
CREATE TABLE IF NOT EXISTS reference.states (
    state_name TEXT PRIMARY KEY,
    geom geometry(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reference.lgas (
    lga_code TEXT PRIMARY KEY,
    lga_name TEXT NOT NULL,
    lga_type TEXT,
    state_name TEXT NOT NULL REFERENCES reference.states(state_name),
    geom geometry(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reference.wards (
    ward_code TEXT PRIMARY KEY,
    ward_name TEXT NOT NULL,
    lga_code TEXT NOT NULL REFERENCES reference.lgas(lga_code),
    lga_name TEXT NOT NULL,
    lga_type TEXT,
    state_name TEXT NOT NULL REFERENCES reference.states(state_name),
    geom geometry(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Raw layer: direct representations of supplied records, retaining source metadata.
CREATE TABLE IF NOT EXISTS raw.gps_points_raw (
    gps_track_point_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id TEXT,
    logger_id TEXT,
    observed_at TIMESTAMP,
    longitude NUMERIC,
    latitude NUMERIC,
    accuracy_m NUMERIC,
    speed_kmh NUMERIC,
    geom geometry(Point, 4326),
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_raw_gps_source_row UNIQUE (source_file, source_row_number)
);

CREATE TABLE IF NOT EXISTS raw.settlements (
    settlement_id TEXT PRIMARY KEY,
    settlement_name TEXT,
    settlement_type TEXT,
    ward_code TEXT REFERENCES reference.wards(ward_code) DEFERRABLE INITIALLY DEFERRED,
    ward_name TEXT,
    lga_code TEXT REFERENCES reference.lgas(lga_code) DEFERRABLE INITIALLY DEFERRED,
    lga_name TEXT,
    longitude NUMERIC,
    latitude NUMERIC,
    target_population_under5 NUMERIC,
    geom geometry(Point, 4326),
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_raw_settlement_source_row UNIQUE (source_file, source_row_number)
);

CREATE TABLE IF NOT EXISTS raw.etally_records (
    etally_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    campaign_date DATE,
    team_id TEXT,
    settlement_id TEXT REFERENCES raw.settlements(settlement_id) DEFERRABLE INITIALLY DEFERRED,
    ward_code TEXT,
    lga_name TEXT,
    target_population_under5 INTEGER,
    doses_administered INTEGER,
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_raw_etally_source_row UNIQUE (source_file, source_row_number)
);

CREATE TABLE IF NOT EXISTS raw.inaccessible_settlements (
    inaccessible_settlement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id TEXT REFERENCES raw.settlements(settlement_id) DEFERRABLE INITIALLY DEFERRED,
    settlement_name TEXT,
    ward_code TEXT,
    ward_name TEXT,
    lga_name TEXT,
    security_classification TEXT,
    date_classified DATE,
    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_raw_inaccessible_source_row UNIQUE (source_file, source_row_number)
);

-- Processed layer: QA outputs and decision-support products derived from raw records.
CREATE TABLE IF NOT EXISTS processed.gps_quality_flags (
    gps_quality_flag_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gps_track_point_id BIGINT NOT NULL REFERENCES raw.gps_points_raw(gps_track_point_id),
    source_file TEXT NOT NULL,
    team_id TEXT,
    observed_at TIMESTAMP,
    quality_rule TEXT NOT NULL,
    flag_value BOOLEAN NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_gps_quality_point_rule UNIQUE (gps_track_point_id, quality_rule)
);

CREATE TABLE IF NOT EXISTS processed.cleaned_gps_points (
    cleaned_gps_point_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gps_track_point_id BIGINT NOT NULL UNIQUE REFERENCES raw.gps_points_raw(gps_track_point_id),
    geom geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed.settlement_visit_classification (
    settlement_visit_classification_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    visit_classification TEXT NOT NULL,
    supporting_track_point_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed.settlement_coverage_summaries (
    settlement_coverage_summary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    track_visit_classification TEXT,
    target_population_under5 NUMERIC,
    etally_doses_administered NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed.ward_coverage_summaries (
    ward_coverage_summary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ward_code TEXT NOT NULL REFERENCES reference.wards(ward_code),
    settlement_count INTEGER,
    visited_settlement_count INTEGER,
    target_population_under5 NUMERIC,
    etally_doses_administered NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed.hotspot_analysis_results (
    hotspot_analysis_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    statistic_name TEXT NOT NULL,
    statistic_value NUMERIC,
    p_value NUMERIC,
    is_significant BOOLEAN,
    spatial_weights_definition TEXT,
    geom geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audit layer: supports idempotent, traceable file ingestion.
CREATE TABLE IF NOT EXISTS audit.ingestion_file_registry (
    ingestion_file_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_file TEXT NOT NULL,
    source_type TEXT NOT NULL,
    file_checksum_sha256 TEXT NOT NULL,
    file_size_bytes BIGINT,
    source_record_count BIGINT,
    loaded_record_count BIGINT,
    ingestion_status TEXT NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_ingestion_file_version UNIQUE (source_file, file_checksum_sha256)
);
