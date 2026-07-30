# GPS Quality Assessment

## Purpose

This module identifies potential GPS quality concerns while preserving all raw observations. Its output is a set of documented flags in `processed.gps_quality_flags`, not a cleaned or deleted source dataset.

## Rules and Provisional Thresholds

| Rule | Provisional rule | Rationale and limitation |
|---|---|---|
| Impossible speed | Reported or calculated sequential speed above 80 km/h | A high ceiling flags likely GPS jumps while avoiding treatment of every vehicle movement as invalid. It is a review flag, not proof of error. |
| Reported-speed disagreement | Difference between reported and calculated speed above 20 km/h | Compares logger-reported speed with coordinate-derived movement. Differences can result from device calculation methods or timing, not only error. |
| Positional accuracy | Missing `accuracy_m` or value above 30 m | Missing accuracy prevents direct confidence assessment; 30 m is a provisional tolerance for reviewing point-location uncertainty. It must be revisited for dense urban conditions. |
| Campaign hours | 9–13 March 2026, 07:00–19:00 | Dates are supplied by the assessment. The daily window is a documented operational assumption intended to flag, not discard, observations. |
| Sequence gap | More than 15 minutes since the preceding point | The audit documentation states that logger fixes are expected approximately every 60 seconds; 15 minutes highlights a sustained interruption without assuming every short delay is failure. |
| Stationary cluster | At least 30 minutes within a 25 m radius, with no sequence gap over 15 minutes | Identifies possible unattended devices. It can also reflect legitimate stationary work, breaks, or constrained movement. |

## Output

Each flag includes the raw GPS point reference, source file, team, timestamp, rule, boolean flag value, explanation, and database creation time. Re-running the same rules updates the matching point/rule record rather than adding a duplicate.
