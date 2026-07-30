"""PostgreSQL/PostGIS connection helpers for Q1 ingestion components."""

from __future__ import annotations

import os
from dataclasses import dataclass

import psycopg
from psycopg import Connection


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
