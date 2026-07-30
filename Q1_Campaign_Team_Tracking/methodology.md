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

_To be completed during implementation._

## Settlement Attribution Methodology

_To be completed during implementation._

## Coverage Reconciliation Methodology

_To be completed during implementation._

## Spatial Statistics Methodology

_To be completed during implementation._
