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

**Fully revised 2026-07-31.** A read-only audit found that the supplied GPS track files, despite
being named one file per team per day, actually contain 6–21 days of continuous logging each;
for 66 of 160 team-days two different files both produced GPS fixes during real duty hours on the
same real campaign date, which is physically impossible for one team and was silently corrupting
attribution. Correcting this properly required finding and fixing three further, compounding
defects: a 1000x unit-conversion bug in the implausible-speed rule; that same rule's sequence
computations still crossing contaminated files after the first fix; and a stale-flag-accumulation
bug that silently re-polluted two earlier correction attempts within this same review before being
found. All four are documented in [technical_decisions.md](technical_decisions.md) (2026-07-31
entries), including the false starts, because a live technical walkthrough is exactly the kind of
setting where "why did the number change three times" needs a real answer. The numbers below are
from the final pipeline re-run, verified consistent between the database and every output file.

Validated attribution classified 139 settlements as visited under the 30 m baseline. A 60 m sensitivity scenario increased this to 171 while also increasing ambiguous classifications; the urban accuracy-aware scenario classified 142 settlements as visited. The baseline remains the primary operational estimate.

Coverage reconciliation found a substantial 73.26 percentage-point gap between baseline GPS coverage (5.43%) and e-tally-reported coverage (78.69%, essentially unchanged by the GPS-side fixes). The reconciled product is the operational decision source; mismatches require rapid verification before mop-up. The gap's size is itself part of the evidence: e-tally reporting this high is implausible against a literal 5.43% physical-coverage rate, so the reconciliation brief treats this as most consistent with GPS-attribution and data-density limitations rather than a literal near-total delivery failure.

Requirement 5 found positive global autocorrelation in the observed GPS-derived missed indicator under the primary k=8 weights (Global Moran's I 0.020281; permutation p=0.026). No local results remained significant after FDR correction, so raw local patterns are retained for screening rather than presented as confirmed local clusters. The ambiguity-included sensitivity scenario lost significance entirely after the correction (p=0.140) — reported plainly rather than smoothed over. See [the spatial-statistics method](docs/missed_settlement_cluster_method.md) for weights, sensitivity analyses, and interpretation limits.

The primary analysis contains 2,318 non-ambiguous settlements (2,179 unvisited and 139 visited). It uses EPSG:32632 binary, row-standardized k=8 nearest-neighbour weights, 999 permutations, seed `20260730`, and Benjamini-Hochberg FDR correction. The 9,050 m distance-band and ambiguity-included scenarios are sensitivity analyses only.

## Requirement 6 Decision Products

The A3 technical map and Incident Manager brief translate observed evidence into cautious operational recommendations. A GPS-unvisited classification means no confirmed GPS visit evidence under the baseline method; it is not proof that a settlement was genuinely missed. Recommendations state evidence confidence and prioritize rapid verification, supervisor follow-up, device inspection, repeat-visit confirmation, and data reconciliation before mop-up deployment or any performance conclusion.
