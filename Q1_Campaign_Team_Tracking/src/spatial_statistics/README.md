# Spatial Statistics

This package implements Requirement 5: Global and Local Moran's I for the GPS-derived missed-settlement indicator. It reads the baseline reconciliation population from PostGIS, calculates weights in EPSG:32632, runs 999 fixed-seed permutations, and retains both raw and Benjamini-Hochberg FDR-adjusted local inference.

The primary analysis uses binary, row-standardized eight-nearest-neighbour weights and excludes ambiguous GPS classifications. Distance-band and ambiguity-included analyses are sensitivity checks. Spatial results describe concentration of the observed indicator only; they do not establish cause or confirm individual service delivery.

Executed primary results: 2,382 non-ambiguous settlements; Global Moran's I 0.046612, expected I -0.000420, z-score 4.821064, and 999-permutation p-value 0.001. No primary Local Moran test is FDR-significant. Raw local labels are retained solely for transparent exploratory review.
