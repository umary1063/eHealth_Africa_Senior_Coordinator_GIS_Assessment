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
