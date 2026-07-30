# GPS Quality Validation

This note records how to interpret outputs from the documented, non-destructive GPS quality assessment.

## Interpreting QA Flag Counts

QA flags represent rule violations, not unique GPS observations. Six independent quality rules are evaluated for every GPS point. A single observation may trigger multiple rules simultaneously, for example outside campaign hours, poor positional accuracy, and impossible calculated speed.

Therefore, total QA flags can legitimately exceed the total number of GPS observations. The reported total of 1,888,426 flags across 956,702 GPS points indicates overlapping quality issues rather than duplicate records.
