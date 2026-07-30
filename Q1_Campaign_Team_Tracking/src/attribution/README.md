# Settlement Attribution

This package assigns in-scope GPS observations to the deterministic nearest planned settlement in PostGIS and reconstructs evidence-based settlement visit episodes.

It implements three separate scenarios: `baseline_30m`, `sensitivity_60m`, and `urban_accuracy_aware`. Raw GPS observations are not changed. Scenario output records retain QA evidence, candidate counts, distances, the selected nearest settlement, and a confidence class.

A confirmed visit requires a non-ambiguous, baseline-eligible episode for one team, campaign date, and settlement with at least three points, at least 15 minutes elapsed dwell time, and no internal gap above 15 minutes.
