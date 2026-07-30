"""File-level audit registry used to support idempotent ingestion."""

from __future__ import annotations

import hashlib
from pathlib import Path

from psycopg import Connection


def calculate_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA256 checksum of a source file without modifying it."""
    digest = hashlib.sha256()
    with file_path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_already_loaded(
    connection: Connection, source_file: str, checksum_sha256: str
) -> bool:
    """Check whether the same file version has a successful registry entry."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM audit.ingestion_file_registry
                WHERE source_file = %s
                  AND file_checksum_sha256 = %s
                  AND ingestion_status = 'succeeded'
            )
            """,
            (source_file, checksum_sha256),
        )
        return bool(cursor.fetchone()[0])


def source_file_has_other_loaded_version(
    connection: Connection, source_file: str, checksum_sha256: str
) -> bool:
    """Detect a changed source file rather than silently mixing file versions."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM audit.ingestion_file_registry
                WHERE source_file = %s
                  AND file_checksum_sha256 <> %s
                  AND ingestion_status = 'succeeded'
            )
            """,
            (source_file, checksum_sha256),
        )
        return bool(cursor.fetchone()[0])


def register_successful_ingestion(
    connection: Connection,
    *,
    source_file: str,
    checksum_sha256: str,
    file_size_bytes: int,
    source_record_count: int,
    loaded_record_count: int,
) -> None:
    """Register a successfully committed file load in the ingestion audit table."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO audit.ingestion_file_registry (
                source_file,
                source_type,
                file_checksum_sha256,
                file_size_bytes,
                source_record_count,
                loaded_record_count,
                ingestion_status,
                started_at,
                completed_at
            )
            VALUES (%s, 'gps_track_csv', %s, %s, %s, %s, 'succeeded', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (source_file, file_checksum_sha256) DO NOTHING
            """,
            (
                source_file,
                checksum_sha256,
                file_size_bytes,
                source_record_count,
                loaded_record_count,
            ),
        )
