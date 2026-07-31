# GPS Quality Assessment

## Purpose

This module identifies potential GPS quality concerns while preserving all raw observations. Its output is a set of documented flags in `processed.gps_quality_flags`, not a cleaned or deleted source dataset.

## Rules and Provisional Thresholds

| Rule | Provisional rule | Rationale and limitation |
|---|---|---|
| Impossible speed | Reported or calculated sequential speed above 80 km/h | A high ceiling flags likely GPS jumps while avoiding treatment of every vehicle movement as invalid. It is a review flag, not proof of error. **Two bugs found and fixed 2026-07-31** (`technical_decisions.md`): `calculated_speed_kmh` was computed in metres per hour, not km/h (a 1000x inflation), and the previous-point chain it depends on crossed contaminated wrong-day files even after that fix. Both together had inflated this rule from a true 0.59% to as much as 36.2% of all points. |
| Reported-speed disagreement | Difference between reported and calculated speed above 20 km/h | Compares logger-reported speed with coordinate-derived movement. Differences can result from device calculation methods or timing, not only error. Affected by the same two bugs as Impossible speed above; corrected rate is 0.16% of all points. |
| Positional accuracy | Missing `accuracy_m` or value above 30 m | Missing accuracy prevents direct confidence assessment; 30 m is a provisional tolerance for reviewing point-location uncertainty. It must be revisited for dense urban conditions. |
| Campaign hours | 9–13 March 2026, 07:00–19:00 | Dates are supplied by the assessment. The daily window is a documented operational assumption intended to flag, not discard, observations. |
| Sequence gap | More than 15 minutes since the preceding point | The audit documentation states that logger fixes are expected approximately every 60 seconds; 15 minutes highlights a sustained interruption without assuming every short delay is failure. |
| Stationary cluster | At least 30 minutes within a 25 m radius, with no sequence gap over 15 minutes | Identifies possible unattended devices. It can also reflect legitimate stationary work, breaks, or constrained movement. |
| Source-file date mismatch | Point's calendar date does not equal the date encoded in its own source file's name | Not an arbitrary threshold: the data pack states "one file per team per day." Full-file inspection (2026-07-31) found source files actually contain 6–21 days of continuous, one-point-per-minute logging beyond their nominal day, and for 66 of 160 team-days two different sibling files both contribute points during real duty hours on the same real campaign date -- physically impossible for one team. Restricting each file to its own nominal day is a direct, deterministic consequence of the data pack's own stated structure, not a judgement threshold. See `technical_decisions.md` for the full finding and its effect on downstream results. |

## Output

Each flag includes the raw GPS point reference, source file, team, timestamp, rule, boolean flag value, explanation, and database creation time. `upsert_quality_flags` fully replaces the table's contents on every run (clears it, then writes the freshly computed set) rather than only inserting or updating rows present in the new batch. An earlier, merge-only version of this function left stale flagged=True rows behind for any point that stopped being flagged after a rule fix, which silently corrupted three re-runs during the 2026-07-31 corrections before being found and fixed -- see `technical_decisions.md`.
