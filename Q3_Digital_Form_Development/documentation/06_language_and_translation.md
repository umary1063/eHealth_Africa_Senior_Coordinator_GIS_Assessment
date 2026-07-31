# Language: Hausa in the field, English for supervisors and analysis

The operating conditions state interviews are conducted in Hausa, 38% of enumerators are not
confident readers of English, and supervisory review and analysis are in English. `settings sheet`
sets `default_language: Hausa (ha)`, and every field carries a `label::Hausa (ha)` column
alongside `label::English (en)`; a supervisor or the office can switch the running language from
the ODK Collect form-language menu without the form needing to be redeployed.

## Hints and guidance hints

Most interactive questions now also carry `hint::English (en)` / `hint::Hausa (ha)` -- a short
line always visible under the question, used for the kind of interviewer instruction the paper
form put inline (read the consent script exactly, observe the handwashing station rather than
just asking about it, record what the vaccination card says rather than what the caregiver
recalls). A handful of fields carry a `guidance_hint` as well -- ODK's separate, collapsed-by-
default "more info" panel, used only where there is genuinely deeper, optional detail that would
clutter the primary hint: the GPS accuracy threshold, the WHO recumbent/standing measurement
convention, the specimen label's check-digit behaviour, and the medicine-list placeholder caveat.
`guidance_hint` text is currently English-only, for the same reason `constraint_message` is
(above): it is the same register of procedural/technical precision, and a wrong translation there
carries the same risk as a wrong translation of the question text itself.

A small number of fields were left without a hint deliberately, not by omission -- where the
label plus its choice list is already unambiguous (`Sex`, `Supervisor code`, `State`), a hint
would only restate the label, which is padding, not information.

## Translation policy, and why it is a policy rather than a completed translation

Short, high-frequency, unambiguous items (yes/no/don't know, male/female, common nouns like
"name," "date," "household," basic instructions) were translated directly and are used throughout
`form/HH2026_v1.xlsx`.

Longer or clinically/procedurally precise text — full question sentences for the AMR and
anthropometry items, and every `constraint_message` — is marked
`[HAUSA: sai an fassara ta kwararre — professional translation pending]` rather than translated by
me. This is a deliberate scope decision, not an oversight (see the `Language 'Hausa (ha)' is
missing the survey constraint_message column` warning in `conversion/conversion_log.txt`, which is
this exact policy surfacing as a pyxform warning, not an error).

**Why:** a wrong clinical translation is more dangerous than an honest gap. An enumerator with low
confidence in English relying on a mistranslated Hausa prompt for, say, the antibiotic or
anthropometry questions could produce a systematically wrong answer with no error signal anywhere
in the pipeline — worse than the current, visible placeholder, which at least cannot be mistaken
for a validated translation. Professional translation with back-translation and field pre-testing
is a specialist task with its own methodology (typically: independent translation,
back-translation by a second translator, reconciliation, cognitive pre-testing with a small
enumerator sample) that is out of scope for this data-engineering deliverable and is recorded as
such in `11_scope_and_omissions.md`.

## What this means operationally before deployment

The `label::Hausa (ha)` and `hint::Hausa (ha)` columns exist and are structurally ready to receive
professional translations — populating them is a spreadsheet edit, not a form redesign. This
should be completed, back-translated, and cognitively pre-tested with a small sample of the actual
enumerator corps (ideally including some of the 38% least confident in English) before the next
fieldwork round, not left for enumerators to work around in the field.

## A real bug this policy caused, found by live field-testing, and fixed

The policy above is "translate short/unambiguous items, mark long/clinical text pending" — but the
first build applied it inconsistently: every `choice()` call defaulted to the pending placeholder,
and only a subset of choice lists were manually given real Hausa. That silently swept in several
choice lists that are unambiguous, everyday vocabulary and should have been translated under the
policy's own rule — household relationships, water sources, toilet types, household assets,
supervisor decisions — and, worst, the 120-row enumerator list at question 1.08, where the
placeholder isn't clinical text at all, it's a code (`ENU003 (TM03, Ilela)`) that needs no
translation in the first place.

This was found by deploying the form to a live KoboToolbox project with all six media CSVs
attached and rendering it in the field's own default language (Hausa): with `default_language: ha`,
question 1.08 — the very first required field after Section 1 opens — showed the same placeholder
string 120 times in a row, one per enumerator, making it impossible for an enumerator to find and
select their own code. A printed export of that rendered form ran to 32 pages, most of it that one
repeated line. This was a real defect in the running form, not a documentation gap, and is fixed
in the current build:

- Every short, unambiguous choice list (`relationship`, `relationship_member`, `visit_result`,
  `measure_status`, `measure_position`, `card_seen`, `photo_status`, `no_specimen_reason`,
  `water_source`, `toilet_type`, `handwash`, `assets`, `supervisor_decision`) now carries real
  Hausa, consistent with the policy stated above.
- The `enumerator` list's Hausa column now repeats the English label (a code/team identifier,
  e.g. `Enumerator 003 (TM03, Ilela)`) rather than a translation placeholder — it was never
  translatable content, and defaulting it to "pending translation" was simply wrong, not
  conservative.
- `medicine_list` keeps a placeholder, but a distinct one (`[JERI BAI ISA BA — ana jira daga
  Ma'aikatar Lafiya]`, "list not supplied — awaiting the Ministry of Health") rather than reusing
  the generic translation-pending text, so a data-pack gap (defect D-05) is never confused with an
  ordinary translation gap again.
- The generic pending placeholder remains only on genuinely long/clinical sentence-level text
  (full question wording for the AMR and anthropometry items) and `constraint_message` text,
  which is what the policy above was actually meant to cover.

`scripts/build_form.py` was regenerated and reconverted after this fix (still converts cleanly —
see `conversion/conversion_log.txt`), and a check confirmed zero remaining choice rows carry the
generic pending marker outside `medicine_list`'s dedicated one.
