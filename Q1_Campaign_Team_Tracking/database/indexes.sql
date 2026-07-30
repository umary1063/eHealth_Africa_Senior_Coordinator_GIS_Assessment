-- Q1 Campaign Team Tracking and Coverage Reconciliation
-- Indexes for spatial lookup, source-traceability checks, and table relationships.

CREATE INDEX IF NOT EXISTS ix_states_geom
    ON reference.states USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_lgas_geom
    ON reference.lgas USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_wards_geom
    ON reference.wards USING GIST (geom);

CREATE INDEX IF NOT EXISTS ix_gps_points_raw_geom
    ON raw.gps_points_raw USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_gps_points_raw_team_observed
    ON raw.gps_points_raw (team_id, observed_at);
CREATE INDEX IF NOT EXISTS ix_settlements_geom
    ON raw.settlements USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_settlements_ward
    ON raw.settlements (ward_code);
CREATE INDEX IF NOT EXISTS ix_etally_settlement
    ON raw.etally_records (settlement_id);
CREATE INDEX IF NOT EXISTS ix_etally_campaign_team
    ON raw.etally_records (campaign_date, team_id);
CREATE INDEX IF NOT EXISTS ix_inaccessible_settlement
    ON raw.inaccessible_settlements (settlement_id);

CREATE INDEX IF NOT EXISTS ix_cleaned_gps_points_geom
    ON processed.cleaned_gps_points USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_gps_quality_flags_point
    ON processed.gps_quality_flags (gps_track_point_id);
CREATE INDEX IF NOT EXISTS ix_settlement_visit_classification_settlement
    ON processed.settlement_visit_classification (settlement_id);
CREATE INDEX IF NOT EXISTS ix_settlement_coverage_summaries_settlement
    ON processed.settlement_coverage_summaries (settlement_id);
CREATE INDEX IF NOT EXISTS ix_ward_coverage_summaries_ward
    ON processed.ward_coverage_summaries (ward_code);
CREATE INDEX IF NOT EXISTS ix_hotspot_analysis_results_geom
    ON processed.hotspot_analysis_results USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_hotspot_analysis_results_settlement
    ON processed.hotspot_analysis_results (settlement_id);

CREATE INDEX IF NOT EXISTS ix_ingestion_file_registry_status
    ON audit.ingestion_file_registry (source_type, ingestion_status);
