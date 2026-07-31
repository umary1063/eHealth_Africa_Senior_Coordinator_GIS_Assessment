"""Idempotency test for GPS ingestion (Q1 requirement 1: "running it twice must
not duplicate records").

Runs against the same live PostGIS instance and the same data-pack files the
rest of this codebase uses -- no mocking, consistent with how the notebooks
and src/ modules already operate. Requires the Docker Postgres/PostGIS
container to be running and src/.env.txt configured; skips (not fails) if
either the database or the data pack is unavailable, so this does not block
a checkout that has not yet stood up the local environment.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ingestion import ingest_gps

try:
    from src.ingestion.db_connection import get_connection
except Exception:  # pragma: no cover - environment not configured
    get_connection = None

DATA_PACK_TRACKS = (
    Path(__file__).resolve().parents[2]
    / "Technical_asssessment"
    / "eHA_Assessment_Data_Pack_v4_CANDIDATE"
    / "Part1_Q1_Campaign_Tracking"
    / "tracks"
)


def _database_available() -> bool:
    if get_connection is None:
        return False
    try:
        with get_connection():
            return True
    except Exception:
        return False


def _row_count(source_file: str) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM raw.gps_points_raw WHERE source_file = %s",
                (source_file,),
            )
            return cursor.fetchone()[0]


@pytest.fixture(scope="module")
def sample_track_file() -> Path:
    if not DATA_PACK_TRACKS.is_dir():
        pytest.skip(f"Data pack tracks directory not found: {DATA_PACK_TRACKS}")
    files = sorted(DATA_PACK_TRACKS.glob("*.csv"))
    if not files:
        pytest.skip("No GPS track files found in the data pack.")
    return files[0]


@pytest.mark.skipif(not _database_available(), reason="PostGIS is not reachable; start it via docker-compose up.")
def test_ingest_file_is_idempotent(sample_track_file: Path) -> None:
    """Ingesting the same file twice must leave the raw row count unchanged."""
    source_file_name = sample_track_file.name

    ingest_gps.ingest_file(sample_track_file, DATA_PACK_TRACKS, batch_size=10_000)
    count_after_first = _row_count(source_file_name)
    assert count_after_first > 0, "No rows present for this source file after ingestion."

    second_run_loaded = ingest_gps.ingest_file(sample_track_file, DATA_PACK_TRACKS, batch_size=10_000)
    count_after_second = _row_count(source_file_name)

    assert second_run_loaded is False, (
        "Re-ingesting an already-loaded file must be reported as skipped "
        f"(ingest_file returned {second_run_loaded!r}, expected False)."
    )
    assert count_after_second == count_after_first, (
        "Row count changed after re-ingesting the same file: "
        f"{count_after_first} -> {count_after_second}. Ingestion is not idempotent."
    )


@pytest.mark.skipif(not _database_available(), reason="PostGIS is not reachable; start it via docker-compose up.")
def test_ingest_file_detects_a_changed_source_file(sample_track_file: Path, tmp_path: Path) -> None:
    """A file that changes content after being registered under the same name
    must be rejected, not silently re-loaded -- this is the other half of
    'idempotent': safe to re-run, not safe to silently accept a mutated input.
    """
    original_text = sample_track_file.read_text(encoding="utf-8")
    header, *rows = original_text.splitlines()
    if not rows:
        pytest.skip("Sample file has no data rows to mutate.")

    # Ensure the real file is registered first, under its real relative path.
    ingest_gps.ingest_file(sample_track_file, DATA_PACK_TRACKS, batch_size=10_000)

    # Build a mutated copy at the *same relative path* under a fake data root,
    # so ingest_file computes the same source_file identifier but a different checksum.
    fake_root = tmp_path / "tracks"
    fake_root.mkdir()
    mutated_path = fake_root / sample_track_file.name
    mutated_rows = [rows[0].replace(rows[0].split(",")[0], "T99", 1)] + rows[1:]
    mutated_path.write_text("\n".join([header, *mutated_rows]) + "\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="different successfully ingested checksum"):
        ingest_gps.ingest_file(mutated_path, fake_root, batch_size=10_000)
