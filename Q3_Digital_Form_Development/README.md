# Question 3: Converting a paper questionnaire into a digital form

`Household_Questionnaire_HH2026v1.docx` (integrated child health and antimicrobial resistance
household survey, Bansara State) converted to a deployable ODK XLSForm, against the operating
conditions stated in the question paper: 120 field staff / 24 teams / 4 LGAs / 40 wards, 2 GB
Android tablets with up to 9 consecutive offline days, a majority-Hausa-speaking, low-English-
confidence enumerator corps, and a fieldwork fraud case that the paper form's own fields cannot
detect.

## Tool and version validated

```
Python  3.14.6
pyxform 4.5.0
Java (Eclipse Temurin) 21.0.12+8   -- required for pyxform's bundled ODK Validate check

python -m pyxform.xls2xform form/HH2026_v1.xlsx conversion/HH2026_v1.xml
```

Result: **Conversion complete!**, exit code 0, two non-blocking warnings (both deliberate scope
decisions, not oversights — explained in `conversion/conversion_log.txt`). Full log and the
generated XForm XML are committed in `conversion/`. Current form version: `2026073101`
(`form_id: hh2026_v1`) — see `documentation/07_deployment_and_version_control.md` for the
versioning scheme and the two revisions before it.

## Live-tested, not just converted

Beyond the conversion check above, this form was deployed and exercised on two real platforms:
**KoboToolbox** (with all media attached) and a **self-hosted ODK Central instance**
(`odk.iddsl.com.ng`, Oracle Cloud Always Free tier, Docker Compose behind a Cloudflare Tunnel —
infrastructure the candidate built independently, recorded in
`documentation/07_deployment_and_version_control.md`). That live testing caught two real defects
that static review had missed — a translation-policy bug that rendered a 120-row choice list as
an identical placeholder string in Hausa, and a relevance bug that made the enumerator's Section 7
sign-off unreachable in refused/vacant/no-consent outcomes, contradicting the paper form's own
instruction — both fixed and documented in `documentation/11_scope_and_omissions.md`, item 9, and
`AI_USE.md`.

## Repository layout

```
Q3_Digital_Form_Development/
├── README.md                        this file
├── index.html                       landing page summarising the deliverable, links to every artefact
├── Q3_Process_and_Design_Record.docx   narrative process record (methodology, not a duplicate of documentation/)
├── constraint_register.csv          central deliverable: every constraint added, what it prevents, its source
├── test_plan.csv                    43 test cases with expected results, incl. boundaries and negatives
├── form/
│   ├── HH2026_v1.xlsx                the XLSForm
│   └── media/                        external CSVs consumed by the form (settlements, wards, lgas,
│                                      staff roster, specimen label allocation, previous-round
│                                      households, and medicine_list.csv -- a deliberately empty
│                                      stub, see defect D-05)
├── conversion/
│   ├── HH2026_v1.xml                 pyxform's XForm output
│   └── conversion_log.txt            tool versions, command, full output, interpretation
├── scripts/
│   ├── build_form.py                 generates form/HH2026_v1.xlsx AND constraint_register.csv from
│   │                                  one set of field definitions, so the two cannot drift apart
│   └── checkdigit_reference.py       plain-Python mirror of the specimen-label check digit XPath,
│                                      used to independently generate/verify test vectors
├── testing/                         live-testing aids only -- not part of the deliverable, see testing/README.md
│   └── medicine_list_DUMMY_FOR_CENTRAL_TESTING_ONLY.csv   obviously-fake data to unblock manual
│                                      click-through testing of question 4.13 on a live server
└── documentation/
    ├── 01_defects_report.md          9 questionnaire defects found; resolved-in-form vs escalated, and why
    ├── 02_sentinel_coding_scheme.md  every sentinel/measurement collision checked; the one real fix
    ├── 03_settlement_list_mechanism.md   serving 2,524 settlements to a 2GB device; alternatives rejected
    ├── 04_specimen_label_validation.md   check-digit scheme, worked test vectors, transposition proof
    ├── 05_duplicate_label_detection.md   what a self-contained form can/cannot enforce, and the real architecture
    ├── 06_language_and_translation.md    Hausa/English policy, the translation bug found live, and why full
    │                                     translation was not attempted
    ├── 07_deployment_and_version_control.md   mid-round changes, 9-day offline devices, version tracking,
    │                                     the self-hosted ODK Central deployment record
    ├── 08_fabrication_detection.md       fields added for QA + the daily check, driven by the fraud case
    ├── 09_data_protection.md             what was configured, what's collected unnecessarily, what I'd cut
    ├── 10_codebook.md                    form fields -> analysis variables, table structure, primary keys
    └── 11_scope_and_omissions.md         what was not implemented, why, and every bug found via live testing
```

## How the 14 required items map to this repository

| # | Requirement | Where |
|---|---|---|
| 1 | Build the form; state tool/version; include conversion output | `form/HH2026_v1.xlsx`, `conversion/`, this README |
| 2 | Constraint register | `constraint_register.csv` |
| 3 | Coding scheme / sentinel handling | `documentation/02_sentinel_coding_scheme.md` |
| 4 | Cross-question consistency (household size vs. roster; eligible children vs. child modules) | `constraint_register.csv` rows C022–C023; `documentation/01_defects_report.md` D-01 |
| 5 | Questionnaire defects | `documentation/01_defects_report.md` (9 defects, D-01..D-09) |
| 6 | Settlement list on a 2GB device | `documentation/03_settlement_list_mechanism.md` |
| 7 | Specimen label check digit + transposition test cases | `documentation/04_specimen_label_validation.md`, `scripts/checkdigit_reference.py` |
| 8 | Cross-device/cross-submission duplicate label | `documentation/05_duplicate_label_detection.md` |
| 9 | Test plan, 15+ cases, boundaries and negatives | `test_plan.csv` (43 cases) |
| 10 | Deployment/version control, mid-round change, offline devices | `documentation/07_deployment_and_version_control.md` |
| 11 | Fabrication detection, daily | `documentation/08_fabrication_detection.md` |
| 12 | Data protection | `documentation/09_data_protection.md` |
| 13 | Codebook | `documentation/10_codebook.md` |
| 14 | Deliberate scope decisions | `documentation/11_scope_and_omissions.md` |

## The single structural decision worth reading first

Sections 4 (child module) and 5 (specimen collection) are not a second repeat group manually
counted against the roster, as the paper form's photocopy-and-tally design implies. They are
nested inside each `roster` row and shown only when that row's own age fields say the person is
age-eligible. One consequence: the number of completed child modules and the number of eligible
children are the same value **by construction**, not by a validation rule checking two separately
-entered numbers against each other (which is what the paper form's own contradiction — column
(7) marked "office use" yet needed live in the field for question 3.02 — was going to keep
producing). This single choice is what resolves defects D-01 and D-04, half of requirement 4, and
most of the specimen-section logic in one move; see `documentation/01_defects_report.md` and
`documentation/10_codebook.md` for the consequences for export table structure.

## Cross-referencing the digital form back to the paper questionnaire

Every field that has a direct paper equivalent carries that question's own number as a literal
prefix in its label -- `1.02  Local Government Area`, `4.05  Weight measurement status`, `5.03
Specimen label number`. The Section 3 roster columns use the paper table's own `(1)`-`(8)`
notation instead, since the paper form numbers them as table columns, not standalone questions.
Fields that exist only in the digital form (no paper equivalent -- `member_under5`, the automatic
`start`/`end` timestamps, `team_code_display`) carry no number, since inventing one would imply a
paper source that doesn't exist. This is why `constraint_register.csv` and every document in
`documentation/` can cite a bare question number ("4.05", "5.03") and have it mean the same thing
in the paper questionnaire, the running form, and the constraint register -- one addressing
scheme, not three that have to be mentally cross-walked.

## Data-pack gap disclosed up front

`reference_media/` does not include a medicine list, although question 4.13 and the pack's own
`README.md` both refer to one. This is reported, not filled in with a substitute: `antibiotic_code`
is wired exactly like the LGA/Ward/Settlement cascade (`select_one_from_file`), but
`form/media/medicine_list.csv` ships as a stub — a header row, zero data rows. No antibiotic name,
invented or sourced from a public document, appears anywhere in the running form; the question
has no answer to offer until the ministry supplies the real coded list. See
`documentation/01_defects_report.md`, defect D-05.

## AI assistance

This submission was produced with Claude (Anthropic) as an assistant: drafting the XLSForm
generator script, the documentation, and the test plan, from my reading of the questionnaire and
reference data and my own design decisions (structural choices, thresholds, and every judgement
call are attributed as mine throughout the documentation, not presented as sourced when they are
not). This includes disclosure of corrections made during review and live testing — notably an
instance where the AI twice attempted to fill the missing-medicine-list gap (D-05) with substitute
content before being explicitly redirected to report the gap instead of filling it. See the full
account in `../AI_USE.md`.
