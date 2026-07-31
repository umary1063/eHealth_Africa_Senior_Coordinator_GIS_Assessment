# Testing aids — not part of the submission

Files in this folder exist only to unblock manual functional testing on a live ODK Central
instance. Nothing here is a claim about the form's actual content, and nothing here is used by
`scripts/build_form.py` or referenced by the committed `form/HH2026_v1.xlsx`.

## `medicine_list_DUMMY_FOR_CENTRAL_TESTING_ONLY.csv`

Question 4.13 (`antibiotic_code`) is a `select_one_from_file medicine_list.csv` field whose real
attachment, `form/media/medicine_list.csv`, ships as an empty stub (header row only) because the
ministry's medicine/antimicrobial code list was never supplied in the data pack — see defect D-05
in `../documentation/01_defects_report.md`. With the real, empty stub attached, that one question
has no options and cannot be answered, which is the correct, honest behaviour of the deliverable.

To exercise the rest of the form during a live walkthrough on a self-hosted ODK Central instance
without that one field being a dead end, this folder provides a **dummy** replacement with
obviously fake entries (`[TEST DATA - NOT A REAL MEDICINE]`) — deliberately not real or
plausible-looking drug names, so it cannot be mistaken for a real coded list even out of context.

**How to use it:** on your Central instance's form attachments page, upload this file in place of
the real `medicine_list.csv` for `hh2026_v1`'s attachment slot, purely to test that far into the
form. Do not commit this file over `form/media/medicine_list.csv` in the actual submission repo,
and do not use it, or anything like it, in real fieldwork — the office needs the ministry's actual
list before this question can be answered for real, and this file is not a substitute for that.

Swap the real stub back in (or simply re-attach `form/media/medicine_list.csv`) once you're done
testing that branch, if you want the Central project to match the submitted deliverable exactly.
