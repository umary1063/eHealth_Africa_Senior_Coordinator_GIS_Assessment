"""Idempotently load supplied Q1 reference datasets into PostGIS, one dataset at a time."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from src.ingestion.reference_db_connection import get_reference_connection, get_reference_database_settings, reference_cursor
from src.project_paths import project_root


LOGGER = logging.getLogger(__name__)
DATASETS = ("settlements", "wards", "lgas", "state", "all")
SETTLEMENT_REQUIRED_COLUMNS = {
    "settlement_id", "settlement_name", "settlement_type", "ward_code", "ward_name",
    "lga_code", "lga_name", "longitude", "latitude", "target_population_under5",
}


def log_step(message: str, *args: object) -> None:
    """Log an immediately flushed diagnostic marker around each native operation."""
    LOGGER.info(message, *args)
    for handler in logging.getLogger().handlers:
        handler.flush()
    sys.stdout.flush()
    sys.stderr.flush()


def package_version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def resolve_source_directory(value: str | None) -> Path:
    configured = value or os.environ.get("EHA_Q1_SOURCE_DIR")
    if not configured:
        raise ValueError("Provide --source-dir or set EHA_Q1_SOURCE_DIR to the supplied Q1 data directory.")
    source_directory = Path(configured).expanduser().resolve()
    expected = (source_directory / "settlement_masterlist.csv", source_directory / "boundaries.gpkg")
    missing = [path.name for path in expected if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required source file(s) in {source_directory}: {', '.join(missing)}")
    return source_directory


def diagnose(source_directory: Path) -> None:
    """Report dependency and connectivity diagnostics without loading any data."""
    log_step("DIAGNOSE: source directory resolved to %s", source_directory)
    for filename in ("settlement_masterlist.csv", "boundaries.gpkg"):
        path = source_directory / filename
        log_step("DIAGNOSE: %s (extension=%s, exists=%s)", path, path.suffix.lower(), path.is_file())
    details = {
        "geopandas_version": package_version("geopandas"),
        "fiona_version": package_version("fiona"),
        "pyogrio_version": package_version("pyogrio"),
        "gdal_version": "unavailable without importing Fiona",
    }
    try:
        import fiona  # Imported only in diagnostic/boundary execution paths.

        details["gdal_version"] = ".".join(map(str, fiona.__gdal_version__))
    except Exception as error:  # Diagnostic output must not hide a dependency problem.
        details["gdal_version"] = f"unavailable: {error}"
    log_step("DIAGNOSE: dependencies %s", json.dumps(details, sort_keys=True))
    settings = get_reference_database_settings()
    log_step("DIAGNOSE: backend=pg8000 python=%s host=%s port=%s database=%s", sys.executable, settings.host, settings.port, settings.database)
    log_step("DIAGNOSE: opening PostgreSQL connection with pg8000")
    connection = get_reference_connection()
    try:
        with reference_cursor(connection) as cursor:
            cursor.execute("SELECT 1")
            select_one = cursor.fetchone()[0]
            cursor.execute("SELECT (SELECT COUNT(*) FROM reference.states), (SELECT COUNT(*) FROM reference.lgas), (SELECT COUNT(*) FROM reference.wards), (SELECT COUNT(*) FROM raw.settlements)")
            counts = cursor.fetchone()
    finally:
        connection.close()
    log_step("DIAGNOSE: SELECT 1 result=%s; existing rows state=%s lgas=%s wards=%s settlements=%s", select_one, *counts)


def validate_settlements(settlements: pd.DataFrame) -> None:
    missing_columns = SETTLEMENT_REQUIRED_COLUMNS - set(settlements.columns)
    if missing_columns:
        raise ValueError(f"Settlement masterlist missing required columns: {', '.join(sorted(missing_columns))}")
    if settlements["settlement_id"].isna().any() or (settlements["settlement_id"].astype(str).str.strip() == "").any():
        raise ValueError("Settlement masterlist contains null or blank settlement_id values.")
    duplicate_count = int(settlements["settlement_id"].duplicated().sum())
    if duplicate_count:
        raise ValueError(f"Settlement masterlist contains {duplicate_count} duplicate settlement_id value(s).")
    for column, lower, upper in (("longitude", -180, 180), ("latitude", -90, 90)):
        values = pd.to_numeric(settlements[column], errors="coerce")
        if values.isna().any() or ((values < lower) | (values > upper)).any():
            raise ValueError(f"Settlement masterlist has missing or invalid {column} values.")


def load_settlements(connection, source_directory: Path) -> dict[str, int]:
    path = source_directory / "settlement_masterlist.csv"
    log_step("SETTLEMENTS: preflighting required LGA and ward parent records")
    with reference_cursor(connection) as cursor:
        cursor.execute("SELECT (SELECT COUNT(*) FROM reference.lgas), (SELECT COUNT(*) FROM reference.wards)")
        lga_count, ward_count = cursor.fetchone()
    if not lga_count or not ward_count:
        raise RuntimeError(
            "Settlement loading requires database-resident LGAs and wards because raw.settlements enforces foreign keys. "
            "Run --dataset all, or load state, lgas, and wards first."
        )
    log_step("SETTLEMENTS: reading %s with pandas", path)
    settlements = pd.read_csv(path)
    log_step("SETTLEMENTS: read %s source row(s); validating identifiers and coordinates", len(settlements))
    validate_settlements(settlements)
    log_step("SETTLEMENTS: creating staging records")
    records = [
        (row.settlement_id, row.settlement_name, row.settlement_type, row.ward_code, row.ward_name,
         row.lga_code, row.lga_name, row.longitude, row.latitude, row.target_population_under5,
         row.longitude, row.latitude, row_number)
        for row_number, row in enumerate(settlements.itertuples(index=False), start=2)
    ]
    log_step("SETTLEMENTS: COPY/load upsert into raw.settlements")
    with reference_cursor(connection) as cursor:
        cursor.executemany(
            """INSERT INTO raw.settlements (settlement_id, settlement_name, settlement_type, ward_code, ward_name,
               lga_code, lga_name, longitude, latitude, target_population_under5, geom, source_file, source_row_number)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                   ST_SetSRID(ST_MakePoint(%s, %s), 4326), 'settlement_masterlist.csv', %s)
               ON CONFLICT (settlement_id) DO UPDATE SET settlement_name=EXCLUDED.settlement_name,
                   settlement_type=EXCLUDED.settlement_type, ward_code=EXCLUDED.ward_code, ward_name=EXCLUDED.ward_name,
                   lga_code=EXCLUDED.lga_code, lga_name=EXCLUDED.lga_name, longitude=EXCLUDED.longitude,
                   latitude=EXCLUDED.latitude, target_population_under5=EXCLUDED.target_population_under5,
                   geom=EXCLUDED.geom, source_file=EXCLUDED.source_file, source_row_number=EXCLUDED.source_row_number""",
            records,
        )
    return {"settlements_expected": len(settlements)}


def iter_boundary_features(source_directory: Path, layer: str):
    """Read one feature at a time with Fiona; never materialise a whole boundary layer."""
    path = source_directory / "boundaries.gpkg"
    log_step("%s: importing Fiona for feature-by-feature reading", layer.upper())
    import fiona

    log_step("%s: opening %s layer from %s", layer.upper(), layer, path)
    with fiona.open(path, layer=layer) as collection:
        for feature in collection:
            yield feature


def _boundary_sql(dataset: str) -> str:
    if dataset == "state":
        return """INSERT INTO reference.states (state_name, geom) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                  ON CONFLICT (state_name) DO UPDATE SET geom=EXCLUDED.geom"""
    if dataset == "lgas":
        return """INSERT INTO reference.lgas (lga_code, lga_name, lga_type, state_name, geom)
                  VALUES (%s, %s, %s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)))
                  ON CONFLICT (lga_code) DO UPDATE SET lga_name=EXCLUDED.lga_name, lga_type=EXCLUDED.lga_type,
                      state_name=EXCLUDED.state_name, geom=EXCLUDED.geom"""
    return """INSERT INTO reference.wards (ward_code, ward_name, lga_code, lga_name, lga_type, state_name, geom)
              VALUES (%s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
              ON CONFLICT (ward_code) DO UPDATE SET ward_name=EXCLUDED.ward_name, lga_code=EXCLUDED.lga_code,
                  lga_name=EXCLUDED.lga_name, lga_type=EXCLUDED.lga_type, state_name=EXCLUDED.state_name, geom=EXCLUDED.geom"""


def load_boundary_dataset(connection, source_directory: Path, dataset: str) -> dict[str, int]:
    layer = "state" if dataset == "state" else dataset
    log_step("%s: creating staging records", dataset.upper())
    records: list[tuple] = []
    repaired = 0
    log_step("%s: COPY/load each feature into PostGIS", dataset.upper())
    with reference_cursor(connection) as cursor:
        for feature in iter_boundary_features(source_directory, layer):
            properties = feature["properties"]
            # Fiona 1.10 returns a Geometry mapping object rather than a plain
            # JSON-serialisable dictionary.
            geometry_json = json.dumps(dict(feature["geometry"]))
            cursor.execute("SELECT ST_IsValid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))", (geometry_json,))
            is_valid = bool(cursor.fetchone()[0])
            if not is_valid:
                repaired += 1
                geometry_json = json.dumps(dict(feature["geometry"]))
            if dataset == "state":
                records.append((properties["state_name"], geometry_json))
            elif dataset == "lgas":
                records.append((properties["lga_code"], properties["lga_name"], properties["lga_type"], properties["state_name"], geometry_json))
            else:
                records.append((properties["ward_code"], properties["ward_name"], properties["lga_code"], properties["lga_name"], properties["lga_type"], properties["state_name"], geometry_json))
        if repaired:
            raise ValueError(f"{dataset} contains {repaired} invalid feature(s); review geometry repair before loading.")
        cursor.executemany(_boundary_sql(dataset), records)
    return {f"{dataset}_source_records": len(records), f"{dataset}_geometries_repaired": repaired}


def collect_validation(connection) -> dict[str, int]:
    queries = {
        "settlements_loaded": "SELECT COUNT(*) FROM raw.settlements",
        "wards_loaded": "SELECT COUNT(*) FROM reference.wards",
        "lgas_loaded": "SELECT COUNT(*) FROM reference.lgas",
        "state_records_loaded": "SELECT COUNT(*) FROM reference.states",
        "duplicate_settlement_ids": "SELECT COUNT(*) - COUNT(DISTINCT settlement_id) FROM raw.settlements",
        "null_settlement_geometries": "SELECT COUNT(*) FROM raw.settlements WHERE geom IS NULL",
        "invalid_settlement_geometries": "SELECT COUNT(*) FROM raw.settlements WHERE NOT ST_IsValid(geom)",
        "invalid_ward_geometries": "SELECT COUNT(*) FROM reference.wards WHERE NOT ST_IsValid(geom)",
        "invalid_lga_geometries": "SELECT COUNT(*) FROM reference.lgas WHERE NOT ST_IsValid(geom)",
        "invalid_state_geometries": "SELECT COUNT(*) FROM reference.states WHERE NOT ST_IsValid(geom)",
    }
    with reference_cursor(connection) as cursor:
        metrics: dict[str, int] = {}
        for name, query in queries.items():
            cursor.execute(query)
            metrics[name] = int(cursor.fetchone()[0])
        return metrics


def load_dataset(source_directory: Path, dataset: str) -> dict[str, int]:
    """Run exactly one dataset in one transaction, then validate the committed database state."""
    log_step("%s: opening PostgreSQL connection", dataset.upper())
    connection = get_reference_connection()
    try:
        if dataset == "settlements":
            metrics = load_settlements(connection, source_directory)
        else:
            metrics = load_boundary_dataset(connection, source_directory, dataset)
        log_step("%s: committing transaction", dataset.upper())
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    log_step("%s: opening PostgreSQL connection for row-count validation", dataset.upper())
    connection = get_reference_connection()
    try:
        metrics.update(collect_validation(connection))
    finally:
        connection.close()
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", help="Directory containing boundaries.gpkg and settlement_masterlist.csv.")
    parser.add_argument("--dataset", choices=DATASETS, default="all", help="One target per transaction; use all to run each target independently.")
    parser.add_argument("--diagnose", action="store_true", help="Report paths, dependency versions, GDAL, and PostgreSQL connectivity without loading data.")
    arguments = parser.parse_args()
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
    log_step("Starting reference-data loader (project root: %s)", project_root())
    source_directory = resolve_source_directory(arguments.source_dir)
    log_step("Discovered source files in %s", source_directory)
    if arguments.diagnose:
        diagnose(source_directory)
        return
    targets = ("state", "lgas", "wards", "settlements") if arguments.dataset == "all" else (arguments.dataset,)
    metrics: dict[str, int] = {}
    for target in targets:
        metrics.update(load_dataset(source_directory, target))
    print(json.dumps(metrics, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
