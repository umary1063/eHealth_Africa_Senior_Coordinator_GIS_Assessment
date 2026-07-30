"""Idempotent ingestion of supplied GPS track CSV files into PostGIS."""

from __future__ import annotations

import argparse
import csv
import logging
import os
from pathlib import Path
from typing import Iterable

from .db_connection import get_connection
from .ingestion_registry import (
    calculate_sha256,
    file_already_loaded,
    register_successful_ingestion,
    source_file_has_other_loaded_version,
)


LOGGER = logging.getLogger(__name__)
EXPECTED_COLUMNS = {
    "team_id",
    "logger_id",
    "timestamp",
    "longitude",
    "latitude",
    "accuracy_m",
    "speed_kmh",
}
INSERT_SQL = """
    INSERT INTO raw.gps_points_raw (
        team_id,
        logger_id,
        observed_at,
        longitude,
        latitude,
        accuracy_m,
        speed_kmh,
        geom,
        source_file,
        source_row_number
    )
    VALUES (
        %s,
        %s,
        NULLIF(%s, '')::timestamp,
        NULLIF(%s, '')::numeric,
        NULLIF(%s, '')::numeric,
        NULLIF(%s, '')::numeric,
        NULLIF(%s, '')::numeric,
        ST_SetSRID(
            ST_MakePoint(NULLIF(%s, '')::double precision, NULLIF(%s, '')::double precision),
            4326
        ),
        %s,
        %s
    )
    ON CONFLICT (source_file, source_row_number) DO NOTHING
"""


def project_root() -> Path:
    """Return the Q1 project directory from this source file location."""
    return Path(__file__).resolve().parents[2]


def configured_gps_directory() -> Path:
    """Resolve the configurable GPS source directory without personal paths."""
    default_directory = project_root() / "data" / "raw" / "gps"
    gps_directory = Path(os.environ.get("EHA_Q1_GPS_DIR", default_directory))
    if not gps_directory.exists():
        raise FileNotFoundError(
            f"GPS source directory not found: {gps_directory}. "
            "Set EHA_Q1_GPS_DIR or place the supplied CSV files in data/raw/gps."
        )
    if not gps_directory.is_dir():
        raise NotADirectoryError(f"GPS source path is not a directory: {gps_directory}")
    return gps_directory


def discover_gps_files(gps_directory: Path) -> list[Path]:
    """Return GPS CSV files in deterministic order."""
    files = sorted(gps_directory.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No GPS CSV files found in: {gps_directory}")
    return files


def validate_columns(file_path: Path) -> None:
    """Fail clearly if a GPS file does not include the required source columns."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        actual_columns = set(reader.fieldnames or [])

    missing_columns = EXPECTED_COLUMNS - actual_columns
    if missing_columns:
        raise ValueError(
            f"{file_path.name} is missing required columns: {', '.join(sorted(missing_columns))}"
        )


def row_parameters(
    rows: Iterable[dict[str, str]], source_file: str, start_row_number: int
) -> list[tuple[str | int | None, ...]]:
    """Create database parameters while retaining every source value and row identity."""
    parameters = []
    for offset, row in enumerate(rows):
        parameters.append(
            (
                row.get("team_id"),
                row.get("logger_id"),
                row.get("timestamp"),
                row.get("longitude"),
                row.get("latitude"),
                row.get("accuracy_m"),
                row.get("speed_kmh"),
                row.get("longitude"),
                row.get("latitude"),
                source_file,
                start_row_number + offset,
            )
        )
    return parameters


def batched_rows(reader: csv.DictReader, batch_size: int) -> Iterable[list[dict[str, str]]]:
    """Yield source rows in bounded batches without filtering or changing them."""
    batch: list[dict[str, str]] = []
    for row in reader:
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def ingest_file(file_path: Path, gps_directory: Path, batch_size: int) -> bool:
    """Ingest one GPS file transactionally; return True when a new version is loaded."""
    validate_columns(file_path)
    source_file = file_path.relative_to(gps_directory).as_posix()
    checksum_sha256 = calculate_sha256(file_path)

    with get_connection() as connection:
        if file_already_loaded(connection, source_file, checksum_sha256):
            LOGGER.info("Skipping previously ingested file: %s", source_file)
            return False
        if source_file_has_other_loaded_version(connection, source_file, checksum_sha256):
            raise RuntimeError(
                f"{source_file} has a different successfully ingested checksum. "
                "Review the source version before loading it."
            )

        source_record_count = 0
        with connection.cursor() as cursor:
            with file_path.open("r", encoding="utf-8-sig", newline="") as source_handle:
                reader = csv.DictReader(source_handle)
                source_row_number = 2  # Row 1 is the CSV header.
                for batch in batched_rows(reader, batch_size):
                    cursor.executemany(
                        INSERT_SQL,
                        row_parameters(batch, source_file, source_row_number),
                    )
                    source_record_count += len(batch)
                    source_row_number += len(batch)

            cursor.execute(
                "SELECT COUNT(*) FROM raw.gps_points_raw WHERE source_file = %s",
                (source_file,),
            )
            loaded_record_count = int(cursor.fetchone()[0])

        register_successful_ingestion(
            connection,
            source_file=source_file,
            checksum_sha256=checksum_sha256,
            file_size_bytes=file_path.stat().st_size,
            source_record_count=source_record_count,
            loaded_record_count=loaded_record_count,
        )

    LOGGER.info(
        "Ingested %s: source records=%s, raw records=%s",
        source_file,
        source_record_count,
        loaded_record_count,
    )
    return True


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10_000,
        help="Number of CSV rows submitted to PostgreSQL per batch (default: 10000).",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    arguments = parse_arguments()
    if arguments.batch_size <= 0:
        raise ValueError("--batch-size must be a positive integer.")

    gps_directory = configured_gps_directory()
    files = discover_gps_files(gps_directory)
    LOGGER.info("Discovered %s GPS CSV file(s) in %s", len(files), gps_directory)

    ingested_file_count = 0
    for file_path in files:
        if ingest_file(file_path, gps_directory, arguments.batch_size):
            ingested_file_count += 1

    LOGGER.info("GPS ingestion complete: %s new file(s) loaded", ingested_file_count)


if __name__ == "__main__":
    main()
