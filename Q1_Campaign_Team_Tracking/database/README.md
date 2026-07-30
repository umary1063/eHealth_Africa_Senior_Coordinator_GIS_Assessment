# Q1 Spatial Database Design

## Purpose

This directory defines the initial PostgreSQL/PostGIS design for Question 1. The schema separates source records, administrative reference data, derived operational products, and ingestion audit metadata so that processing can remain traceable and reproducible.

## Files

- `schema.sql` creates the PostGIS extension, logical schemas, tables, primary keys, foreign keys, geometry columns, and ingestion-registry constraints.
- `indexes.sql` creates spatial and relational indexes after the schema is created.

## Table Roles

| Layer | Role |
|---|---|
| `reference` | Ward, LGA, and state boundaries used to provide administrative geography. |
| `raw` | Source GPS tracks, settlement masterlist, e-Tally records, and inaccessible-settlement records, with source-file metadata retained. |
| `processed` | Cleaned GPS records, quality flags, settlement-visit classifications, coverage summaries, and hotspot-analysis results. |
| `audit` | File-level ingestion registry supporting traceable and idempotent loading. |

## Relationships

Administrative boundaries provide the reference hierarchy from state to LGA to ward. The settlement masterlist is the primary settlement reference and links e-Tally, inaccessible-settlement, visit-classification, coverage, and hotspot records through `settlement_id`. GPS quality flags and cleaned GPS records reference their corresponding raw GPS point. The ingestion registry records each source-file version independently of its loaded records.

The design establishes storage and traceability only. It does not load data, apply quality thresholds, or select spatial-attribution or hotspot-analysis methods.

## Local Development Database

The Q1 local database uses Docker Compose with PostgreSQL and PostGIS. Set the required database password in your shell, then start the service from the `Q1_Campaign_Team_Tracking` directory:

```text
POSTGRES_PASSWORD=<choose-a-local-password> docker compose up -d
```

Optional environment variables are `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PORT`. No credentials are committed to the repository.

On the first start with an empty Docker volume, PostgreSQL runs the ordered scripts in `database/init/`. `001_create_extensions.sql` enables PostGIS; `002_create_schema.sql` applies the version-controlled `database/schema.sql` file. The named Docker volume retains the database between container restarts. To apply the initialization sequence again, use a new or intentionally removed volume.

This arrangement gives each developer the same database engine, PostGIS capability, initialization order, and schema definition without requiring a manually configured local PostgreSQL installation.
