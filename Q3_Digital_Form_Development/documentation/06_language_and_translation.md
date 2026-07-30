# Language: Hausa in the field, English for supervisors and analysis

The operating conditions state interviews are conducted in Hausa, 38% of enumerators are not
confident readers of English, and supervisory review and analysis are in English. `settings sheet`
sets `default_language: Hausa (ha)`, and every field carries a `label::Hausa (ha)` column
alongside `label::English (en)`; a supervisor or the office can switch the running language from
the ODK Collect form-language menu without the form needing to be redeployed.

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
