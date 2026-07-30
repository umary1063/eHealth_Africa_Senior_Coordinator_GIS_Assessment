"""Reconstruct settlement visit episodes from confident attribution evidence."""

from __future__ import annotations

from psycopg import Connection


def classify_settlement_visits(connection: Connection, scenario_name: str) -> None:
    """Build 15-minute continuous episodes and one scenario summary per settlement."""
    delete_episodes_sql = "DELETE FROM processed.settlement_visit_episodes WHERE scenario_name = %(scenario)s"
    delete_summaries_sql = "DELETE FROM processed.settlement_visit_summaries WHERE scenario_name = %(scenario)s"
    episodes_sql = """
    WITH evidence AS (
        SELECT *, LAG(observed_at) OVER (
            PARTITION BY settlement_id, team_id, campaign_date ORDER BY observed_at, gps_track_point_id
        ) AS previous_observed_at
        FROM processed.gps_settlement_attributions
        WHERE scenario_name = %(scenario)s AND baseline_eligible AND confidence_class <> 'ambiguous'
    ), episode_points AS (
        SELECT *, SUM(CASE WHEN previous_observed_at IS NULL
                                OR observed_at - previous_observed_at > INTERVAL '15 minutes'
                           THEN 1 ELSE 0 END) OVER (
            PARTITION BY settlement_id, team_id, campaign_date ORDER BY observed_at, gps_track_point_id
        ) AS episode_number
        FROM evidence
    ), episodes AS (
        SELECT settlement_id, team_id, campaign_date, episode_number::integer,
            COUNT(*)::integer AS point_count, MIN(observed_at) AS first_observed_at,
            MAX(observed_at) AS last_observed_at,
            EXTRACT(EPOCH FROM MAX(observed_at) - MIN(observed_at)) / 60.0 AS dwell_duration_minutes,
            MAX(EXTRACT(EPOCH FROM observed_at - previous_observed_at) / 60.0) AS maximum_internal_gap_minutes
        FROM episode_points
        GROUP BY settlement_id, team_id, campaign_date, episode_number
    )
    INSERT INTO processed.settlement_visit_episodes (
        scenario_name, settlement_id, team_id, campaign_date, episode_number, point_count,
        first_observed_at, last_observed_at, dwell_duration_minutes, maximum_internal_gap_minutes, is_confirmed_visit
    )
    SELECT %(scenario)s, settlement_id, team_id, campaign_date, episode_number, point_count,
        first_observed_at, last_observed_at, dwell_duration_minutes, maximum_internal_gap_minutes,
        point_count >= 3 AND dwell_duration_minutes >= 15
            AND COALESCE(maximum_internal_gap_minutes, 0) <= 15
    FROM episodes
    """

    summaries_sql = """
    WITH attribution_rollup AS (
        SELECT settlement_id,
            COUNT(*) FILTER (WHERE baseline_eligible AND confidence_class <> 'ambiguous')::integer AS eligible_gps_point_count,
            COUNT(*) FILTER (WHERE confidence_class = 'ambiguous')::integer AS ambiguous_attribution_count,
            COUNT(DISTINCT team_id) FILTER (WHERE baseline_eligible AND confidence_class <> 'ambiguous')::integer AS team_count,
            MIN(observed_at) FILTER (WHERE baseline_eligible AND confidence_class <> 'ambiguous') AS first_observed_at,
            MAX(observed_at) FILTER (WHERE baseline_eligible AND confidence_class <> 'ambiguous') AS last_observed_at,
            MIN(distance_to_settlement_m) AS nearest_attribution_distance_m
        FROM processed.gps_settlement_attributions
        WHERE scenario_name = %(scenario)s
        GROUP BY settlement_id
    ), episode_rollup AS (
        SELECT settlement_id,
            BOOL_OR(is_confirmed_visit) AS has_confirmed_visit,
            COALESCE(SUM(dwell_duration_minutes) FILTER (WHERE is_confirmed_visit), 0) AS confirmed_dwell_duration_minutes
        FROM processed.settlement_visit_episodes
        WHERE scenario_name = %(scenario)s
        GROUP BY settlement_id
    )
    INSERT INTO processed.settlement_visit_summaries (
        scenario_name, settlement_id, visit_classification, team_count, first_observed_at, last_observed_at,
        dwell_duration_minutes, eligible_gps_point_count, nearest_attribution_distance_m, confidence_class,
        ambiguous_attribution_count
    )
    SELECT %(scenario)s, s.settlement_id,
        CASE WHEN COALESCE(e.has_confirmed_visit, FALSE) THEN 'visited'
             WHEN COALESCE(a.eligible_gps_point_count, 0) > 0 OR COALESCE(a.ambiguous_attribution_count, 0) > 0 THEN 'ambiguous'
             ELSE 'unvisited' END,
        COALESCE(a.team_count, 0), a.first_observed_at, a.last_observed_at,
        COALESCE(e.confirmed_dwell_duration_minutes, 0), COALESCE(a.eligible_gps_point_count, 0),
        a.nearest_attribution_distance_m,
        CASE WHEN COALESCE(e.has_confirmed_visit, FALSE) THEN 'high'
             WHEN COALESCE(a.eligible_gps_point_count, 0) > 0 OR COALESCE(a.ambiguous_attribution_count, 0) > 0 THEN 'ambiguous'
             ELSE 'review' END,
        COALESCE(a.ambiguous_attribution_count, 0)
    FROM raw.settlements s
    LEFT JOIN attribution_rollup a ON a.settlement_id = s.settlement_id
    LEFT JOIN episode_rollup e ON e.settlement_id = s.settlement_id
    """
    with connection.cursor() as cursor:
        parameters = {"scenario": scenario_name}
        cursor.execute(delete_episodes_sql, parameters)
        cursor.execute(delete_summaries_sql, parameters)
        cursor.execute(episodes_sql, parameters)
        cursor.execute(summaries_sql, parameters)
