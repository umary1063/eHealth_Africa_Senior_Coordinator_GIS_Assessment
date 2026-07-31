# Incident Manager Decision Brief: Next 24 Hours

*Fully revised 2026-07-31 after four compounding GPS-pipeline defects were found and fixed (`technical_decisions.md`); every figure below reflects the final, verified-consistent state.*

## Executive summary

Confirmed GPS visit coverage is 5.43%, against 78.69% e-tally-reported coverage. This gap is too large to read literally -- e-tally reporting that high is not plausible alongside genuine 5.43% physical presence. **Treat this as evidence of a GPS-attribution and data-completeness limitation, not as evidence that most settlements were unserved.** It remains a rapid-verification problem, not proof of non-performance.

With 1,657 of 2,562 settlements in definitive disagreement, full census verification is not achievable in 24 hours. Work the ward-ranked order below, not settlement order, and treat GPS absence as inconclusive.

## Situation

1,657 definitive GPS/e-tally disagreements, 244 ambiguous GPS classifications, and seven unmatched e-tally identifiers. All 40 wards now show at least one disagreement, so the ward "requires review" flag no longer differentiates priority -- rank by percentage-point gap instead (`ward_coverage_reconciliation.csv`).

## Evidence

| Evidence | Finding | Confidence |
|---|---:|---|
| GPS coverage | 5.43% confirmed visit evidence | High for the measured evidence; not a credible estimate of true coverage given the gap below |
| E-tally coverage | 78.69% reported settlements | High for reported service; not proof of physical arrival |
| Definitive agreement | 28.52% | Low: the two sources disagree far more than they agree |
| Coverage discrepancy | 73.26 percentage points | Very high -- too large to act on literally; escalate to data engineering alongside fieldwork |
| Local hotspots | No Local Moran result survived FDR correction | High: no confirmed hotspot claim is supported |

## Operational priorities

### Priority 1 - Phased verification, worst ward-level gap first

1,654 settlements are e-tally reported but GPS-unvisited -- too many to visit in 24 hours. Rank wards by `absolute_percentage_point_difference` and start with the worst: the ten worst (Mawako, Enyoko-Kofar, UMZABA-KOFAR, Wangoja, Wangoni, BISANI-GABAS, Dodeta, NUNGONI-AREWA, ADWANA, YESAWO -- mostly Ilela and Gwarin LGAs, one in Katsuma) each show 83-91pp gaps, most with 0-5 GPS-confirmed visits against 32-75 e-tally-reported settlements. Confidence in any individual non-visit conclusion is low; priority for verification is high. Supervisor call-back and repeat-visit confirmation in the worst wards first; inspect logger/device/battery status for the teams that served them; reconcile team, date, settlement ID, and reporting time. Escalate the scale of the shortfall to data engineering in parallel -- this is not solely a field problem.

### Priority 2 - No GPS evidence and no e-tally report

525 settlements have neither. No competing delivery claim to explain away, so these are arguably stronger mop-up candidates than Priority 1 once its worst wards are underway. Confirm access/security status, check device logs and tally workflow, schedule repeat visits where non-delivery is confirmed.

### Priority 3 - Resolve ambiguous GPS attribution

244 settlements have multiple or uncertain attribution candidates -- not confirmed visits or confirmed misses. Verify coordinates and team movement context against supervisor records before routing into mop-up.

## Uncertainty

Logger failure or non-use, battery failure, signal loss, reporting mismatch, attribution uncertainty, identifier mismatch, and timing mismatch cannot be distinguished from genuine missed settlements from this evidence alone. The scale of this gap makes a data/attribution explanation more likely than a literal reading: true 5.43% coverage alongside 78.69% e-tally reporting would itself be a remarkable, separately-investigable finding. Do not use these findings for disciplinary or performance action.

## Recommended action within 24 hours

Do not attempt exhaustive settlement-by-settlement verification; the volume exceeds 24-hour capacity. Work Priority 1's worst-ranked wards first while escalating the GPS data-completeness gap to data engineering as its own workstream, then move to Priority 2 and 3 as capacity allows. Reconcile unmatched IDs and team/date/settlement identifiers. Treat inaccessible settlements as an access-coordination constraint, not a performance exception.

<sub>Technical appendix: Primary Global Moran's I is significant (I=0.020281; 999-permutation p=0.026; fully revised 2026-07-31, originally I=0.046612/p=0.001). No Local Moran findings survive FDR correction, before or after the revision. The ambiguity-included sensitivity scenario is no longer significant at all after this revision (p=0.140) -- reported for completeness, not used operationally. Exploratory local patterns are not evidence of true operational hotspots.</sub>
