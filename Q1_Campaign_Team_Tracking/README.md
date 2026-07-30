# Question 1: Campaign Team Tracking and Coverage Reconciliation

## Purpose

This component addresses the assessment scenario of a five-day house-to-house supplementary immunization activity. It establishes a reproducible approach for evaluating operational GPS tracking evidence, reconciling it with reported vaccination activity, and producing decision-ready coverage information.

## Campaign Tracking Problem

GPS logger observations, planned settlement locations, daily e-tally reports, and administrative boundaries provide complementary but imperfect views of campaign delivery. The work will assess data quality, determine whether planned settlements were visited, reconcile track-derived coverage with reported doses, and identify areas that may require operational follow-up.

## Planned Workflow

```text
Raw GPS data
    → spatial database
    → quality assurance
    → settlement attribution
    → coverage reconciliation
    → hotspot analysis
    → decision products
```

## Documentation

- [Methodology](methodology.md) records the analytical approach and its assumptions.
- [Technical decisions](technical_decisions.md) records material design choices and their rationale.
- [Data dictionary](data_dictionary.md) describes the supplied source datasets and derived data assets as they are defined.

## Q1 Outputs

GPS QA outputs are screening indicators that support downstream analysis and operational review. They are not automatic exclusion criteria: flagged observations remain available for documented interpretation in later stages.

Settlement attribution is evaluated under separate baseline and sensitivity scenarios. Proximity evidence supports visit classification but does not itself prove service delivery.

Validated attribution classified 214 settlements as visited under the 30 m baseline. A 60 m sensitivity scenario increased this to 241 while also increasing ambiguous classifications; the urban accuracy-aware scenario classified 216 settlements as visited. The baseline remains the primary operational estimate.

Coverage reconciliation found a substantial 70.34 percentage-point gap between baseline GPS coverage (8.35%) and e-tally-reported coverage (78.69%). The reconciled product is the operational decision source; mismatches require rapid verification before mop-up.

Requirement 5 found positive global autocorrelation in the observed GPS-derived missed indicator under the primary k=8 weights (Global Moran's I 0.046612; permutation p=0.001). No local results remained significant after FDR correction, so raw local patterns are retained for screening rather than presented as confirmed local clusters. See [the spatial-statistics method](docs/missed_settlement_cluster_method.md) for weights, sensitivity analyses, and interpretation limits.

The primary analysis contains 2,382 non-ambiguous settlements (2,168 unvisited and 214 visited). It uses EPSG:32632 binary, row-standardized k=8 nearest-neighbour weights, 999 permutations, seed `20260730`, and Benjamini-Hochberg FDR correction. The 9,050 m distance-band and ambiguity-included scenarios are sensitivity analyses only.
