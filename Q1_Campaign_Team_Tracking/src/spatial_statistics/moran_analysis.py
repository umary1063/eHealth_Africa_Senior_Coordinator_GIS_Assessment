"""Global and local Moran's I with reproducible permutation inference."""
from __future__ import annotations

import numpy as np
import pandas as pd
from src.ingestion.reference_db_connection import get_reference_connection, reference_cursor
from src.project_paths import output_table_path
from src.spatial_statistics.spatial_weights import distance_band_weights, knn_candidate_diagnostics, knn_weights

PERMUTATIONS = 999
SEED = 20260730
ALPHA = 0.05


def benjamini_hochberg(p_values: np.ndarray, alpha: float = ALPHA) -> tuple[np.ndarray, np.ndarray]:
    """Return BH-FDR rejection flags and adjusted p-values without an extra dependency."""
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ranked = p_values[order]
    count = len(ranked)
    adjusted_ranked = np.minimum.accumulate((ranked * count / np.arange(1, count + 1))[::-1])[::-1]
    adjusted_ranked = np.clip(adjusted_ranked, 0.0, 1.0)
    adjusted = np.empty(count, dtype=float)
    adjusted[order] = adjusted_ranked
    return adjusted <= alpha, adjusted


def _label(quadrant: int, significant: bool) -> str:
    if not significant:
        return "Not significant"
    return {1: "High-High missed cluster", 2: "Low-High outlier", 3: "Low-Low visited cluster", 4: "High-Low outlier"}.get(int(quadrant), "Not significant")


def _two_sided_permutation_p(observed: np.ndarray, simulated: np.ndarray) -> np.ndarray:
    """Monte Carlo two-sided p-values with the +1 correction."""
    return (1 + (np.abs(simulated) >= np.abs(observed)).sum(axis=0)) / (simulated.shape[0] + 1)


def _global_i(values: np.ndarray, sparse_weights) -> float:
    centered = values - values.mean()
    return float((len(values) / sparse_weights.sum()) * (centered @ (sparse_weights @ centered)) / (centered @ centered))


def _permutation_moran(values: np.ndarray, weights) -> tuple[float, float, float, float, np.ndarray, np.ndarray]:
    """Pure NumPy/SciPy permutation inference, avoiding an unstable Windows compiled path."""
    sparse = weights.sparse
    centered = values - values.mean()
    scale = np.sqrt((centered @ centered) / (len(values) - 1))
    z = centered / scale
    observed_global = _global_i(values, sparse)
    observed_local = z * (sparse @ z)
    rng = np.random.default_rng(SEED)
    global_sim = np.empty(PERMUTATIONS, dtype=float)
    local_sim = np.empty((PERMUTATIONS, len(values)), dtype=float)
    for index in range(PERMUTATIONS):
        permuted = rng.permutation(values)
        global_sim[index] = _global_i(permuted, sparse)
        permuted_centered = permuted - permuted.mean()
        permuted_z = permuted_centered / np.sqrt((permuted_centered @ permuted_centered) / (len(values) - 1))
        local_sim[index] = permuted_z * (sparse @ permuted_z)
    global_p = float(_two_sided_permutation_p(np.array([observed_global]), global_sim[:, None])[0])
    global_z = float((observed_global - global_sim.mean()) / global_sim.std(ddof=1))
    return observed_global, -1 / (len(values) - 1), global_z, global_p, observed_local, _two_sided_permutation_p(observed_local, local_sim)


def run_moran_analysis(frame: pd.DataFrame, weights, scenario: str, weights_specification: str):
    """Run Global and Local Moran tests; retain raw and BH-FDR-adjusted inference."""
    if frame["settlement_id"].duplicated().any():
        raise ValueError(f"Duplicate settlement identifiers in {scenario}.")
    if len(frame) == 0:
        raise ValueError(f"No settlements supplied for {scenario}.")
    values = frame["missed_indicator"].astype(float).to_numpy()
    global_i, expected_i, global_z, global_p, local_i, raw_p = _permutation_moran(values, weights)
    fdr_significant, fdr_adjusted_p = benjamini_hochberg(raw_p)
    centered = values - values.mean()
    spatial_lag = weights.sparse @ values
    lag_centered = spatial_lag - values.mean()
    quadrant = np.select(
        [(centered > 0) & (lag_centered > 0), (centered < 0) & (lag_centered > 0),
         (centered < 0) & (lag_centered < 0), (centered > 0) & (lag_centered < 0)],
        [1, 2, 3, 4], default=0,
    )
    local = frame[["settlement_id", "gps_visit_status", "missed_indicator", "x_32632", "y_32632"]].copy()
    local["analysis_scenario"] = scenario
    local["weights_specification"] = weights_specification
    local["neighbour_count"] = [len(weights.neighbors[i]) for i in weights.id_order]
    local["local_moran_i"] = local_i
    local["quadrant"] = quadrant
    local["raw_permutation_p_value"] = raw_p
    local["fdr_adjusted_p_value"] = fdr_adjusted_p
    local["raw_significant"] = raw_p <= ALPHA
    local["fdr_adjusted_significant"] = fdr_significant
    local["spatial_lag"] = spatial_lag
    local["local_cluster_raw"] = [_label(q, s) for q, s in zip(quadrant, local["raw_significant"])]
    local["local_cluster_fdr"] = [_label(q, s) for q, s in zip(quadrant, local["fdr_adjusted_significant"])]
    global_row = {
        "analysis_scenario": scenario, "weights_specification": weights_specification,
        "observations": len(frame), "missed_settlements": int(values.sum()),
        "visited_settlements": int((values == 0).sum()), "permutations": PERMUTATIONS,
        "seed": SEED, "global_moran_i": global_i, "expected_i": expected_i,
        "z_score": global_z, "permutation_p_value": global_p,
    }
    return pd.DataFrame([global_row]), local


def cluster_summary(local: pd.DataFrame) -> pd.DataFrame:
    """Summarise local labels for both raw and FDR-adjusted inference."""
    rows = []
    for field, inference in [("local_cluster_raw", "raw_permutation"), ("local_cluster_fdr", "fdr_adjusted")]:
        for (scenario, specification, label), group in local.groupby(["analysis_scenario", "weights_specification", field], dropna=False):
            rows.append({"analysis_scenario": scenario, "weights_specification": specification, "inference": inference, "cluster_class": label, "settlement_count": len(group)})
    return pd.DataFrame(rows)


POPULATION_SQL = """
SELECT r.settlement_id, r.gps_visit_status,
       ST_X(ST_Transform(s.geom, 32632)) AS x_32632,
       ST_Y(ST_Transform(s.geom, 32632)) AS y_32632,
       ST_IsValid(s.geom) AS geometry_valid
FROM processed.settlement_coverage_reconciliation r
JOIN raw.settlements s ON s.settlement_id = r.settlement_id
ORDER BY r.settlement_id
"""


def load_population(connection) -> pd.DataFrame:
    """Load only database-resident planned settlements and projected coordinates."""
    with reference_cursor(connection) as cursor:
        cursor.execute(POPULATION_SQL)
        rows = cursor.fetchall()
        columns = [item[0] for item in cursor.description]
    frame = pd.DataFrame(rows, columns=columns)
    if len(frame) != 2562 or frame["settlement_id"].duplicated().any():
        raise ValueError("The reconciliation population must contain 2,562 unique planned settlements.")
    if frame[["x_32632", "y_32632"]].isna().any().any() or not frame["geometry_valid"].all():
        raise ValueError("All analysis settlements require valid EPSG:32632 coordinates.")
    return frame


def _scenario(frame: pd.DataFrame, name: str, include_ambiguous: bool) -> pd.DataFrame:
    result = frame.copy() if include_ambiguous else frame.loc[frame["gps_visit_status"] != "ambiguous"].copy()
    result["missed_indicator"] = (result["gps_visit_status"] != "visited").astype(int)
    expected = 2562 if include_ambiguous else 2318
    if len(result) != expected:
        raise ValueError(f"{name} expected {expected} settlements; found {len(result)}.")
    return result.reset_index(drop=True)


def execute_requirement_five(connection=None) -> dict[str, pd.DataFrame]:
    """Execute approved primary and sensitivity analyses and write four CSV outputs."""
    owns_connection = connection is None
    if owns_connection:
        # pg8000 avoids the known local Windows native psycopg/libpq access violation.
        # The analysis still reads the same PostGIS-resident reconciliation tables.
        connection = get_reference_connection()
    try:
        all_settlements = load_population(connection)
        primary = _scenario(all_settlements, "primary_knn8_excluding_ambiguous", False)
        ambiguity = _scenario(all_settlements, "sensitivity_knn8_ambiguous_as_missed", True)
        primary_coords = primary[["x_32632", "y_32632"]].to_numpy(dtype=float)
        ambiguity_coords = ambiguity[["x_32632", "y_32632"]].to_numpy(dtype=float)
        diagnostics = knn_candidate_diagnostics(primary_coords)
        primary_weights, primary_diag = knn_weights(primary_coords, 8)
        band_weights, band_diag = distance_band_weights(primary_coords, 9050.0)
        ambiguity_weights, ambiguity_diag = knn_weights(ambiguity_coords, 8)
        diagnostics = pd.concat([diagnostics, pd.DataFrame([
            {**band_diag, "analysis_scenario": "sensitivity_distance_band_excluding_ambiguous"},
            {**ambiguity_diag, "analysis_scenario": "sensitivity_knn8_ambiguous_as_missed"},
        ])], ignore_index=True)
        analyses = [
            (primary, primary_weights, "primary_knn8_excluding_ambiguous", primary_diag["weights_specification"]),
            (primary, band_weights, "sensitivity_distance_band_excluding_ambiguous", band_diag["weights_specification"]),
            (ambiguity, ambiguity_weights, "sensitivity_knn8_ambiguous_as_missed", ambiguity_diag["weights_specification"]),
        ]
        global_rows, local_rows = [], []
        for data, weights, name, specification in analyses:
            global_result, local_result = run_moran_analysis(data, weights, name, specification)
            global_rows.append(global_result)
            local_rows.append(local_result)
        global_summary = pd.concat(global_rows, ignore_index=True)
        local_results = pd.concat(local_rows, ignore_index=True)
        summary = cluster_summary(local_results)
        for filename, data in {
            "global_moran_summary.csv": global_summary,
            "local_moran_results.csv": local_results,
            "cluster_summary.csv": summary,
            "weights_diagnostics.csv": diagnostics,
        }.items():
            path = output_table_path(filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(path, index=False)
        return {"global": global_summary, "local": local_results, "cluster": summary, "diagnostics": diagnostics}
    finally:
        if owns_connection:
            connection.close()


if __name__ == "__main__":
    results = execute_requirement_five()
    print(results["global"].to_string(index=False))
