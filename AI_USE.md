# AI Use Disclosure

AI assistance was used selectively during this submission, disclosed per-module below. In every
case, design decisions, judgement calls (thresholds, ranges, structural choices), and analytical
interpretation are the candidate's own; AI assistance is limited to drafting, scaffolding, and
mechanical generation from decisions the candidate specified and reviewed.

## Q1 — Campaign Team Tracking and Coverage Reconciliation

Built using OpenAI Codex and ChatGPT for code scaffolding and drafting, alongside the candidate's
own design decisions, review, and analysis — the same standard as the rest of this document:
thresholds, methodological choices (attribution tolerance distances, spatial weights definition,
QA rule cut-offs, the reconciliation source-of-record decision), and interpretation of results are
the candidate's own; AI assistance was limited to drafting and mechanical generation. This module
was built in earlier working sessions with those tools, not in Claude Code, so the per-decision,
per-correction level of disclosure given for Q3 below (which was built interactively in this tool)
is not reconstructable from this session and is not attempted here.

**Read-only audit and subsequent fix, 2026-07-31, in Claude Code.** A requested read-only audit of
Q1 against the assessment's stated requirements found, among other things, that the supplied GPS
track files contain 6–21 days of continuous logging each despite being named one file per team per
day, and that this was silently corrupting settlement attribution for 66 of 160 team-days. With the
candidate's explicit direction to implement a full fix rather than merely document the finding,
Claude: added a seventh, documented QA rule (`source_file_date_mismatch`) and wired it into the
attribution query; started, then — on the candidate's explicit instruction mid-task — reverted an
attempt to add Hausa translations to Q3 constraint messages in the same session, replacing it with
an escalated-defect note instead (see the Q3 entry below); started, and here completed, Docker
Desktop setup, Python environment setup, and a full re-run of the Q1 pipeline (QA → attribution →
visit classification → reconciliation → cluster analysis → cartography) against the live PostGIS
container from the candidate's original build; fixed a pre-existing (not AI-introduced) hardcoded-
statistics bug in the coverage-reconciliation notebook and an equivalent one found afterward in the
A3 cartography script, both by making them read from their own computed output rather than literal
numbers; re-executed all five Q1 notebooks headlessly (the standard `jupyter nbconvert --execute`
path was unreliable in this environment, so a purpose-built in-process executor was used instead,
disclosed in case its output differs subtly from a real Jupyter kernel's); and propagated the
corrected figures through every Q1 markdown document, the top-level README, and
`docs/Q1_Technical_Response.docx`. A second, unrelated documentation/code mismatch (ward severity
described as a three-tier percentage-point scale in `docs/coverage_reconciliation_method.md` but
implemented in `src/reconciliation/ward_coverage.py` as a binary flag) was found and corrected to
describe the code as it actually behaves. This first fix produced a corrected estimate of 50 visited
settlements at the 30 m baseline (originally 214), which was reported to the candidate as final.

**Three further defects found during the candidate's own request to verify the fix, same session.**
When the candidate asked Claude to re-check the first fix against the source requirements, Claude
independently re-verified rather than re-asserting the same figures, and this surfaced three further,
compounding defects, all disclosed here in full because each intermediate figure was reported to the
candidate as final before the next one was found:

1. The visited-settlement count did not move at all after a plausible-looking second fix (a missing
   metres-to-kilometres conversion in the "implausible speed" QA rule, inflating calculated speed
   1000x), which Claude flagged to the candidate as suspicious rather than accepting; hand-verification
   on a genuinely clean point confirmed the bug, but fixing it alone still had zero visible effect.
2. Investigating that non-effect found a second, compounding bug: the same rule's sequence
   computations (previous point, gap, calculated speed, stationary clustering) still chained across
   the contaminated wrong-day files identified in the first fix, so a corrected formula was still being
   fed physically unrelated point pairs. Fixing this raised the estimate to 55 visited settlements,
   again reported to the candidate as final.
3. A discrepancy between the live database (55) and the notebook-written CSV outputs (still 50)
   prompted a direct check that found `upsert_quality_flags` had never removed a flag row once a point
   stopped being flagged across any of the session's re-runs — every fix had been silently re-polluted
   by its own predecessor's stale flags, going back to the very first re-run. Fixing this and re-running
   the entire pipeline one final time, with the database and every output file directly cross-checked
   for agreement before anything was reported, produced the true final figure: 139 visited settlements
   at the 30 m baseline.

The candidate explicitly asked Claude to pause mid-pipeline and re-read the original Q1 requirements
against everything changed, to check for scope drift; Claude did so and reported back that every
change traced to one of the six numbered requirements (the required QA rules and their correctness,
required attribution/reconciliation/cluster-statistic methodology left unchanged, and the required
decision brief's actual operational deployability). All specific numbers, thresholds, and the
interpretation of the widened GPS/e-tally gap (treated as a data-attribution artefact, not a literal
coverage claim) are Claude's drafting of an argument explained to and directed by the candidate
in-session; see `Q1_Campaign_Team_Tracking/technical_decisions.md` (2026-07-31 entries) for the full
technical record, including the false starts.

## Q3 — Digital Form Development

Claude (Anthropic, Claude Sonnet 5, in Claude Code) was used throughout, across a multi-session
build-and-test cycle, disclosed here in full rather than summarised to the finished state only.

**Initial build.** Claude read and structured the paper questionnaire and reference media into an
XLSForm field list; drafted `Q3_Digital_Form_Development/scripts/build_form.py`, which generates
both the XLSForm (`form/HH2026_v1.xlsx`) and the constraint register
(`constraint_register.csv`) from one set of field definitions so the two cannot drift apart; ran
the actual conversion tool chain (pyxform 4.5.0 against ODK Validate, a Java runtime installed for
this purpose) and captured its output verbatim in `conversion/conversion_log.txt` — real tool
output, not AI-generated text describing what the tool would say; and drafted the documentation
set, the specimen-label check-digit proof, and the test plan from the candidate's reading of the
questionnaire, the operating conditions, and data actually queried from the reference CSVs (row
counts, coordinate extents, team/label ranges) rather than assumed. Every range, threshold, and
design decision not directly stated in the source documents is labelled "my judgement" or
attributed to a named source throughout, rather than presented as authoritative.

**Corrections during review and live testing.** The candidate tested the built form on
KoboToolbox and later on a self-hosted ODK Central instance, and directed several corrections that
are disclosed here because they matter for how this deliverable should be read:

- A translation-policy bug (a 120-row choice list rendering an untranslated placeholder string
  in Hausa 120 times over) was found by the candidate on KoboToolbox and fixed.
- Claude twice attempted to fill the data-pack's missing-medicine-list gap (question 4.13) with
  substitute content — first an illustrative antibiotic list, then a free-text fallback — before
  the candidate explicitly instructed that gaps be reported, not filled in with content chosen on
  the AI's own initiative, sourced or not. The field was rebuilt as a `select_one_from_file`
  against a genuinely empty stub CSV instead. This correction, and the reasoning behind it, is
  recorded in full in `documentation/01_defects_report.md` (defect D-05) and
  `documentation/06_language_and_translation.md`, not edited out of the record.
- A Section 7 relevance bug (the enumerator's own sign-off unreachable in refused/vacant/
  no-consent outcomes, contradicting both the paper form and two of the form's own on-screen
  notes) was found by rendering the live form on the candidate's self-hosted Central instance via
  a public access link, and fixed.
- At the candidate's explicit request, a clearly-labelled dummy CSV
  (`testing/medicine_list_DUMMY_FOR_CENTRAL_TESTING_ONLY.csv`, obviously fake entries) was added
  purely to unblock manual click-through testing of one field on the test Central project; it is
  documented as a testing aid only and does not replace the empty stub that ships with the actual
  deliverable.

Version numbers (`2026060100` → `2026073100` → `2026073101`) and the infrastructure record in
`documentation/07_deployment_and_version_control.md` reflect this iterative process rather than a
single one-shot build.

**Post-audit correction, 2026-07-31.** An independent read-only audit (below) flagged that all 13
`constraint_message` fields are English-only, which risks the assessment's own automatic-loss-of-
marks condition on constraint messages in a language the enumerator cannot read. Claude drafted
Hausa translations for all 13 messages and began adding them to `scripts/build_form.py`; the
candidate stopped this before it was completed or rebuilt, instructing that no translation be
added and that the gap instead be documented as an escalated defect. The partial edit was reverted
via `git restore` (never rebuilt, converted, or committed), and `documentation/06_language_and_translation.md`
and `documentation/11_scope_and_omissions.md` were instead updated to name the `constraint_message`
gap explicitly as a pre-deployment blocker requiring professional translation and native-speaker
review, using the same resolved-vs-escalated framing as the defects report, rather than leaving it
as background reasoning only. Separately, `test_plan.csv` row T26 was found to cite two incorrect
cross-references (`constraint_register.csv` row C022, which is an unrelated keyboard-appearance
fix, and `documentation/01_defects_report.md`, which does not discuss the household-size-vs-roster
check at all) and was corrected to cite the actual rule, row C024.

## Q5 — Technical Coordination, and Q6 — Capability Development

Claude (Anthropic, Claude Sonnet 5, in Claude Code) drafted the prose of both written responses
(`Q5_Technical_Coordination/Q5_Response.docx`, `Q6_Capability_Development/Q6_Response.docx`) from
the candidate's own decisions and reasoning about the Part 3 scenario, and generated the `.docx`
files programmatically — including a shared eHealth Africa-styled template (headers, footers, page
numbers, colour theme) — so page counts against the stated limits (3 pages, 6 pages excluding
annexes) could be checked and controlled directly against the rendered PDF rather than estimated.

The technical decisions attributable to the candidate include: the choice of a PostGIS-native
controlled-editing workflow (staging tables, UUID identifiers, feature-level conflict detection,
named-reviewer merge approval, row-level audit history) as the named mechanism for concurrent
spatial editing in Q5, in preference to a dependency on an external versioning product; the
24-hour sequencing logic and its five ordering criteria; the split between blocking and flagging
data-quality rules; the categorised root-cause structure for the coverage discrepancy; the
interpretation of the Q6 capability-assessment evidence (the 0.11 self-rating/tested-knowledge
correlation and the zero-of-21 software-access finding) as the basis for course design rather than
the cohort's stated demand; the six-domain competency framework and its observable behaviours; the
five-day course sequencing and the explicit scope decision on what is not taught; the 0–4
demonstrated-capability scoring scale and the 90-day transfer-measurement plan; and the argument,
placed in each document's own concluding section rather than as a separate question, connecting
coordination fragility in Q5 to the counterpart's capability gap in Q6 — including its stated
limits (institutional capability reduces the likelihood of escalation, it does not eliminate the
operational cost of losing key staff).

This module was substantially reworked on 2026-07-31 against a detailed content brief supplied by
the candidate, which specified the structural argument to be carried through both responses, the
required tables and sections, the PostGIS-native (rather than GeoGig-dependent) editing
architecture, and the document's visual design. The rework was carried out directly in-session
rather than via an unattended external agent. A first pass of this rework incorrectly introduced a
separate "Question 7" document; the candidate corrected this, since Part 3 of the assessment
contains only Questions 5 and 6, and the coordination/capability connection is an expectation to
be argued within them, not a standalone compulsory question. That document was deleted and its
content folded into the concluding sections of Q5 and Q6 instead, as reflected above.

## Other modules

To be completed as each module is finalised.
