"""Explicit spatial-weights construction and diagnostics."""
from __future__ import annotations

import numpy as np
import pandas as pd
from libpysal.weights import DistanceBand, KNN
from scipy.sparse.csgraph import connected_components


def _diagnostics(weights, coordinates: np.ndarray, specification: str, kth_distances=None) -> dict:
    neighbour_counts = np.asarray([len(weights.neighbors[i]) for i in weights.id_order], dtype=int)
    # Connectivity is assessed on the undirected neighbour graph: either member
    # of a KNN pair establishes a graph edge for component diagnostics.
    adjacency = weights.sparse.maximum(weights.sparse.T)
    components, _ = connected_components(adjacency, directed=False)
    result = {
        "weights_specification": specification,
        "observations": weights.n,
        "minimum_neighbours": int(neighbour_counts.min()),
        "median_neighbours": float(np.median(neighbour_counts)),
        "maximum_neighbours": int(neighbour_counts.max()),
        "islands": int(len(weights.islands)),
        "connected_components": int(components),
    }
    if kth_distances is not None:
        result["median_kth_neighbour_distance_m"] = float(np.median(kth_distances))
        result["maximum_kth_neighbour_distance_m"] = float(np.max(kth_distances))
    return result


def knn_weights(coordinates: np.ndarray, k: int = 8):
    """Create binary KNN weights, then row-standardize them for analysis."""
    weights = KNN.from_array(coordinates, k=k)
    kth_distances = np.sort(
        np.sqrt(((coordinates[:, None, :] - coordinates[None, :, :]) ** 2).sum(axis=2)), axis=1
    )[:, k]
    diagnostics = _diagnostics(weights, coordinates, f"knn_k{k}_binary_row_standardized", kth_distances)
    weights.transform = "R"
    return weights, diagnostics


def distance_band_weights(coordinates: np.ndarray, threshold_m: float = 9050.0):
    """Create binary distance-band weights, then row-standardize them."""
    weights = DistanceBand.from_array(coordinates, threshold=threshold_m, binary=True, silence_warnings=True)
    diagnostics = _diagnostics(weights, coordinates, f"distance_band_{threshold_m:g}m_binary_row_standardized")
    weights.transform = "R"
    return weights, diagnostics


def knn_candidate_diagnostics(coordinates: np.ndarray, candidates=(4, 6, 8, 10)) -> pd.DataFrame:
    """Return documented diagnostics for each candidate KNN graph."""
    rows = []
    for k in candidates:
        _, row = knn_weights(coordinates, k=k)
        row["analysis_scenario"] = "primary_excluding_ambiguous"
        rows.append(row)
    return pd.DataFrame(rows)
