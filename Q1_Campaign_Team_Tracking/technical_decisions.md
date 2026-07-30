# Technical Decisions

This log records material technical and methodological decisions made during Question 1 implementation.

| Date | Decision | Options Considered | Selected Approach | Justification |
|---|---|---|---|---|
| 2026-07-30 | Settlement identifier strategy | `settlement_id`; settlement name | Use `settlement_id` as the primary settlement reference key. | The completed audit recorded zero duplicate `settlement_id` values in the settlement masterlist. |
| 2026-07-30 | Data quality handling | Remove anomalous records; preserve and flag anomalous records | Preserve anomalous records and flag them rather than silently removing them. | The completed audit identified GPS missing values, e-Tally missing values, and potentially suspicious dose rows that require documented review. |
| _YYYY-MM-DD_ | Spatial database architecture | _To be completed_ | _To be completed_ | _To be completed after schema review._ |
| 2026-07-30 | Local development database environment | Local PostgreSQL/PostGIS installation; Dockerized PostgreSQL/PostGIS | Dockerized PostgreSQL/PostGIS | Ensures reproducible spatial database setup. |
| 2026-07-30 | GPS ingestion strategy | File-based loading without registry; checksum-based idempotent ingestion | Checksum-based idempotent ingestion into PostGIS raw layer | Maintains traceability and prevents duplicate loading. |
