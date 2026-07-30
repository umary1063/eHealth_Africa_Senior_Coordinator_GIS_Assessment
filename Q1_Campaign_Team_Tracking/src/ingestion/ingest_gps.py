"""Idempotent COPY-based ingestion of supplied GPS track CSV files into PostGIS."""

from __future__ import annotations

import argparse
import csv
import logging
import os
from pathlib import Path
from typing import Iterable

from .db_connection import get_connection
from .ingestion_registry import calculate_sha256, file_already_loaded, register_successful_ingestion, source_file_has_other_loaded_version


LOGGER = logging.getLogger(__name__)
EXPECTED_COLUMNS = {"team_id", "logger_id", "timestamp", "longitude", "latitude", "accuracy_m", "speed_kmh"}
STAGE_TABLE_SQL = """
CREATE TEMP TABLE gps_copy_stage (
    team_id TEXT, logger_id TEXT, observed_at_text TEXT, longitude_text TEXT,
    latitude_text TEXT, accuracy_m_text TEXT, speed_kmh_text TEXT,
    source_file TEXT NOT NULL, source_row_number INTEGER NOT NULL
) ON COMMIT DROP
"""
COPY_SQL = """
COPY gps_copy_stage (
    team_id, logger_id, observed_at_text, longitude_text, latitude_text,
    accuracy_m_text, speed_kmh_text, source_file, source_row_number
) FROM STDIN
"""
MERGE_SQL = """
INSERT INTO raw.gps_points_raw (
    team_id, logger_id, observed_at, longitude, latitude, accuracy_m, speed_kmh,
    geom, source_file, source_row_number
)
SELECT
    team_id, logger_id,
    NULLIF(observed_at_text, '')::timestamp,
    NULLIF(longitude_text, '')::numeric,
    NULLIF(latitude_text, '')::numeric,
    NULLIF(accuracy_m_text, '')::numeric,
    NULLIF(speed_kmh_text, '')::numeric,
    ST_SetSRID(ST_MakePoint(NULLIF(longitude_text, '')::double precision, NULLIF(latitude_text, '')::double precision), 4326),
    source_file, source_row_number
FROM gps_copy_stage
ON CONFLICT (source_file, source_row_number) DO NOTHING
"""


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def configured_gps_directory() -> Path:
    gps_directory = Path(os.environ.get("EHA_Q1_GPS_DIR", project_root() / "data" / "raw" / "gps"))
    if not gps_directory.is_dir():
        raise NotADirectoryError(f"GPS source directory not found: {gps_directory}")
    return gps_directory


def discover_gps_files(gps_directory: Path) -> list[Path]:
    files = sorted(gps_directory.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No GPS CSV files found in: {gps_directory}")
    return files


def validate_columns(file_path: Path) -> None:
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        actual_columns = set(csv.DictReader(handle).fieldnames or [])
    missing_columns = EXPECTED_COLUMNS - actual_columns
    if missing_columns:
        raise ValueError(f"{file_path.name} is missing required columns: {', '.join(sorted(missing_columns))}")


def batched_rows(reader: csv.DictReader, batch_size: int) -> Iterable[list[dict[str, str]]]:
    batch: list[dict[str, str]] = []
    for row in reader:
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def copy_batch(cursor, rows: list[dict[str, str]], source_file: str, start_row: int) -> None:
    """Stream one bounded CSV batch into a temporary PostgreSQL staging table."""
    with cursor.copy(COPY_SQL) as copy:
        for offset, row in enumerate(rows):
            copy.write_row((
                row.get("team_id"), row.get("logger_id"), row.get("timestamp"),
                row.get("longitude"), row.get("latitude"), row.get("accuracy_m"),
                row.get("speed_kmh"), source_file, start_row + offset,
            ))
    cursor.execute(MERGE_SQL)
    cursor.execute("TRUNCATE gps_copy_stage")


def ingest_file(file_path: Path, gps_directory: Path, batch_size: int) -> bool:
    """Load one file atomically; failed files roll back and are never registered."""
    validate_columns(file_path)
    source_file = file_path.relative_to(gps_directory).as_posix()
    checksum_sha256 = calculate_sha256(file_path)

    try:
        with get_connection() as connection:
            if file_already_loaded(connection, source_file, checksum_sha256):
                LOGGER.info("Skipping previously ingested file: %s", source_file)
                return False
            if source_file_has_other_loaded_version(connection, source_file, checksum_sha256):
                raise RuntimeError(f"{source_file} has a different successfully ingested checksum; review it before loading.")

            source_record_count = 0
            with connection.cursor() as cursor:
                cursor.execute(STAGE_TABLE_SQL)
                with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
                    reader = csv.DictReader(handle)
                    source_row_number = 2
                    for batch in batched_rows(reader, batch_size):
                        copy_batch(cursor, batch, source_file, source_row_number)
                        source_record_count += len(batch)
                        source_row_number += len(batch)
                cursor.execute("SELECT COUNT(*) FROM raw.gps_points_raw WHERE source_file = %s", (source_file,))
                loaded_record_count = int(cursor.fetchone()[0])

            register_successful_ingestion(
                connection, source_file=source_file, checksum_sha256=checksum_sha256,
                file_size_bytes=file_path.stat().st_size, source_record_count=source_record_count,
                loaded_record_count=loaded_record_count,
            )
        LOGGER.info("Ingested %s: source records=%s, raw records=%s", source_file, source_record_count, loaded_record_count)
        return True
    except Exception:
        LOGGER.exception("Failed ingestion for %s; transaction rolled back and file was not registered.", source_file)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=10_000)
    arguments = parser.parse_args()
    if arguments.batch_size <= 0:
        raise ValueError("--batch-size must be a positive integer.")
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    gps_directory = configured_gps_directory()
    files = discover_gps_files(gps_directory)
    LOGGER.info("Discovered %s GPS CSV file(s) in %s", len(files), gps_directory)
    loaded = sum(ingest_file(path, gps_directory, arguments.batch_size) for path in files)
    LOGGER.info("GPS ingestion complete: %s new file(s) loaded", loaded)


if __name__ == "__main__":
    main()
