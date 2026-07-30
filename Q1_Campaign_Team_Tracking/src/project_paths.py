"""Project-relative paths shared by Q1 notebooks and reusable modules."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the Q1 project root independent of the current working directory."""
    return Path(__file__).resolve().parent.parent


def source_directory() -> Path:
    """Return the reusable source-code directory."""
    return project_root() / "src"


def local_environment_file() -> Path:
    """Return the Git-ignored local database-environment file path."""
    return source_directory() / ".env.txt"


def output_table_path(filename: str) -> Path:
    """Return a project-relative output-table path."""
    return project_root() / "outputs" / "tables" / filename
