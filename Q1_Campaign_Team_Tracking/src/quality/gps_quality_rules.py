"""Documented, non-destructive GPS quality assessment rules for Q1."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, time
from math import asin, cos, radians, sin, sqrt
from typing import Iterable

import pandas as pd
from psycopg import Connection

SOURCE_FILE_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True)
class GPSQualityConfig:
    """Provisional thresholds to be reviewed in the Q1 decision log."""

    maximum_plausible_speed_kmh: float = 80.0
    reported_speed_disagreement_kmh: float = 20.0
    maximum_acceptable_accuracy_m: float = 30.0
    campaign_start: date = date(2026, 3, 9)
    campaign_end: date = date(2026, 3, 13)
    duty_start: time = time(7, 0)
    duty_end: time = time(19, 0)
    sequence_gap_minutes: int = 15
    stationary_radius_m: float = 25.0
    stationary_duration_minutes: int = 30


CONFIG = GPSQualityConfig()
REQUIRED_COLUMNS = {
    "gps_track_point_id",
    "source_file",
    "team_id",
    "logger_id",
    "observed_at",
    "longitude",
    "latitude",
    "accuracy_m",
    "speed_kmh",
}


def _haversine_m(
    longitude_1: float, latitude_1: float, longitude_2: float, latitude_2: float
) -> float:
    """Calculate great-circle distance in metres for two EPSG:4326 coordinates."""
    longitude_delta = radians(longitude_2 - longitude_1)
    latitude_delta = radians(latitude_2 - latitude_1)
    a_value = (
        sin(latitude_delta / 2) ** 2
        + cos(radians(latitude_1))
        * cos(radians(latitude_2))
        * sin(longitude_delta / 2) ** 2
    )
    return 6_371_000 * 2 * asin(sqrt(a_value))


def _validate_input(points: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS - set(points.columns)
    if missing_columns:
        raise ValueError(f"GPS QA input is missing: {', '.join(sorted(missing_columns))}")


def _mark_stationary_clusters(points: pd.DataFrame, config: GPSQualityConfig) -> pd.Series:
    """Flag contiguous, low-displacement sequences; source points remain unchanged.

    Chains only points that pass the source_file_date_mismatch check, for the same
    reason evaluate_gps_quality restricts its previous-point/gap/speed computations
    to clean points -- see technical_decisions.md, 2026-07-31.
    """
    flagged = pd.Series(False, index=points.index, dtype=bool)
    clean_points = points.loc[~points["source_file_date_mismatch_flag"]]
    group_columns = ["team_id", "logger_id"]
    for _, group in clean_points.groupby(group_columns, dropna=False, sort=False):
        cluster_indices: list[int] = []
        anchor = None

        def finalize_cluster() -> None:
            if len(cluster_indices) < 2:
                return
            start_time = points.loc[cluster_indices[0], "observed_at"]
            end_time = points.loc[cluster_indices[-1], "observed_at"]
            if pd.notna(start_time) and pd.notna(end_time):
                duration_minutes = (end_time - start_time).total_seconds() / 60
                if duration_minutes >= config.stationary_duration_minutes:
                    flagged.loc[cluster_indices] = True

        for index, row in group.iterrows():
            valid_point = pd.notna(row["longitude"]) and pd.notna(row["latitude"]) and pd.notna(row["observed_at"])
            if not valid_point:
                finalize_cluster()
                cluster_indices, anchor = [], None
                continue
            if anchor is None:
                cluster_indices, anchor = [index], row
                continue

            displacement_m = _haversine_m(
                anchor["longitude"], anchor["latitude"], row["longitude"], row["latitude"]
            )
            elapsed_minutes = (row["observed_at"] - points.loc[cluster_indices[-1], "observed_at"]).total_seconds() / 60
            if displacement_m <= config.stationary_radius_m and elapsed_minutes <= config.sequence_gap_minutes:
                cluster_indices.append(index)
            else:
                finalize_cluster()
                cluster_indices, anchor = [index], row
        finalize_cluster()
    return flagged


def evaluate_gps_quality(
    gps_points: pd.DataFrame, config: GPSQualityConfig = CONFIG
) -> pd.DataFrame:
    """Return QA-enriched points with flags; never filter or modify the input source table."""
    _validate_input(gps_points)
    points = gps_points.copy()
    points["observed_at"] = pd.to_datetime(points["observed_at"], errors="coerce")
    for column in ["longitude", "latitude", "accuracy_m", "speed_kmh"]:
        points[column] = pd.to_numeric(points[column], errors="coerce")

    points = points.sort_values(["team_id", "logger_id", "observed_at", "gps_track_point_id"], kind="stable")

    # source_file_date_mismatch is computed first and used to exclude contaminated
    # rows from every sequence-dependent computation below (previous point, gap,
    # calculated distance/speed, stationary clusters). Source files were found to
    # contain many days of logging beyond their nominal day (technical_decisions.md,
    # 2026-07-31); without this exclusion, a legitimate point's "previous point" in
    # a naive team/logger sort can be an unrelated position from a different real
    # track that happens to share a nearby timestamp, producing a genuine (not a
    # units-bug) implausible calculated speed between two physically unconnected
    # fixes. Points are still reported and flagged individually below; only the
    # *sequence* they are chained into for gap/speed/cluster purposes is restricted
    # to same-file-day points.
    observed_date = points["observed_at"].dt.date
    source_file_date = points["source_file"].str.extract(SOURCE_FILE_DATE_PATTERN, expand=False)
    source_file_date = pd.to_datetime(source_file_date, format="%Y-%m-%d", errors="coerce").dt.date
    points["source_file_date_mismatch_flag"] = (
        source_file_date.isna() | (observed_date != source_file_date)
    ).fillna(True)

    sequence_columns = ["previous_longitude", "previous_latitude", "previous_observed_at", "sequence_gap_minutes"]
    for column in sequence_columns:
        points[column] = pd.NaT if column == "previous_observed_at" else float("nan")

    clean = points.loc[~points["source_file_date_mismatch_flag"]]
    clean_grouped = clean.groupby(["team_id", "logger_id"], dropna=False, sort=False)
    points.loc[clean.index, "previous_longitude"] = clean_grouped["longitude"].shift()
    points.loc[clean.index, "previous_latitude"] = clean_grouped["latitude"].shift()
    points.loc[clean.index, "previous_observed_at"] = clean_grouped["observed_at"].shift()
    points.loc[clean.index, "sequence_gap_minutes"] = (
        (points.loc[clean.index, "observed_at"] - points.loc[clean.index, "previous_observed_at"]).dt.total_seconds() / 60
    )

    valid_pair = points[["longitude", "latitude", "previous_longitude", "previous_latitude"]].notna().all(axis=1)
    # Use NumPy-compatible NaN for derived numeric measures.  ``pd.NA`` cannot
    # be safely converted with ``astype(float)`` in the comparisons below.
    points["calculated_distance_m"] = float("nan")
    points.loc[valid_pair, "calculated_distance_m"] = points.loc[valid_pair].apply(
        lambda row: _haversine_m(row["previous_longitude"], row["previous_latitude"], row["longitude"], row["latitude"]),
        axis=1,
    )
    valid_interval = points["sequence_gap_minutes"] > 0
    points["calculated_speed_kmh"] = float("nan")
    points.loc[valid_pair & valid_interval, "calculated_speed_kmh"] = (
        (points.loc[valid_pair & valid_interval, "calculated_distance_m"].astype(float) / 1000.0)
        / (points.loc[valid_pair & valid_interval, "sequence_gap_minutes"] / 60)
    )

    points["impossible_speed_flag"] = (
        (points["calculated_speed_kmh"] > config.maximum_plausible_speed_kmh)
        | (points["speed_kmh"] > config.maximum_plausible_speed_kmh)
    ).fillna(False)
    points["reported_speed_disagreement_flag"] = (
        (points["calculated_speed_kmh"] - points["speed_kmh"]).abs()
        > config.reported_speed_disagreement_kmh
    ).fillna(False)
    points["accuracy_quality_flag"] = (
        points["accuracy_m"].isna() | (points["accuracy_m"] > config.maximum_acceptable_accuracy_m)
    )
    observation_date = points["observed_at"].dt.date
    observation_time = points["observed_at"].dt.time
    points["outside_campaign_hours_flag"] = (
        points["observed_at"].isna()
        | (observation_date < config.campaign_start)
        | (observation_date > config.campaign_end)
        | (observation_time < config.duty_start)
        | (observation_time > config.duty_end)
    ).fillna(True)
    points["gps_gap_flag"] = (points["sequence_gap_minutes"] > config.sequence_gap_minutes).fillna(False)
    points["stationary_cluster_flag"] = _mark_stationary_clusters(points, config)
    return points


def build_flag_records(points: pd.DataFrame, config: GPSQualityConfig = CONFIG) -> pd.DataFrame:
    """Convert flagged QA columns to an auditable long-form table."""
    rule_explanations = {
        "impossible_speed": f"Reported or calculated speed exceeds {config.maximum_plausible_speed_kmh:g} km/h.",
        "reported_speed_disagreement": f"Reported and calculated speed differ by more than {config.reported_speed_disagreement_kmh:g} km/h.",
        "accuracy_quality": f"Accuracy is missing or exceeds {config.maximum_acceptable_accuracy_m:g} m.",
        "outside_campaign_hours": "Timestamp is outside the configured campaign dates or duty-hours window.",
        "gps_gap": f"Time since the preceding point exceeds {config.sequence_gap_minutes} minutes.",
        "stationary_cluster": f"Point belongs to a low-displacement sequence of at least {config.stationary_duration_minutes} minutes.",
        "source_file_date_mismatch": "Timestamp's calendar date does not match the date encoded in the source "
                                      "file's own name (one file per team per day, per the supplied data pack) "
                                      "-- source files were found to contain many days of continuous logging "
                                      "beyond their nominal day, so a point is only trusted for analysis on the "
                                      "day its own file claims to be.",
    }
    flag_columns = {
        "impossible_speed": "impossible_speed_flag",
        "reported_speed_disagreement": "reported_speed_disagreement_flag",
        "accuracy_quality": "accuracy_quality_flag",
        "outside_campaign_hours": "outside_campaign_hours_flag",
        "gps_gap": "gps_gap_flag",
        "stationary_cluster": "stationary_cluster_flag",
        "source_file_date_mismatch": "source_file_date_mismatch_flag",
    }
    records = []
    for rule, column in flag_columns.items():
        for _, row in points.loc[points[column]].iterrows():
            records.append(
                {
                    "gps_track_point_id": int(row["gps_track_point_id"]),
                    "source_file": row["source_file"],
                    "team_id": row["team_id"],
                    "observed_at": row["observed_at"],
                    "quality_rule": rule,
                    "flag_value": True,
                    "explanation": rule_explanations[rule],
                }
            )
    return pd.DataFrame(records, columns=["gps_track_point_id", "source_file", "team_id", "observed_at", "quality_rule", "flag_value", "explanation"])


def upsert_quality_flags(connection: Connection, flag_records: pd.DataFrame) -> None:
    """Replace all quality flags with the freshly computed set; raw GPS observations are never touched.

    This clears the table before writing rather than only inserting/updating rows
    present in `flag_records`. The previous upsert-only version left stale True
    rows behind for any point that stopped being flagged after a rule change --
    e.g. after fixing the calculated-speed unit-conversion bug, points that were
    no longer impossible_speed-flagged kept their old flagged=True row forever,
    because nothing ever deleted it. That silently polluted every downstream
    query that checks for the *existence* of a flagged row (BOOL_OR-style), not
    just its latest value. See technical_decisions.md, 2026-07-31.
    """
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM processed.gps_quality_flags")
        if flag_records.empty:
            return
        values: Iterable[tuple] = flag_records.itertuples(index=False, name=None)
        cursor.executemany(
            """
            INSERT INTO processed.gps_quality_flags (
                gps_track_point_id, source_file, team_id, observed_at, quality_rule, flag_value, explanation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (gps_track_point_id, quality_rule) DO UPDATE SET
                source_file = EXCLUDED.source_file,
                team_id = EXCLUDED.team_id,
                observed_at = EXCLUDED.observed_at,
                flag_value = EXCLUDED.flag_value,
                explanation = EXCLUDED.explanation,
                created_at = CURRENT_TIMESTAMP
            """,
            values,
        )


def quality_summary(flag_records: pd.DataFrame, point_count: int) -> pd.DataFrame:
    """Return a rule-level count and percentage summary for reporting."""
    rules = [
        "impossible_speed",
        "reported_speed_disagreement",
        "accuracy_quality",
        "outside_campaign_hours",
        "gps_gap",
        "stationary_cluster",
        "source_file_date_mismatch",
    ]
    counts = flag_records.groupby("quality_rule", dropna=False).size().rename("flagged_records")
    summary = pd.DataFrame({"Rule": rules})
    summary["flagged_records"] = summary["Rule"].map(counts).fillna(0).astype(int)
    summary["percentage"] = (summary["flagged_records"] / point_count * 100) if point_count else 0.0
    return summary
