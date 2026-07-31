-- Scenario-specific settlement attribution and reconstructed visit evidence.
-- Distances are measured in EPSG:32632 (UTM zone 32N); source geometries remain EPSG:4326.

CREATE TABLE IF NOT EXISTS processed.gps_settlement_attributions (
    scenario_name TEXT NOT NULL,
    gps_track_point_id BIGINT NOT NULL REFERENCES raw.gps_points_raw(gps_track_point_id),
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    observed_at TIMESTAMP NOT NULL,
    team_id TEXT,
    campaign_date DATE NOT NULL,
    distance_to_settlement_m NUMERIC NOT NULL,
    applicable_tolerance_m NUMERIC NOT NULL,
    candidate_count INTEGER NOT NULL,
    attribution_method TEXT NOT NULL,
    confidence_class TEXT NOT NULL,
    baseline_eligible BOOLEAN NOT NULL,
    impossible_speed_flag BOOLEAN NOT NULL DEFAULT FALSE,
    accuracy_quality_flag BOOLEAN NOT NULL DEFAULT FALSE,
    reported_speed_disagreement_flag BOOLEAN NOT NULL DEFAULT FALSE,
    stationary_cluster_flag BOOLEAN NOT NULL DEFAULT FALSE,
    gps_gap_flag BOOLEAN NOT NULL DEFAULT FALSE,
    outside_campaign_hours_flag BOOLEAN NOT NULL DEFAULT FALSE,
    source_file_date_mismatch_flag BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (scenario_name, gps_track_point_id),
    CONSTRAINT chk_attribution_scenario CHECK (scenario_name IN ('baseline_30m', 'sensitivity_60m', 'urban_accuracy_aware')),
    CONSTRAINT chk_attribution_confidence CHECK (confidence_class IN ('high', 'review', 'ambiguous'))
);

CREATE TABLE IF NOT EXISTS processed.settlement_visit_episodes (
    scenario_name TEXT NOT NULL,
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    team_id TEXT,
    campaign_date DATE NOT NULL,
    episode_number INTEGER NOT NULL,
    point_count INTEGER NOT NULL,
    first_observed_at TIMESTAMP NOT NULL,
    last_observed_at TIMESTAMP NOT NULL,
    dwell_duration_minutes NUMERIC NOT NULL,
    maximum_internal_gap_minutes NUMERIC,
    is_confirmed_visit BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (scenario_name, settlement_id, team_id, campaign_date, episode_number)
);

CREATE TABLE IF NOT EXISTS processed.settlement_visit_summaries (
    scenario_name TEXT NOT NULL,
    settlement_id TEXT NOT NULL REFERENCES raw.settlements(settlement_id),
    visit_classification TEXT NOT NULL,
    team_count INTEGER NOT NULL DEFAULT 0,
    first_observed_at TIMESTAMP,
    last_observed_at TIMESTAMP,
    dwell_duration_minutes NUMERIC NOT NULL DEFAULT 0,
    eligible_gps_point_count INTEGER NOT NULL DEFAULT 0,
    nearest_attribution_distance_m NUMERIC,
    confidence_class TEXT NOT NULL,
    ambiguous_attribution_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (scenario_name, settlement_id),
    CONSTRAINT chk_visit_classification CHECK (visit_classification IN ('visited', 'unvisited', 'ambiguous'))
);

CREATE INDEX IF NOT EXISTS ix_attributions_settlement_scenario
    ON processed.gps_settlement_attributions (scenario_name, settlement_id);
CREATE INDEX IF NOT EXISTS ix_attributions_team_date
    ON processed.gps_settlement_attributions (scenario_name, team_id, campaign_date, observed_at);
CREATE INDEX IF NOT EXISTS ix_visit_episodes_scenario_settlement
    ON processed.settlement_visit_episodes (scenario_name, settlement_id);
CREATE INDEX IF NOT EXISTS ix_visit_summaries_scenario_classification
    ON processed.settlement_visit_summaries (scenario_name, visit_classification);
CREATE INDEX IF NOT EXISTS ix_gps_points_projected_32632
    ON raw.gps_points_raw USING GIST (ST_Transform(geom, 32632));
CREATE INDEX IF NOT EXISTS ix_settlements_projected_32632
    ON raw.settlements USING GIST (ST_Transform(geom, 32632));
