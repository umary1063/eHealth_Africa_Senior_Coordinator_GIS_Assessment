# 📱 Question 3: Converting a Paper Questionnaire into a Digital Form

`Household_Questionnaire_HH2026v1.docx` (a child health and antimicrobial resistance household survey, Bansara State) becomes a real, deployable ODK form here — built against the actual field conditions the question states: 120 staff across 24 teams, 2GB Android tablets offline for up to 9 days, an enumerator corps where most people are more confident in Hausa than English, and a fraud pattern from a past round that the paper form's own fields can't catch.

## 🔧 Tool and version validated

```
Python  3.14.6
pyxform 4.5.0
Java (Eclipse Temurin) 21.0.12+8   — required for pyxform's bundled ODK Validate check

python -m pyxform.xls2xform form/HH2026_v1.xlsx conversion/HH2026_v1.xml
```

**Result: `Conversion complete!`**, no errors, two harmless warnings (both deliberate, explained in [`conversion/conversion_log.txt`](conversion/conversion_log.txt), not oversights). The full log and generated XForm are committed in [`conversion/`](conversion/). Current version: `2026080101` (`form_id: hh2026_v1`) — see [`documentation/07_deployment_and_version_control.md`](documentation/07_deployment_and_version_control.md) for the version history.

## ✅ Live-tested, not just converted

Beyond passing the conversion check, this form has actually run on two real platforms: **KoboToolbox**, and a **self-hosted ODK Central server** built independently (`odk.iddsl.com.ng`, Docker Compose on a cloud VM — recorded in [`documentation/07_deployment_and_version_control.md`](documentation/07_deployment_and_version_control.md)). That live testing caught what static review missed:

- 🌐 A translation bug that rendered a 120-row choice list as an identical placeholder in Hausa
- 🔀 A logic bug that made the supervisor sign-off unreachable in refused/vacant/no-consent cases
- 🔐 And most recently, **ODK Entities was implemented and verified live** for cross-submission duplicate-label detection (Requirement 8) — see [`documentation/05_duplicate_label_detection.md`](documentation/05_duplicate_label_detection.md) for exactly what was proven and what wasn't

All fixes and corrections are documented in [`documentation/11_scope_and_omissions.md`](documentation/11_scope_and_omissions.md) and [`AI_USE.md`](../AI_USE.md).

## 📁 Repository layout

```text
Q3_Digital_Form_Development/
├── README.md                          this file
├── index.html                         landing page linking every artefact
├── Q3_Response.docx                   the direct answer to all 14 numbered requirements
├── Q3_Process_and_Design_Record.docx  the fuller story of how it was built and tested
├── constraint_register.csv            🧾 central deliverable: every rule, what it prevents, its source
├── test_plan.csv                      🧪 43 test cases, incl. boundaries and negative cases
├── form/
│   ├── HH2026_v1.xlsx                 the XLSForm itself
│   └── media/                         external CSVs the form reads (settlements, wards, LGAs,
│                                       staff roster, specimen labels, previous-round households,
│                                       and medicine_list.csv — a deliberately empty stub, see D-05)
├── conversion/
│   ├── HH2026_v1.xml                  pyxform's XForm output
│   └── conversion_log.txt             tool versions, full output, what each warning means
├── scripts/
│   ├── build_form.py                  generates the form AND the constraint register from one
│   │                                   set of field definitions, so they can't drift apart
│   └── checkdigit_reference.py        independent check on the specimen-label maths
├── testing/                           testing aids only — not part of the deliverable
└── documentation/
    ├── 01_defects_report.md           🐛 9 questionnaire defects — fixed or escalated, and why
    ├── 02_sentinel_coding_scheme.md   every "no answer" code checked against every field
    ├── 03_settlement_list_mechanism.md   serving 2,524 settlements to a 2GB device
    ├── 04_specimen_label_validation.md   the check-digit scheme, proved not just demonstrated
    ├── 05_duplicate_label_detection.md   🔐 ODK Entities, implemented and live-verified
    ├── 06_language_and_translation.md    the Hausa/English policy and the bug found live
    ├── 07_deployment_and_version_control.md   version history, the live server, offline devices
    ├── 08_fabrication_detection.md       fields added for QA, driven by a real fraud case
    ├── 09_data_protection.md             what's configured, what's collected that maybe shouldn't be
    ├── 10_codebook.md                    form fields → analysis variables, table structure
    └── 11_scope_and_omissions.md         what was deliberately left out, and why
```

## 🗂️ How the 14 requirements map to this repository

| # | Requirement | Where |
|---|---|---|
| 1 | Build the form; state tool/version; include conversion output | `form/HH2026_v1.xlsx`, `conversion/`, this README |
| 2 | Constraint register | `constraint_register.csv` |
| 3 | Coding scheme / sentinel handling | `documentation/02_sentinel_coding_scheme.md` |
| 4 | Cross-question consistency (household size vs. roster; eligible children vs. child modules) | `constraint_register.csv` rows C022–C023; `documentation/01_defects_report.md` D-01 |
| 5 | Questionnaire defects | `documentation/01_defects_report.md` (9 defects, D-01–D-09) |
| 6 | Settlement list on a 2GB device | `documentation/03_settlement_list_mechanism.md` |
| 7 | Specimen label check digit + transposition test cases | `documentation/04_specimen_label_validation.md`, `scripts/checkdigit_reference.py` |
| 8 | Cross-device/cross-submission duplicate label | `documentation/05_duplicate_label_detection.md` |
| 9 | Test plan, 15+ cases, boundaries and negatives | `test_plan.csv` (43 cases) |
| 10 | Deployment/version control, mid-round change, offline devices | `documentation/07_deployment_and_version_control.md` |
| 11 | Fabrication detection, run daily | `documentation/08_fabrication_detection.md` |
| 12 | Data protection | `documentation/09_data_protection.md` |
| 13 | Codebook | `documentation/10_codebook.md` |
| 14 | Deliberate scope decisions | `documentation/11_scope_and_omissions.md` |

## 💡 The one design decision worth reading first

The paper form's photocopy-and-tally design implies Sections 4 (child module) and 5 (specimen collection) need to be manually counted against the roster. Here, they're built differently: nested inside each roster row, and only shown once that row's own age fields say the person qualifies. One result: the number of completed child modules and the number of eligible children are **always the same number, by design** — not by a rule checking two separately-typed numbers against each other. That single choice also fixes a real contradiction in the paper form (column 7 marked "office use" but actually needed live in the field). See [`documentation/01_defects_report.md`](documentation/01_defects_report.md) and [`documentation/10_codebook.md`](documentation/10_codebook.md) for the knock-on effects.

## 🔗 Matching the digital form back to the paper questionnaire

Every field with a direct paper equivalent keeps that question's own number in its label — `1.02  Local Government Area`, `4.05  Weight measurement status`, `5.03  Specimen label number`. The roster section uses the paper table's own column numbers `(1)`–`(8)`. Fields that only exist digitally (`member_under5`, the automatic timestamps) carry no number at all, since giving them one would imply a paper source that doesn't exist. That's why a bare question number like "4.05" means the same thing everywhere — the paper form, the running app, and the constraint register — with nothing to mentally translate between them.

## ⚠️ A data-pack gap, disclosed up front

The reference data doesn't include a medicine list, even though question 4.13 and the data pack's own README both refer to one. This is reported, not papered over: `antibiotic_code` is wired up exactly like the LGA/Ward/Settlement picker, but its source file ships as an empty stub — a header row, zero data. No medicine name, invented or borrowed from elsewhere, appears anywhere in the form. The question has no answer to give until the ministry supplies the real list. See [`documentation/01_defects_report.md`](documentation/01_defects_report.md), defect D-05.

## 🤖 AI assistance

This submission was built with Claude (Anthropic) as an assistant — drafting the form-generator script, documentation, and test plan from the candidate's own reading of the questionnaire and design decisions. Every structural choice, threshold, and judgement call is attributed to the candidate throughout, not presented as sourced when it wasn't. This includes disclosing mistakes made and corrected along the way — notably a case where the AI twice tried to fill the missing-medicine-list gap with invented content before being told plainly to report the gap instead. Full account in [`../AI_USE.md`](../AI_USE.md).
