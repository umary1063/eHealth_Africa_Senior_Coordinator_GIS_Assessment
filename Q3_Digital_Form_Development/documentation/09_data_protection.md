# Data protection

Q3 requirement 12.

## What was configured

- **Confidentiality banner retained.** The paper form's confidentiality notice and ethics
  approval reference (`BSHREC/2026/041`) are reproduced as the form's opening note, unchanged —
  removing or softening ethics-approved consent/confidentiality text is not something a
  digitisation exercise should do unilaterally (same principle as defect handling: no silent
  edits to ethics-approved content).
- **Consent gates data collection structurally, not just procedurally.** `s3` (roster, onward)
  is only `relevant` when `${visit_result}='1' and ${consent_given}='1'` — a refusal at 2.02
  cannot result in any household, roster, child, or specimen data being entered at all, because
  the fields are not merely skipped by instruction (as on paper) but are not rendered or
  storable by the form.
- **Specimen labels carry no name.** `specimen_label` links a specimen to a *label number* (and,
  via the form's own structure, to a specific roster line within a specific household
  submission) — never to `member_name` directly in the same field. The link from label to name
  exists only through the household submission as a whole, which is exactly the level at which
  the paper form's own confidentiality control (custody of the completed form) already operates.
- **`device_id` and `enumerator_code` are collected**, which are indirect identifiers of
  *fieldworkers*, not respondents — justified in `08_fabrication_detection.md` as necessary for
  the daily QA checks; without them, per-enumerator monitoring (an explicit requirement of this
  question) is not possible.
- **GPS is collected at the dwelling (1.11), not at the child or specimen level.** No additional
  precise-location field was added beyond what the paper form already specifies.

## What the questionnaire collects that it arguably need not

1. **`member_name`/`c_name` (name or initials) for every household member, not only eligible
   children.** The roster's stated purpose (Section 3 instruction) is to identify who is eligible
   for Section 4 and to support the household-size cross-check — both achievable with a line
   number, relationship, sex, and age, none of which requires a name. A name or initials adds
   re-identification risk for members who are never otherwise the subject of any question (adults
   not the household head, older children) with no analytic use of the name field itself (it is
   not used in any calculation, cross-check, or output table in `10_codebook.md`).
2. **`settlement_local_name` (1.05) is free text with no stated retention/use rule.** It is useful
   operationally (matching local usage to the register) but is exactly the kind of open free-text
   field that tends to accumulate incidental personal or locational detail beyond its stated
   purpose if enumerators over-write it (e.g. "known as the place near [named family]'s
   compound").
3. **`supervisor_note` (7.02) is unrestricted free text**, explicitly intended to help the office
   interpret the form — but with no guidance on what it should and should not contain, it is a
   predictable place for a supervisor to write something identifying or sensitive about a specific
   respondent that does not belong in a field with no defined retention rule.

## What I would propose removing or restricting

- **Replace `member_name`/`c_name` with initials-only for non-index household members**, keeping
  full name only where an operational need is stated (none was, beyond the child whose card is
  being checked — and even there, a first name or initials is sufficient to match the roster line
  to the vaccination card being examined in the same sitting; nothing downstream needs a full
  name). I did not implement this — the paper form asks for "name or initials," so an enumerator
  can already choose initials; forcing initials-only would go beyond digitising the instrument
  into re-authoring an ethics-approved data item, which is exactly the kind of unilateral edit
  `01_defects_report.md` argues against for defects. Flagging it here for the ministry's own data
  minimisation review, as requirement 12 asks for a view, is the right level of action for this
  deliverable.
- **Add a short guidance hint to `supervisor_note`** ("Do not record respondent names or other
  identifying detail here") — a one-line addition I judged did not need ministry sign-off (no
  data item is added, removed, or redefined) and would have added it, but left it out to keep this
  submission's scope to what the required deliverables ask for; noted here as a low-cost follow-up.
- **`settlement_local_name` should carry an explicit retention/purpose statement** in the
  ministry's data management plan (outside the form itself) so field staff and analysts know it is
  operational metadata for register matching, not a general free-text box.

## What was not addressed

Encryption at rest (device and Central), access control on the Central project, and the formal
data management plan referenced by the ethics approval are all governance/infrastructure matters
outside what an XLSForm can configure, and outside the reference media supplied. They are named
here as out of scope rather than left unmentioned — see `11_scope_and_omissions.md`.
