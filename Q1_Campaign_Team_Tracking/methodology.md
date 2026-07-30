# Methodology

This document will record the reproducible methodology used for Question 1. Each section will identify the data used, the procedure applied, the assumptions made, and the validation performed.

The data audit documented in `notebooks/01_data_audit.ipynb` is the first validation stage. It inventories the supplied datasets and records descriptive quality observations before ingestion or analytical methods are implemented.

## Completed Data Audit

### Purpose

The data audit established a documented baseline for the supplied Q1 data before any ingestion, cleaning, spatial attribution, or coverage analysis.

### Checks Performed

- GPS track file inventory, record counts, team and campaign-date counts, schema consistency, missing values, coordinate ranges, and timestamp validity.
- Settlement masterlist row count, field inventory, `settlement_id` uniqueness, coordinate completeness, and administrative summaries.
- e-Tally row count, field inventory, duplicate key checks, missing-value counts, and descriptive suspicious-dose checks.
- Inaccessible-settlement row count, field inventory, and LGA and ward distributions.
- GeoPackage layer names, feature counts, coordinate reference system reporting, and geometry-validity checks.

### Why the Audit Precedes Processing Decisions

The audit records the observed structure and quality conditions of the source data before later methods are selected. This prevents missing values, suspicious dose records, or structural differences from being silently handled during processing and provides an evidence base for decisions that will be documented separately.

## Data Ingestion Methodology

The first ingestion component is GPS track loading. Implementation details, execution records, and any source-file exceptions will be documented after the ingestion process is run.

## GPS Quality Methodology

### Purpose

Identify and document GPS observations with potential quality concerns without changing or deleting records in `raw.gps_points_raw`.

### Rules and Assumptions

The QA layer evaluates calculated and reported speed, positional accuracy, campaign dates and assumed duty hours, sequence gaps, and stationary clusters. The campaign period is 9–13 March 2026. The provisional duty-hours window is 07:00–19:00, selected as an explicit operational assumption for flagging only. Thresholds and limitations are documented in `src/quality/README.md` and must be reviewed before downstream interpretation.

Quality rules are non-exclusive. Each observation is evaluated independently against all configured rules, allowing multiple quality flags to be assigned to the same GPS observation.

### Validation Approach

GPS points are ordered by team, logger, timestamp, and point identifier. Coordinate-derived speeds are compared with `speed_kmh` where available. Each concern is written as a separate record in `processed.gps_quality_flags`, allowing one point to carry multiple flags. Rule-level counts and percentages are exported for review; no flagged point is silently excluded.

## Settlement Attribution Methodology

Settlement attribution uses deterministic nearest-settlement proximity in PostGIS after transforming source EPSG:4326 geometry to EPSG:32632 for metre-based calculations. Validated results were 214 visited settlements for the 30 m baseline, 241 for the 60 m sensitivity scenario, and 216 for the urban accuracy-aware scenario. The 30 m baseline is the primary operational estimate; the 60 m scenario is retained to show sensitivity, while the urban adjustment does not materially change conclusions. Visit evidence is reconstructed from continuous, non-ambiguous team/date/settlement episodes; raw GPS records remain unchanged.

## Coverage Reconciliation Methodology

Using `baseline_30m`, reconciliation represented all 2,562 planned settlements. It found 742 strict agreements, 1,640 definitive disagreements, and 180 ambiguous GPS cases. GPS coverage was 8.35% and e-tally coverage was 78.69%; the 70.34 percentage-point gap is operationally substantial. GPS supports physical-presence evidence, while e-tally supports reported delivery and doses; neither alone proves both.

## Spatial Statistics Methodology

Requirement 5 uses `baseline_30m` settlement reconciliation to define a binary missed indicator: unvisited is 1 and visited is 0. The primary population excludes 180 ambiguous settlements (2,382 analysed settlements). Global Moran's I is the global diagnostic and Local Moran's I is used for local classification.

Primary weights are binary, row-standardized eight-nearest-neighbour weights calculated in EPSG:32632. Each analysis uses 999 fixed-seed permutations (seed `20260730`) and alpha 0.05. Raw permutation p-values and Benjamini-Hochberg FDR-adjusted p-values are both retained; FDR-adjusted inference defines the primary local labels. A 9,050 m distance-band matrix and an ambiguity-included k=8 population are sensitivity analyses. Results identify spatial concentration of the GPS-derived indicator only and do not establish causation, actual non-visit, misconduct, or vaccination outcomes.

The executed primary Global Moran's I was 0.046612 (expected I -0.000420; z-score 4.821064; permutation p=0.001). Although raw Local Moran screening identified 58 Low-Low visited clusters, 15 Low-High outliers, and one High-Low outlier, none of the 2,382 local tests remained significant after Benjamini-Hochberg FDR correction. Raw local classes are exploratory signals only.
