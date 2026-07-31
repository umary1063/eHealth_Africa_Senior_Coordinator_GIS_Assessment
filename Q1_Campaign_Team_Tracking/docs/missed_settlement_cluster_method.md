# Missed-Settlement Cluster Method

## Purpose and population

This Requirement 5 analysis identifies spatial concentration in the observed, GPS-derived missed-settlement indicator. The primary population contains 2,318 planned settlements classified under `baseline_30m`: 2,179 unvisited (`missed_indicator = 1`) and 139 visited (`0`) (fully revised 2026-07-31 after four compounding GPS-pipeline defects were found and fixed -- see `technical_decisions.md`; originally 2,382 / 2,168 / 214). The 244 ambiguous settlements (originally 180) are excluded rather than treated as missed.

## Weights and inference

Coordinates are transformed from source EPSG:4326 to EPSG:32632 before all distance operations. Primary weights are binary k-nearest-neighbour (`k=8`) weights, row-standardized before statistic calculation. They have no islands and one connected component. KNN candidate diagnostics for k=4, 6, 8, and 10 are retained in `weights_diagnostics.csv`; the executed k=4 graph has two components, while k=6, k=8, and k=10 have one. This reinforces the selected k=8 primary matrix.

Two sensitivity analyses are retained separately: binary row-standardized 9,050 m distance-band weights for the primary population, and binary row-standardized k=8 weights for all 2,562 settlements with ambiguous cases treated as missed. The distance threshold removes islands but produces dense neighbourhoods; it is therefore a sensitivity matrix rather than the primary local interpretation.

Global Moran's I is a global autocorrelation diagnostic. Local Moran's I supplies local statistics, quadrants, spatial lag, raw two-sided permutation p-values, and Benjamini-Hochberg FDR-adjusted p-values. Each analysis uses 999 permutations, seed `20260730`, and alpha 0.05. The primary labels use FDR-adjusted significance: High-High missed cluster, Low-Low visited cluster, High-Low outlier, Low-High outlier, or Not significant.

## Results and limits

The primary Global Moran's I was 0.020281 (expected -0.000432; z=2.267140; permutation p=0.026; fully revised 2026-07-31, originally 0.046612/p=0.001), still indicating positive global autocorrelation in the observed indicator at alpha 0.05. No primary local results remained significant after FDR correction, before or after the revision. Raw local results remain available for operational screening but must not be presented as confirmed local discoveries.

The distance-band sensitivity produced I=0.030441 (expected -0.000432; z=6.597646; p=0.001), still significant. The ambiguity-included k=8 sensitivity produced I=0.012755 (expected -0.000390; z=1.519055; p=0.140) -- this scenario is **no longer statistically significant** after the revision, unlike the other two, and unlike its own pre-revision result (p=0.008). This is reported plainly because it is a genuine consequence of the correction, not a discretionary choice: the ambiguity-included population is the largest and most diluted of the three, and the corrected, sparser missed-indicator signal no longer clears the significance bar there. Both sensitivity analyses have no FDR-significant local results regardless. The distance-band raw screening counts are 78 Low-Low, 40 Low-High, and 54 High-Low (out of 2,318); the ambiguity sensitivity has 53 Low-Low, 86 Low-High, and 10 High-Low (out of 2,562). The primary scenario's own raw screening counts are 63 Low-Low and 4 Low-High, with no High-Low outliers. These counts are not confirmed hotspots.

Spatial results identify concentration only. They do not establish causation, prove that an individual settlement was truly missed, establish team misconduct, or establish whether individual children were vaccinated. Results depend on GPS QA, settlement attribution, the missed definition, weights, permutation inference, and FDR correction. The high prevalence of the missed indicator also creates an imbalanced binary outcome that limits contrast between local categories.
