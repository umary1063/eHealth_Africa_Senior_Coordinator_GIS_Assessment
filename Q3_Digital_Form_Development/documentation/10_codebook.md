# Codebook: form fields to analysis variables

Q3 requirement 13.

## How this form flattens into tables

The form has **exactly one repeat** (`roster`, Section 3). Sections 4 (child module) and 5
(specimen collection) are **not** separate repeats — they are groups *nested inside* each roster
instance, shown only when that roster row is age-eligible (see `01_defects_report.md`, D-01/D-04,
and `constraint_register.csv` row C023 for why). A standard ODK export (Central's OData/CSV export
or Briefcase) therefore produces exactly **two flattened tables**, not three:

### Table 1 — `hh2026_v1` (main submission table, one row per household visited)

**Primary key:** `meta/instanceID` (ODK's own UUID, generated per submission — the only value
guaranteed globally unique across every device and every day of fieldwork; this is the key to use
for deduplication and for joining to Table 2).

**Natural/business key (for human cross-reference, not database-enforced uniqueness):**
`lga` + `settlement` + `structure_no` + `hh_serial` + `visit_date`. Flag for the analysis team:
this combination is expected to be unique *within a clean round*, but nothing in the form
prevents an enumerator revisiting and re-submitting the same dwelling (e.g. after a "return for
correction" supervisor decision), so treat it as a lookup convenience, not a hard key — use
`meta/instanceID` for anything requiring guaranteed uniqueness.

Key columns:

| Column | Source question | Coding | Notes |
|---|---|---|---|
| `meta/instanceID` | (system) | UUID | Primary key |
| `meta/formVersion`... wait, exported as `KEY`/`formVersion` per exporter | (system) | e.g. `2026060100` | See `07_deployment_and_version_control.md` — always retain |
| `device_id` | (system, added) | free text | Fabrication-detection grouping key, `08_fabrication_detection.md` |
| `lga`, `ward`, `settlement` | 1.02–1.04 | codes from `lgas.csv`/`wards.csv`/`settlements.csv` | Join back to the register on these codes for names/coordinates |
| `structure_no`, `hh_serial` | 1.06–1.07 | integer 1–999 | |
| `enumerator_code`, `team_code_display` | 1.08–1.09 | `ENUnnn` / `TMnn` | `team_code_display` is derived, never typed (D: removed manual entry) |
| `visit_date` | 1.10 | date, 2026-06-01..2026-06-30 | See defect D-07 for the window caveat |
| `gps_dwelling` | 1.11 | geopoint (`lat lon alt acc`) | |
| `prev_round_hh_id` | 1.13 | `BAN-######` or blank | Link to `previous_round_households.csv` |
| `visit_result` | 1.14 | 1 completed / 2 refused / 3 no adult / 4 vacant | Gates everything downstream |
| `consent_given` | 2.02 | 1 yes / 2 no | Gates Section 3 onward |
| `hh_size_stated` | 3.01 | integer | Stated, pre-roster |
| `roster_count_actual` | (derived) | integer | `count(roster)` — compare to `hh_size_stated` |
| `roster_mismatch_flag` | (derived) | 0/1 | See `08_fabrication_detection.md` |
| `start`, `end`, `duration_minutes` | (system/derived) | dateTime / dateTime / minutes | See defect D-06 |
| `water_source`..`hh_assets` | 6.01–6.07 | see choices in `form/HH2026_v1.xlsx` | `hh_assets` is space-delimited multi-select codes in the flattened export |
| `supervisor_decision` | 7.05 | 1 accept / 2 return / 3 void | **Filter `supervisor_decision != 2/3` before any headline analysis** — returned/voided forms should not be pooled with accepted ones without re-review |

### Table 2 — `hh2026_v1-roster` (one row per household member, per household)

**Primary key:** `PARENT_KEY` (= Table 1's `meta/instanceID`) + `line` (or the exporter's own
repeat-row `KEY`, which already encodes both). **Foreign key:** `PARENT_KEY` → Table 1.

Because the child module and specimen section are nested inside this same repeat rather than a
second one, **this single table already carries child- and specimen-level columns on the same
row as the person's basic demographics** — no join is needed to build a child-level analysis
table; filter to `eligible_s4 = 1` and every child-module/specimen column is already attached.

| Column | Source question | Coding | Notes |
|---|---|---|---|
| `line` | 3(1) | integer, auto | `position(..)` |
| `member_name` | 3(2) | text | See data-protection note, `09_data_protection.md` |
| `member_relationship` | 3(3) | 1–6 | |
| `member_sex` | 3(4) | 1 M / 2 F | |
| `member_under5` | (added) | 1/2 | Drives which age field applies — D-02 |
| `age_years` | 3(5) | integer 5–110, blank if under 5 | |
| `age_months` | 3(6) | integer 0–59, blank if 5+ | |
| `eligible_s4` | (derived, replaces "office use" col. 7) | 0/1 | 1 iff under5 and 9≤age_months≤59 |
| — *columns below populated only where `eligible_s4=1`, else blank* — | | | |
| `weight_status`, `c_weight_kg` | 4.05 | status 1/2/3; kg 2.0–30.0 or blank | See `02_sentinel_coding_scheme.md` — never a `99` |
| `height_status`, `c_height_cm`, `measure_position` | 4.06–4.07 | status; cm 45.0–130.0 or blank; 1 recumbent/2 standing | Track `measure_position` explicitly — a mid-round switch is expected, not an error, see D on 4.07 |
| `vacc_card_seen`, `measles_from_card`, `measles_recall`, `measles_status` | 4.08–4.10 | see choices | `measles_status` is the single analysis-ready field; the three raw fields are kept for Q4-style source attribution (card vs. recall) |
| `diarrhoea_14d` | 4.11 | 1/2/8 | |
| `antibiotic_30d`, `antibiotic_code`, `antibiotic_other`, `antibiotic_no_rx`, `antibiotic_photo`, `antibiotic_photo_file` | 4.12–4.16 | see choices | `antibiotic_code` is a **placeholder** list — see D-05, do not treat as final coding until the ministry list replaces it |
| `specimen_obtained` | 5.02 | 1/2 | Section only shown if age≥12 months (5.01 removed, D-04) |
| `specimen_label`, `label_digits` | 5.03 | `BSN######-C` / 6-digit substring | Validated per `04_specimen_label_validation.md` |
| `specimen_cold_box_time`, `specimen_temp_c` | 5.04–5.05 | time; 0.0–12.0°C | |
| `specimen_no_reason`, `specimen_no_reason_other` | 5.06–5.07 | see choices | Only populated if `specimen_obtained=2` |

## What is deliberately *not* in either table

Anything the paper form marks "office use only" (Section 8) was **not** implemented in the
digital form at all — 8.01–8.03 describe a paper-file receipt/entry-clerk workflow that has no
meaning once data arrives in Central already structured and timestamped; see
`11_scope_and_omissions.md`.
