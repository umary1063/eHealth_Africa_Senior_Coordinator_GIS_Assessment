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
- **Attribution use:** `settlement_id` is the settlement-attribution key; coordinates are retained in EPSG:4326 and transformed to EPSG:32632 for distance calculations.

## E-Tally

- **Size:** 2,023 records.
- **Fields:** `campaign_date`, `team_id`, `settlement_id`, `ward_code`, `lga_name`, `target_population_under5`, `doses_administered`.
- **Audit findings:** No duplicate `campaign_date` + `team_id` + `settlement_id` combinations were recorded. The audit recorded seven missing values and 201 potentially suspicious dose rows.
- **Quality considerations:** Missing values and potentially suspicious dose rows require documented review during subsequent processing; they are not treated as deleted records.
- **Executed reconciliation:** 2,023 supplied rows were retained; seven unmatched IDs were preserved separately. Reported doses remain unchanged, with all-linked and plausible-only totals reported separately.

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

## Spatial Statistics Outputs

- **Analysis population:** Primary output excludes 180 GPS-ambiguous settlements and contains 2,382 unique planned settlements; the ambiguity sensitivity contains all 2,562.
- **`global_moran_summary.csv`:** scenario, weights specification, population, missed/visited counts, permutation settings, Global Moran's I, expected I, z-score, and permutation p-value.
- **`local_moran_results.csv`:** one row per analysed settlement and scenario with projected coordinates, missed indicator, neighbour count, Local Moran's I, quadrant, spatial lag, raw and FDR-adjusted p-values, significance flags, and raw/FDR local labels.
- **`cluster_summary.csv`:** local class counts by scenario and raw or FDR-adjusted inference.
- **`weights_diagnostics.csv`:** KNN and distance-band neighbour, island, connectivity, and distance diagnostics.
- **Executed interpretation:** The primary Global Moran's I is 0.046612 (permutation p=0.001). Raw local classes are retained, while all 2,382 primary local tests are `Not significant` after Benjamini-Hochberg FDR adjustment.

## Decision-Product Evidence Confidence

- **High confidence:** corroborated GPS and e-tally evidence, or a directly measured source metric stated within its own scope.
- **Moderate confidence:** one source provides evidence while the other is unavailable or ambiguous.
- **Low confidence:** source disagreement, ambiguous attribution, material QA concerns, or unmatched identifiers.
- **Unknown:** insufficient evidence for an operational conclusion.
- **Interpretation rule:** confidence describes evidence sufficiency; it does not convert missing GPS evidence into proof that a settlement was missed.
