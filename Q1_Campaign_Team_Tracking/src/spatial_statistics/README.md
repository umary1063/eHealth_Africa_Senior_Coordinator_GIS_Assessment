# Spatial Statistics

This package implements Requirement 5: Global and Local Moran's I for the GPS-derived missed-settlement indicator. It reads the baseline reconciliation population from PostGIS, calculates weights in EPSG:32632, runs 999 fixed-seed permutations, and retains both raw and Benjamini-Hochberg FDR-adjusted local inference.

The primary analysis uses binary, row-standardized eight-nearest-neighbour weights and excludes ambiguous GPS classifications. Distance-band and ambiguity-included analyses are sensitivity checks. Spatial results describe concentration of the observed indicator only; they do not establish cause or confirm individual service delivery.

Executed primary results: 2,318 non-ambiguous settlements; Global Moran's I 0.020281, expected I -0.000432, z-score 2.267140, and 999-permutation p-value 0.026 (fully revised 2026-07-31 after four compounding GPS-pipeline defects were found and fixed -- see `technical_decisions.md`; originally 2,382 settlements, I=0.046612, p=0.001). No primary Local Moran test is FDR-significant, before or after the revision. The ambiguity-included sensitivity scenario, run on all 2,562 settlements, is no longer significant at all after the revision (I=0.012755, p=0.140) -- reported plainly as a genuine consequence of the correction. Raw local labels are retained solely for transparent exploratory review.
