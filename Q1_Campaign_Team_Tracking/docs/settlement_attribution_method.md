# Settlement Attribution Method

## Spatial method

GPS and settlement source geometries are retained in EPSG:4326 and transformed to EPSG:32632 for all metre-based distance calculations. For each scenario, PostGIS selects the deterministic nearest planned settlement within the applicable tolerance. `settlement_id` is the authoritative key.

## Reference-data prerequisite

Before attribution, the dedicated `src.ingestion.ingest_reference_data` command loads supplied state, LGA, ward, and settlement records into PostGIS. Notebook 03 does not read raw source files: it checks for 2,562 settlements, 40 wards, 4 LGAs, and 1 state record, then fails clearly when the database is incomplete. This separates repeatable source loading from analytical execution.

## Scenarios

| Scenario | Tolerance |
|---|---|
| `baseline_30m` | Fixed 30 m. |
| `sensitivity_60m` | Fixed 60 m for every settlement. |
| `urban_accuracy_aware` | For `Urban block` settlements only: `max(30 m, reported accuracy_m)`, capped at 60 m; 30 m otherwise. |

The 30 m baseline aligns with the documented positional-accuracy screening threshold. The 60 m sensitivity ceiling is supported by the observed maximum reported positional accuracy of 58 m. The settlement nearest-neighbour distribution has a 5th percentile of 195.1 m, so both tolerances remain substantially below typical settlement spacing. Where more than one settlement is within the applicable tolerance, the nearest settlement is retained for review with `confidence_class = ambiguous` and is excluded from confirmed visit evidence.

## Eligibility and visit reconstruction

Confirmed-evidence eligibility requires a valid timestamp and geometry, being inside the documented campaign date and duty-hour window, and no impossible-speed flag. Accuracy, reported-speed disagreement, stationary-cluster, and sequence-gap flags remain available as QA evidence.

Observations are split into team, campaign-date, and settlement episodes at time gaps greater than 15 minutes. A confirmed visit requires a non-ambiguous episode with at least three eligible points, at least 15 minutes between its first and last timestamp, and no internal interval above 15 minutes. Short three-point sequences are therefore not confirmed visits.

## Interpretation

Validated execution produced 214 visited, 180 ambiguous, and 2,168 unvisited settlements under `baseline_30m`. The `sensitivity_60m` scenario produced 241 visited, 225 ambiguous, and 2,096 unvisited settlements: 27 additional visited settlements, alongside 45 additional ambiguous settlements. The `urban_accuracy_aware` scenario produced 216 visited, 181 ambiguous, and 2,165 unvisited settlements: a marginal increase of 2 visited and 1 ambiguous settlement over baseline.

The 30 m scenario remains the primary operational estimate. The 60 m scenario is retained as sensitivity analysis because it changes the visit count but introduces more ambiguity. The urban-specific adjustment is documented but does not materially change campaign conclusions. These are tracking-evidence classifications, not proof of vaccination delivery.
