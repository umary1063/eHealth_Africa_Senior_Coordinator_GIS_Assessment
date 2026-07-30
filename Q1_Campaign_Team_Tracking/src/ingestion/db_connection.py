"""PostgreSQL/PostGIS connection helpers for Q1 ingestion components."""

from __future__ import annotations

import os
from dataclasses import dataclass
import psycopg
from psycopg import Connection

from src.project_paths import local_environment_file


def load_local_environment() -> None:
    """Load optional local database variables from the Git-ignored Q1 env file."""
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


load_local_environment()


@dataclass(frozen=True)
class DatabaseSettings:
    """Connection settings sourced from the execution environment."""

    host: str
    port: int
    database: str
    user: str
    password: str


def get_database_settings() -> DatabaseSettings:
    """Read database settings without storing credentials in source code."""
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("POSTGRES_PASSWORD must be set before connecting to PostgreSQL.")

    return DatabaseSettings(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "eha_q1"),
        user=os.environ.get("POSTGRES_USER", "eha_q1_user"),
        password=password,
    )


def get_connection() -> Connection:
    """Create a transactional PostgreSQL connection using environment variables."""
    settings = get_database_settings()
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
    )
