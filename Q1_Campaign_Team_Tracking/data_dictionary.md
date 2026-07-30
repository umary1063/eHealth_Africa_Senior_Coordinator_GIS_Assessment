# Data Dictionary

This dictionary records the confirmed source dataset structure and the descriptive findings from `outputs/tables/data_audit_summary.csv`. It does not define derived fields or processing rules.

## GPS Tracks

- **Size:** 160 CSV files; 956,702 records; 32 teams; 24 observed campaign dates.
- **Fields:** `team_id`, `logger_id`, `timestamp`, `longitude`, `latitude`, `accuracy_m`, `speed_kmh`.
- **Audit findings:** One schema variant was observed across the files. The audit recorded 19,025 missing values, zero invalid timestamps, and zero coordinates outside global valid ranges.
- **Quality consideration:** Missing values are present and must be retained for explicit handling in later quality-assurance work.

## Settlement Masterlist

- **Size:** 2,562 records.
- **Fields:** `settlement_id`, `settlement_name`, `settlement_type`, `ward_code`, `ward_name`, `lga_code`, `lga_name`, `longitude`, `latitude`, `target_population_under5`.
- **Audit findings:** No duplicate `settlement_id` values and no records with missing coordinates were recorded.

## E-Tally

- **Size:** 2,023 records.
- **Fields:** `campaign_date`, `team_id`, `settlement_id`, `ward_code`, `lga_name`, `target_population_under5`, `doses_administered`.
- **Audit findings:** No duplicate `campaign_date` + `team_id` + `settlement_id` combinations were recorded. The audit recorded seven missing values and 201 potentially suspicious dose rows.
- **Quality considerations:** Missing values and potentially suspicious dose rows require documented review during subsequent processing; they are not treated as deleted records.

## Inaccessible Settlements

- **Size:** 75 records.
- **Fields:** `settlement_id`, `settlement_name`, `ward_code`, `ward_name`, `lga_name`, `security_classification`, `date_classified`.
- **Audit findings:** No missing values were recorded.

## Administrative Boundaries

- **Source:** `boundaries.gpkg`.
- **Layers and feature counts:** `wards` (40), `lgas` (4), and `state` (1).
- **Known fields:**
  - `wards`: `ward_code`, `ward_name`, `lga_code`, `lga_name`, `lga_type`, `state_name`
  - `lgas`: `lga_code`, `lga_name`, `lga_type`, `state_name`
  - `state`: `state_name`
- **Audit findings:** No invalid geometries were recorded in any layer.
