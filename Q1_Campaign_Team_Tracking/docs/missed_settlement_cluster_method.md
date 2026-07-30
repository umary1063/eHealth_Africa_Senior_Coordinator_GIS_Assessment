# Missed-Settlement Cluster Method

## Purpose and population

This Requirement 5 analysis identifies spatial concentration in the observed, GPS-derived missed-settlement indicator. The primary population contains 2,382 planned settlements classified under `baseline_30m`: 2,168 unvisited (`missed_indicator = 1`) and 214 visited (`0`). The 180 ambiguous settlements are excluded rather than treated as missed.

## Weights and inference

Coordinates are transformed from source EPSG:4326 to EPSG:32632 before all distance operations. Primary weights are binary k-nearest-neighbour (`k=8`) weights, row-standardized before statistic calculation. They have no islands and one connected component. KNN candidate diagnostics for k=4, 6, 8, and 10 are retained in `weights_diagnostics.csv`; the executed k=4 graph has two components, while k=6, k=8, and k=10 have one. This reinforces the selected k=8 primary matrix.

Two sensitivity analyses are retained separately: binary row-standardized 9,050 m distance-band weights for the primary population, and binary row-standardized k=8 weights for all 2,562 settlements with ambiguous cases treated as missed. The distance threshold removes islands but produces dense neighbourhoods; it is therefore a sensitivity matrix rather than the primary local interpretation.

Global Moran's I is a global autocorrelation diagnostic. Local Moran's I supplies local statistics, quadrants, spatial lag, raw two-sided permutation p-values, and Benjamini-Hochberg FDR-adjusted p-values. Each analysis uses 999 permutations, seed `20260730`, and alpha 0.05. The primary labels use FDR-adjusted significance: High-High missed cluster, Low-Low visited cluster, High-Low outlier, Low-High outlier, or Not significant.

## Results and limits

The primary Global Moran's I was 0.046612 (expected -0.000420; z=4.821064; permutation p=0.001), indicating positive global autocorrelation in the observed indicator. However, no primary local results remained significant after FDR correction. Raw local results remain available for operational screening but must not be presented as confirmed local discoveries.

The distance-band sensitivity produced I=0.040196 (expected -0.000420; z=8.401129; p=0.001); the ambiguity-included k=8 sensitivity produced I=0.043926 (expected -0.000390; z=5.004061; p=0.001). Both sensitivity analyses also have no FDR-significant local results. The distance-band raw screening counts are 118 Low-Low, 38 Low-High, and 8 High-Low; the ambiguity sensitivity has 52 Low-Low and 29 Low-High. These counts are not confirmed hotspots.

Spatial results identify concentration only. They do not establish causation, prove that an individual settlement was truly missed, establish team misconduct, or establish whether individual children were vaccinated. Results depend on GPS QA, settlement attribution, the missed definition, weights, permutation inference, and FDR correction. The high prevalence of the missed indicator also creates an imbalanced binary outcome that limits contrast between local categories.
