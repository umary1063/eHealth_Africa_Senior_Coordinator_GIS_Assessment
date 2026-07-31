-- 2026-07-31: adds the source_file_date_mismatch_flag column so an existing
-- database (already ingested before this rule existed) matches the current
-- source-of-truth schema in settlement_attribution.sql without a full rebuild.
-- Idempotent: safe to run against a database that already has the column
-- (e.g. one bootstrapped fresh from database/init/ after this change).

ALTER TABLE processed.gps_settlement_attributions
    ADD COLUMN IF NOT EXISTS source_file_date_mismatch_flag BOOLEAN NOT NULL DEFAULT FALSE;
