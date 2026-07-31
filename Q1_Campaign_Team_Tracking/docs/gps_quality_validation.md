# GPS Quality Validation

This note records how to interpret outputs from the documented, non-destructive GPS quality assessment.

## Interpreting QA Flag Counts

QA flags represent rule violations, not unique GPS observations. Seven independent quality rules are evaluated for every GPS point (added `source_file_date_mismatch` on 2026-07-31; see `technical_decisions.md` and `src/quality/README.md`). A single observation may trigger multiple rules simultaneously, for example outside campaign hours, poor positional accuracy, and impossible calculated speed.

Therefore, total QA flags can legitimately exceed the total number of GPS observations. The final, fully-corrected total is 2,023,508 flags across 956,702 GPS points (originally 1,888,426 flags before any of the four defects documented in `technical_decisions.md` were found; the total moved substantially during the correction process itself, since two of those defects were bugs in the `impossible_speed` and `reported_speed_disagreement` rule computations, not just the new seventh rule). `source_file_date_mismatch` accounts for 818,397 flagged points (85.5% of all raw points) -- by far the largest single category, because it is the rule that catches the file/date defect. After the two speed-computation bugs were fixed, `impossible_speed` fell to 5,612 points (0.59%) and `reported_speed_disagreement` to 1,529 (0.16%) -- both were previously inflated to roughly a third of all points by a unit-conversion error and by chaining sequence calculations across contaminated files; see `technical_decisions.md` for the full defect-by-defect account.
