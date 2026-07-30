# Incident Manager Decision Brief: Next 24 Hours

## Executive summary

The reconciled evidence shows a substantial gap between confirmed GPS visit coverage (8.35%) and e-tally-reported coverage (78.69%). This is a rapid-verification problem, not proof of non-performance: absence of GPS evidence may reflect a genuine missed settlement, logger failure or non-use, signal loss, attribution uncertainty, identifier mismatch, timing mismatch, or a processing issue.

Deploy supervisors to verify the highest-priority disagreement locations before assuming teams failed to visit. Use the reconciled product, not GPS or e-tally alone, for tomorrow's decisions.

## Situation

2,562 planned settlements were reconciled under the baseline 30 m GPS attribution scenario. There are 1,640 definitive GPS/e-tally disagreements, 180 ambiguous GPS classifications, and seven e-tally records with identifiers unmatched to planned settlements.

## Evidence

| Evidence | Finding | Confidence |
|---|---:|---|
| GPS coverage | 8.35% confirmed GPS visit evidence | High for the measured GPS evidence; not proof of service delivery |
| E-tally coverage | 78.69% reported settlements | High for reported service evidence; not proof of physical arrival |
| Definitive agreement | 31.15% | Moderate: agreement reflects two imperfect sources |
| Coverage discrepancy | 70.34 percentage points | High: operationally substantial reconciliation gap |
| Local hotspots | No Local Moran result survived FDR correction | High: no confirmed local hotspot claim is supported |

## Operational priorities

### Priority 1 - Verify e-tally-reported settlements without confirmed GPS visit evidence

- **Why:** 1,639 settlements were e-tally reported but GPS-unvisited under the baseline method.
- **Evidence:** reported service record without corroborating physical-presence evidence.
- **Confidence:** Low for a conclusion about actual non-visit; high priority for verification.
- **Suggested field action:** supervisor call-back and repeat-visit confirmation; inspect logger assignment, battery status, and device carry/use; reconcile team, date, settlement ID, and reporting time before mop-up assignment.

### Priority 2 - Verify settlements with neither GPS visit evidence nor e-tally report

- **Why:** 529 planned settlements have no confirmed GPS visit evidence and no linked e-tally report.
- **Evidence:** two sources are absent, but neither absence proves failure.
- **Confidence:** Low to moderate; potentially stronger mop-up candidates only after rapid supervisor verification and access review.
- **Suggested field action:** contact ward supervisors, confirm access/security status, check device logs and tally workflow, then schedule repeat visit where non-delivery is confirmed.

### Priority 3 - Resolve ambiguous GPS attribution before classification

- **Why:** 180 settlements have ambiguous GPS evidence.
- **Evidence:** multiple or uncertain eligible attribution candidates; these are not confirmed visits or confirmed missed settlements.
- **Confidence:** Low.
- **Suggested field action:** verify settlement coordinates and team movement context; reconcile with supervisor records and e-tally before placing in a mop-up route.

## Uncertainty

Possible GPS logger failure, logger non-use, battery failure, signal loss, reporting mismatch, attribution uncertainty, identifier mismatch, and timing mismatch cannot be distinguished from genuine missed settlements using current evidence alone. Seven unmatched e-tally IDs require data reconciliation. Do not use these findings for disciplinary or performance action.

## Recommended action within 24 hours

Prioritize rapid verification before assuming non-performance. Assign ward supervisors to Priority 1 and Priority 2 locations; confirm repeat visits where needed; inspect devices and GPS-log capture; and reconcile unmatched IDs, team/date/settlement identifiers, and e-tally timing. Treat inaccessible settlements as operational constraints requiring access coordination rather than performance exceptions.

<sub>Technical appendix: Primary Global Moran's I is significant (I=0.046612; 999-permutation p=0.001). No Local Moran findings survive Benjamini-Hochberg FDR correction. Exploratory local patterns must not be used as evidence of true operational hotspots.</sub>
