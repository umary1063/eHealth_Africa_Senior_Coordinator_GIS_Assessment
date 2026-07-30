"""Pure-Python pg8000 database connection for reference-data ingestion only."""

from __future__ import annotations

import os
from dataclasses import dataclass
from contextlib import contextmanager

import pg8000.dbapi

from src.project_paths import local_environment_file


def load_local_environment() -> None:
    """Load the same Git-ignored local database variables used by Q1 modules."""
    environment_path = local_environment_file()
    if not environment_path.is_file():
        return
    for line in environment_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid environment entry in {environment_path.name}: {line.split()[0]!r}")
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class ReferenceDatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str


def get_reference_database_settings() -> ReferenceDatabaseSettings:
    load_local_environment()
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("POSTGRES_PASSWORD must be set before connecting to PostgreSQL.")
    return ReferenceDatabaseSettings(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "eha_q1"),
        user=os.environ.get("POSTGRES_USER", "eha_q1_user"),
        password=password,
    )


def get_reference_connection():
    """Open a pg8000 DB-API connection and verify it with a Python exception on failure."""
    settings = get_reference_database_settings()
    connection = pg8000.dbapi.connect(
        host=settings.host,
        port=settings.port,
        database=settings.database,
        user=settings.user,
        password=settings.password,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        if cursor.fetchone()[0] != 1:
            raise RuntimeError("pg8000 PostgreSQL preflight did not return SELECT 1.")
        cursor.close()
    except Exception:
        connection.close()
        raise
    return connection


@contextmanager
def reference_cursor(connection):
    """Provide context-managed cursors for pg8000's DB-API implementation."""
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
