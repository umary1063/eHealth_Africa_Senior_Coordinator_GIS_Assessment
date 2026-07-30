# AI Use Disclosure

AI assistance was used selectively during this submission, disclosed per-module below. In every
case, design decisions, judgement calls (thresholds, ranges, structural choices), and analytical
interpretation are the candidate's own; AI assistance is limited to drafting, scaffolding, and
mechanical generation from decisions the candidate specified and reviewed.

## Q3 — Digital Form Development

Claude (Anthropic, Claude Sonnet 5, in Claude Code) was used to:

- Read and structure the paper questionnaire and reference media into an XLSForm field list.
- Draft `Q3_Digital_Form_Development/scripts/build_form.py`, which generates the XLSForm
  (`form/HH2026_v1.xlsx`) and the constraint register (`constraint_register.csv`) from a single
  set of field definitions.
- Run the actual conversion tool chain (pyxform 4.5.0 against ODK Validate, requiring a Java
  runtime installed for this purpose) and capture its output verbatim in
  `Q3_Digital_Form_Development/conversion/conversion_log.txt` — this is real tool output, not
  AI-generated text describing what the tool would say.
- Draft the documentation set in `Q3_Digital_Form_Development/documentation/`, the defects
  report, the specimen label check-digit proof, and the 43-case test plan, from the candidate's
  reading of the questionnaire, the operating conditions, and the supplied reference data
  (`reference_media/`), including data actually queried from the CSVs (row counts, coordinate
  extents, team/label range checks) rather than assumed.
- Every range, threshold, and design decision not directly stated in the source documents is
  explicitly labelled "my judgement" (or attributed to a named source) throughout the constraint
  register and documentation, rather than presented as authoritative.

## Other modules

To be completed as each module is finalised.
