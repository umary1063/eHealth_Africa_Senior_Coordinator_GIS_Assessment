# Q1 Reusable Python Modules

## Purpose

The `src` package contains reusable Q1 implementation code. Keeping database, ingestion, and quality-assessment logic outside notebooks supports consistent execution, review, and testing.

## Package Organization

| Package or module | Role |
|---|---|
| `src.project_paths` | Central project-relative paths for notebooks and modules. |
| `src.ingestion` | PostgreSQL connection handling, ingestion registry, and raw GPS ingestion. |
| `src.quality` | Non-destructive GPS quality-rule evaluation and flag persistence. |

## Notebook Use

Notebooks add the Q1 project root to `sys.path` only when needed, then import reusable code with package imports such as `from src.ingestion.db_connection import get_connection`. This avoids hardcoded machine paths and duplicate implementation logic.
