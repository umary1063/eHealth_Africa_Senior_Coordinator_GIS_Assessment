# GPS Track Ingestion

## Purpose

This component loads supplied GPS track CSV files into `raw.gps_points_raw` in PostgreSQL/PostGIS. It preserves supplied values, source-file identity, and source row numbers without applying quality filters.

## Execution Flow

1. Resolve the GPS directory from `EHA_Q1_GPS_DIR`, or from the project-relative default `data/raw/gps`.
2. Discover CSV files in deterministic order and validate the required source columns.
3. Calculate a SHA256 checksum for each source file.
4. Insert source rows and EPSG:4326 point geometries into the raw layer.
5. Register each successfully committed file in `audit.ingestion_file_registry`.

Run from the `Q1_Campaign_Team_Tracking` directory after the database schema has been initialized:

```text
POSTGRES_PASSWORD=<local-password> python -m src.ingestion.ingest_gps
```

Set `EHA_Q1_GPS_DIR` when the supplied raw GPS files are retained outside the project-relative `data/raw/gps` directory.

## Idempotency Design

The ingestion registry records the source-file path and SHA256 checksum for each successful load. A matching successful registry entry causes the file to be skipped on later runs. In addition, the raw table enforces a unique `(source_file, source_row_number)` constraint, preventing duplicate point rows if a prior run was interrupted before registration. A changed checksum for an already registered file is stopped for review rather than being silently mixed with an earlier source version.
