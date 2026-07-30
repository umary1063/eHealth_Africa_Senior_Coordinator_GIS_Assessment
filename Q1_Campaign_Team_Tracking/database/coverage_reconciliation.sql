CREATE TABLE IF NOT EXISTS raw.etally_records_unmatched (etally_unmatched_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, campaign_date DATE, team_id TEXT, settlement_id TEXT, ward_code TEXT, lga_name TEXT, target_population_under5 INTEGER, doses_administered INTEGER, source_file TEXT NOT NULL, source_row_number INTEGER NOT NULL, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, UNIQUE(source_file,source_row_number));
CREATE TABLE IF NOT EXISTS processed.settlement_coverage_reconciliation (
 settlement_id TEXT PRIMARY KEY REFERENCES raw.settlements(settlement_id), settlement_name TEXT, ward_code TEXT, ward_name TEXT, lga_name TEXT,
 gps_visit_status TEXT NOT NULL, gps_confidence_status TEXT NOT NULL, etally_report_status TEXT NOT NULL, etally_row_count INTEGER NOT NULL,
 reported_doses_all_linked NUMERIC NOT NULL, reported_doses_plausible_only NUMERIC NOT NULL, dose_quality_flag BOOLEAN NOT NULL,
 reconciliation_class TEXT NOT NULL, discrepancy_flag BOOLEAN NOT NULL, explanatory_notes TEXT, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS processed.ward_coverage_reconciliation (
 ward_code TEXT PRIMARY KEY REFERENCES reference.wards(ward_code), ward_name TEXT, lga_name TEXT, planned_settlements INTEGER NOT NULL,
 gps_visited_settlements INTEGER NOT NULL, gps_ambiguous_settlements INTEGER NOT NULL, gps_unvisited_settlements INTEGER NOT NULL,
 etally_reported_settlements INTEGER NOT NULL, gps_coverage_pct NUMERIC NOT NULL, etally_coverage_pct NUMERIC NOT NULL,
 absolute_percentage_point_difference NUMERIC NOT NULL, discrepancy_severity TEXT NOT NULL, reported_doses_all_linked NUMERIC NOT NULL,
 reported_doses_plausible_only NUMERIC NOT NULL, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
