# Coverage Reconciliation Method

E-tally records are at `campaign_date + team_id + settlement_id` grain. A linked row is reported service evidence; it is not proof of physical arrival. The baseline GPS visit classification is physical-presence evidence; it is not proof of vaccination.

Settlement coverage uses planned settlements as the denominator. GPS coverage is confirmed GPS visits divided by planned settlements; e-tally coverage is linked reported settlements divided by planned settlements. Reconciliation classes retain visited, unvisited, and ambiguous GPS evidence separately.

Unmatched IDs are retained outside the linked raw table. Duplicate reporting keys are reported explicitly. Raw doses are preserved; totals report all linked doses and plausible-only doses excluding rows above their reported target population.

Ward severity is an operational triage rule, not a statistical significance test: low <10 percentage points, moderate 10–24.9, high >=25. Present the reconciled product to the Incident Manager. GPS is stronger evidence of presence; e-tally is stronger evidence of reported delivery and doses. Neither alone proves both.

Strict agreement is GPS visited/e-tally reported plus GPS unvisited/no e-tally report. Definitive agreement rate is agreement divided by agreement plus disagreement, excluding ambiguous GPS cases. Execution found 742 agreements, 1,640 disagreements, and 180 ambiguous cases (31.15% definitive agreement). The 70.34 percentage-point GPS/e-tally coverage gap is operationally substantial. Of the disagreements, 1,639 settlements were e-tally reported but GPS unvisited and one was GPS visited without e-tally reporting. These findings do not alone prove false reporting: logger non-use or failure, poor capture, identifier or timing mismatch, and genuine reporting without corroborating GPS evidence remain plausible. Verify disagreements before mop-up.
