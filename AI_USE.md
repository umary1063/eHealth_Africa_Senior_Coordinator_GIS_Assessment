# AI Use Disclosure

AI assistance was used selectively during this submission, disclosed per-module below. In every
case, design decisions, judgement calls (thresholds, ranges, structural choices), and analytical
interpretation are the candidate's own; AI assistance is limited to drafting, scaffolding, and
mechanical generation from decisions the candidate specified and reviewed.

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

## Other modules

To be completed as each module is finalised.
