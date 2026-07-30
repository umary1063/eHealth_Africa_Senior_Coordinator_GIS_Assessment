"""PostGIS nearest-settlement attribution for approved Q1 scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from psycopg import Connection


@dataclass(frozen=True)
class AttributionScenario:
    name: str
    base_tolerance_m: float
    urban_accuracy_aware: bool = False


SCENARIOS = (
    AttributionScenario("baseline_30m", 30.0),
    AttributionScenario("sensitivity_60m", 60.0),
    AttributionScenario("urban_accuracy_aware", 30.0, urban_accuracy_aware=True),
)


def schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "database" / "settlement_attribution.sql"


def create_attribution_schema(connection: Connection) -> None:
    """Create scenario output tables and supporting indexes."""
    with connection.cursor() as cursor:
        cursor.execute(schema_path().read_text(encoding="utf-8"))


def run_settlement_attribution(connection: Connection, scenario: AttributionScenario) -> None:
    """Write one deterministic nearest-settlement attribution per GPS point and scenario."""
    delete_sql = "DELETE FROM processed.gps_settlement_attributions WHERE scenario_name = %(scenario)s"
    insert_sql = """
    WITH qa AS (
        SELECT gps_track_point_id,
            BOOL_OR(quality_rule = 'impossible_speed') AS impossible_speed_flag,
            BOOL_OR(quality_rule = 'accuracy_quality') AS accuracy_quality_flag,
            BOOL_OR(quality_rule = 'reported_speed_disagreement') AS reported_speed_disagreement_flag,
            BOOL_OR(quality_rule = 'stationary_cluster') AS stationary_cluster_flag,
            BOOL_OR(quality_rule = 'gps_gap') AS gps_gap_flag,
            BOOL_OR(quality_rule = 'outside_campaign_hours') AS outside_campaign_hours_flag
        FROM processed.gps_quality_flags
        GROUP BY gps_track_point_id
    ), scoped_points AS (
        SELECT g.*, COALESCE(qa.impossible_speed_flag, FALSE) AS impossible_speed_flag,
            COALESCE(qa.accuracy_quality_flag, FALSE) AS accuracy_quality_flag,
            COALESCE(qa.reported_speed_disagreement_flag, FALSE) AS reported_speed_disagreement_flag,
            COALESCE(qa.stationary_cluster_flag, FALSE) AS stationary_cluster_flag,
            COALESCE(qa.gps_gap_flag, FALSE) AS gps_gap_flag,
            COALESCE(qa.outside_campaign_hours_flag, FALSE) AS outside_campaign_hours_flag
        FROM raw.gps_points_raw g
        LEFT JOIN qa ON qa.gps_track_point_id = g.gps_track_point_id
        WHERE g.geom IS NOT NULL AND g.observed_at IS NOT NULL
          AND g.observed_at::date BETWEEN DATE '2026-03-09' AND DATE '2026-03-13'
          AND g.observed_at::time BETWEEN TIME '07:00' AND TIME '19:00'
    )
    INSERT INTO processed.gps_settlement_attributions (
        scenario_name, gps_track_point_id, settlement_id, observed_at, team_id, campaign_date,
        distance_to_settlement_m, applicable_tolerance_m, candidate_count, attribution_method,
        confidence_class, baseline_eligible, impossible_speed_flag, accuracy_quality_flag,
        reported_speed_disagreement_flag, stationary_cluster_flag, gps_gap_flag, outside_campaign_hours_flag
    )
    SELECT %(scenario)s, p.gps_track_point_id, nearest.settlement_id, p.observed_at, p.team_id, p.observed_at::date,
        nearest.distance_m, nearest.applicable_tolerance_m, candidates.candidate_count,
        'nearest_eligible_settlement_postgis',
        CASE WHEN candidates.candidate_count > 1 THEN 'ambiguous'
             WHEN p.accuracy_quality_flag OR p.reported_speed_disagreement_flag OR p.stationary_cluster_flag THEN 'review'
             ELSE 'high' END,
        NOT p.outside_campaign_hours_flag AND NOT p.impossible_speed_flag,
        p.impossible_speed_flag, p.accuracy_quality_flag, p.reported_speed_disagreement_flag,
        p.stationary_cluster_flag, p.gps_gap_flag, p.outside_campaign_hours_flag
    FROM scoped_points p
    CROSS JOIN LATERAL (
        SELECT s.settlement_id,
            ST_Distance(ST_Transform(p.geom, 32632), ST_Transform(s.geom, 32632)) AS distance_m,
            CASE WHEN %(urban_aware)s AND s.settlement_type = 'Urban block'
                 THEN LEAST(60.0, GREATEST(30.0, COALESCE(p.accuracy_m, 30.0)::double precision))
                 ELSE %(tolerance)s::double precision END AS applicable_tolerance_m
        FROM raw.settlements s
        WHERE ST_DWithin(ST_Transform(p.geom, 32632), ST_Transform(s.geom, 32632),
            CASE WHEN %(urban_aware)s AND s.settlement_type = 'Urban block'
                 THEN LEAST(60.0, GREATEST(30.0, COALESCE(p.accuracy_m, 30.0)::double precision))
                 ELSE %(tolerance)s::double precision END)
        ORDER BY ST_Transform(s.geom, 32632) <-> ST_Transform(p.geom, 32632), s.settlement_id
        LIMIT 1
    ) nearest
    CROSS JOIN LATERAL (
        SELECT COUNT(*)::integer AS candidate_count
        FROM raw.settlements s
        WHERE ST_DWithin(ST_Transform(p.geom, 32632), ST_Transform(s.geom, 32632),
            CASE WHEN %(urban_aware)s AND s.settlement_type = 'Urban block'
                 THEN LEAST(60.0, GREATEST(30.0, COALESCE(p.accuracy_m, 30.0)::double precision))
                 ELSE %(tolerance)s::double precision END)
    ) candidates;
    """
    parameters = {"scenario": scenario.name, "tolerance": scenario.base_tolerance_m, "urban_aware": scenario.urban_accuracy_aware}
    with connection.cursor() as cursor:
        cursor.execute(delete_sql, parameters)
        cursor.execute(insert_sql, parameters)
