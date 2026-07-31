#!/usr/bin/env python3
"""
Builds the HH2026v1 XLSForm from a single field-definition list.

Why a generator script rather than a hand-edited spreadsheet: the constraint
register (Q3 requirement 2) must match what the form actually enforces. Every
row below carries its own justification metadata, and constraint_register.csv
is exported from the same rows that produce the XLSForm survey sheet, so the
two artefacts cannot drift apart.

Run: python scripts/build_form.py
Output: form/HH2026_v1.xlsx, constraint_register.csv
"""
import csv
import os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FORM_PATH = os.path.join(ROOT, "form", "HH2026_v1.xlsx")
REGISTER_PATH = os.path.join(ROOT, "constraint_register.csv")

# ---------------------------------------------------------------------------
# Hausa translation policy (documented in full in
# documentation/06_language_and_translation.md): short, high-frequency,
# unambiguous items are translated. Full clinical sentence text is marked
# PENDING rather than guessed, because a wrong clinical translation is worse
# than an English fallback for a 38%-low-confidence-English enumerator corps.
# ---------------------------------------------------------------------------
PENDING = "[HAUSA: sai an fassara ta kwararre — professional translation pending]"

# name, label_en, label_ha
YES_NO = None

rows = []          # survey sheet rows (list of dicts)
register = []      # constraint register rows (list of dicts)
reg_id = 0


def add(row):
    rows.append(row)


def constraint_entry(field, question_no, rule_type, rule, prevents, source):
    global reg_id
    reg_id += 1
    register.append({
        "id": f"C{reg_id:03d}",
        "field_name": field,
        "questionnaire_no": question_no,
        "rule_type": rule_type,
        "rule_added": rule,
        "prevents": prevents,
        "source_or_judgement": source,
    })


def begin_group(name, label_en, label_ha=PENDING, appearance=None, relevant=None):
    r = {"type": "begin group", "name": name, "label::English (en)": label_en,
         "label::Hausa (ha)": label_ha}
    if appearance:
        r["appearance"] = appearance
    if relevant:
        r["relevant"] = relevant
    add(r)


def end_group():
    add({"type": "end group"})


def begin_repeat(name, label_en, label_ha=PENDING):
    add({"type": "begin repeat", "name": name, "label::English (en)": label_en,
         "label::Hausa (ha)": label_ha})


def end_repeat():
    add({"type": "end repeat"})


def note(name, label_en, label_ha=PENDING, relevant=None):
    r = {"type": "note", "name": name, "label::English (en)": label_en,
         "label::Hausa (ha)": label_ha}
    if relevant:
        r["relevant"] = relevant
    add(r)


def calc(name, calculation):
    add({"type": "calculate", "name": name, "calculation": calculation})


def q(type_, name, label_en, label_ha=PENDING, hint_en="", hint_ha="",
      required=False, relevant=None, constraint=None, constraint_message=None,
      appearance=None, default=None, read_only=False, choice_filter=None,
      calculation=None):
    r = {
        "type": type_, "name": name,
        "label::English (en)": label_en, "label::Hausa (ha)": label_ha,
    }
    if hint_en:
        r["hint::English (en)"] = hint_en
    if hint_ha:
        r["hint::Hausa (ha)"] = hint_ha
    if required:
        r["required"] = "yes"
    if relevant:
        r["relevant"] = relevant
    if constraint:
        r["constraint"] = constraint
    if constraint_message:
        r["constraint_message::English (en)"] = constraint_message
    if appearance:
        r["appearance"] = appearance
    if default is not None:
        r["default"] = default
    if read_only:
        r["read_only"] = "yes"
    if choice_filter:
        r["choice_filter"] = choice_filter
    if calculation:
        r["calculation"] = calculation
    add(r)


choices = []  # (list_name, name, label_en, label_ha, extra_cols dict)


def choice(list_name, name, label_en, label_ha=PENDING, **extra):
    row = {"list_name": list_name, "name": name, "label::English (en)": label_en,
           "label::Hausa (ha)": label_ha}
    row.update(extra)
    choices.append(row)


# ===========================================================================
# SETTINGS
# ===========================================================================
settings = {
    "form_title": "Integrated Child Health and AMR Household Survey 2026",
    "form_id": "hh2026_v1",
    "version": "2026060100",
    "default_language": "Hausa (ha)",
    "instance_name": "concat(${lga_name_txt}, '-', ${settlement_code}, '-', ${structure_no}, '-', ${hh_serial})",
}

# ===========================================================================
# FRONT MATTER / METADATA
# Standard ODK begin/end timestamps: added because the paper form has NO
# interview start time at all -- only 7.01 "time interview ended". Without a
# start time, interview duration (the exact signal that caught the 94x
# 4-minute-interview enumerator in the last round, but only after fieldwork
# closed) cannot be computed from the paper's own fields. See defects report,
# defect D-06, and fabrication-detection doc.
# ===========================================================================
add({"type": "start", "name": "start"})
add({"type": "end", "name": "end"})
add({"type": "deviceid", "name": "device_id"})
add({"type": "today", "name": "today_date"})

constraint_entry("start/end (system)", "n/a (added)", "added field",
                  "ODK start/end metadata timestamps captured automatically at open/finalize",
                  "Interview duration cannot be computed from the paper form at all -- it has "
                  "no start-time field, only 7.01 end time. This is the exact signal that "
                  "identified the 94-interview, 4-minute-mean fraud case, but only after "
                  "fieldwork closed.",
                  "My judgement, directly driven by the operating-conditions fraud case")
constraint_entry("device_id (system)", "n/a (added)", "added field",
                  "ODK deviceid metadata captured automatically",
                  "Cannot attribute submissions to a specific tablet for the per-device "
                  "duplicate-label check (requirement 8) or for device-level QA dashboards",
                  "My judgement")

# ===========================================================================
# SECTION 1: HOUSEHOLD IDENTIFICATION
# ===========================================================================
begin_group("s1", "Section 1: Household identification", "Kashi na 1: Bayanan gida")

q("select_one state", "state", "State", "Jiha", default="1")
choice("state", "1", "Bansara", "Bansara")

q("select_one_from_file lgas.csv", "lga", "Local Government Area", "Kananan Hukuma",
  hint_en="Select from the administrative list. Do not type the name.",
  required=True)

calc("lga_name_txt", "${lga}")

q("select_one_from_file wards.csv", "ward", "Ward", "Yankin gunduma",
  required=True, choice_filter="lga_code=${lga}")

q("select_one_from_file settlements.csv", "settlement", "Settlement", "Gari/kauye",
  hint_en="Type a few letters to search. List has 2,524 entries -- do not scroll.",
  required=True, choice_filter="ward_code=${ward}")

calc("settlement_code", "${settlement}")

q("select_one yes_no", "settlement_local_name_known", "Is the settlement known locally by a "
  "different name?", "Shin mutanen yankin na kiran wannan wuri da wani suna daban?",
  required=True)
q("text", "settlement_local_name", "If yes, write the name used locally.",
  "Idan ee, rubuta sunan da ake amfani da shi a wurin.",
  relevant="${settlement_local_name_known}='1'")

q("integer", "structure_no", "Structure number painted on the dwelling",
  "Lambar da aka rubuta a gidan",
  required=True, constraint=". >= 1 and . <= 999",
  constraint_message="Enter 1-999 (three digit box on the paper form).")
constraint_entry("structure_no", "1.06", "range", "1-999",
                  "Non-numeric or >3-digit entry that cannot fit the printed 3-digit box",
                  "Paper form coding box is three digits wide (⌷⌷⌷); my judgement on the "
                  "implied range")

q("integer", "hh_serial", "Household serial number within the settlement",
  "Lambar gida a cikin yankin",
  required=True, constraint=". >= 1 and . <= 999",
  constraint_message="Enter 1-999 (three digit box on the paper form).")
constraint_entry("hh_serial", "1.07", "range", "1-999",
                  "Non-numeric or >3-digit entry", "Paper form coding box is three digits wide")

q("select_one enumerator", "enumerator_code", "Enumerator code", "Lambar ma'aikaci",
  required=True, hint_en="Select your code from the staff list.")
calc("team_code_auto", "pulldata('staff_roster','team_code','name',${enumerator_code})")
q("text", "team_code_display", "Team code (auto-filled)", "Lambar kungiya (kai tsaye)",
  read_only=True, calculation="${team_code_auto}")
constraint_entry("team_code_display", "1.08 / 1.09", "removed manual entry, auto-filled",
                  "team_code_display = pulldata('staff_roster', 'team_code', 'name', "
                  "enumerator_code), shown read-only; the enumerator never types a team code",
                  "Paper 1.09 lets an enumerator enter their own code correctly at 1.08 but a "
                  "mistyped or wrong team code at 1.09, which would then misassign the "
                  "specimen-label range check in Section 5 to the wrong team's block",
                  "Derived from staff_roster.csv (120 rows, 24 teams, verified 1:1 with "
                  "specimen_label_allocation.csv team codes)")

q("date", "visit_date", "Date of visit", "Ranar ziyara", required=True,
  constraint=". >= date('2026-06-01') and . <= date('2026-06-30')",
  constraint_message="Date must fall within the fieldwork period printed on the form "
                      "(1-30 June 2026).")
constraint_entry("visit_date", "1.10", "range",
                  "2026-06-01 to 2026-06-30 (closed interval)",
                  "Backdated/postdated entries; device clock errors; typed year defaulting "
                  "to device-current-year instead of 2026",
                  "Printed on the questionnaire header ('Fieldwork period 1 to 30 June 2026'). "
                  "NOTE: this conflicts with the operating-conditions brief, which states "
                  "fieldwork runs 14 days -- flagged as defect D-07, escalated, not resolved "
                  "silently. I used the form's own printed period because it is the "
                  "ethics-approved text.")

q("geopoint", "gps_dwelling", "GPS reading at the entrance to the dwelling",
  "Wurin GPS a kofar gida", required=True,
  constraint="number(substring-before(.,' ')) >= 10.0 and "
             "number(substring-before(.,' ')) <= 11.9 and "
             "number(substring-before(substring-after(.,' '),' ')) >= 6.3 and "
             "number(substring-before(substring-after(.,' '),' ')) <= 9.0",
  constraint_message="Point falls outside the Bansara state working area. Re-take the reading.")
constraint_entry("gps_dwelling", "1.11", "range",
                  "longitude 6.3-9.0, latitude 10.0-11.9 (geopoint bounding box)",
                  "Wrong-hemisphere entry, transposed lat/long, GPS fix taken indoors far "
                  "from the dwelling, stale cached fix from a previous survey",
                  "My judgement -- padded from the settlement register's actual coordinate "
                  "extent (longitude 6.9544 to 8.4288, latitude 10.3659 to 11.5735 across the "
                  "2,524 settlements in settlements.csv) with roughly a 0.4-0.5 degree margin "
                  "for genuine edge-of-catchment points")

q("select_one yes_no_dk", "prev_round_visited", "Was this household visited during the "
  "October 2025 round?", "An ziyarci wannan gida a lokacin 2025 ba?", required=True)
q("text", "prev_round_hh_id", "Household identifier allocated in the October 2025 round",
  "Lambar da aka bawa gida a 2025",
  relevant="${prev_round_visited}='1'", required=True,
  constraint="regex(., '^BAN-[0-9]{6}$') and "
             "pulldata('previous_round_households','household_id','household_id',.) != ''",
  constraint_message="Format must be BAN-000000 and must match an identifier in the previous "
                      "round register.")
constraint_entry("prev_round_hh_id", "1.13", "format + existence",
                  "regex ^BAN-[0-9]{6}$, and must resolve via pulldata() against "
                  "previous_round_households.csv (3,982 rows, format verified 100% compliant)",
                  "A transcription error that silently creates a phantom link between this "
                  "round and a household that was never actually visited last round, which "
                  "would corrupt any longitudinal linkage analysis",
                  "previous_round_households.csv, all 3,982 household_id values checked; "
                  "format is uniform")

calc("prev_round_children_u5", "if(${prev_round_visited}='1', "
     "pulldata('previous_round_households','children_under5_last_round','household_id',"
     "${prev_round_hh_id}), '')")
note("prev_round_children_u5_note",
     "Previous round recorded ${prev_round_children_u5} child(ren) under five in this "
     "household. Confirm this is still plausible once the roster is complete.",
     "An gaba an rubuta yara ${prev_round_children_u5} 'yan kasa da shekara biyar a wannan "
     "gida. Tabbatar hakan bayan kammala jerin gida.",
     relevant="${prev_round_visited}='1' and ${prev_round_children_u5}!=''")

q("select_one visit_result", "visit_result", "Result of visit", "Sakamakon ziyara",
  required=True)

end_group()

note("end_note_no_further", "Result of visit means no further section is completed. Sign at "
     "7.03 and submit.", "Sakamakon ziyara na nufin ba za a ci gaba da wani kashi ba. Sa hannu "
     "a 7.03 sannan a mika.",
     relevant="${visit_result}='2' or ${visit_result}='3' or ${visit_result}='4'")

# ===========================================================================
# SECTION 2: CONSENT
# ===========================================================================
begin_group("s2", "Section 2: Consent", "Kashi na 2: Yardar shiga",
            relevant="${visit_result}='1'")

q("select_one yes_no", "consent_read", "Consent statement read aloud to the respondent in "
  "full?", "An karanta bayanin yardar shiga gaba daya ga wanda ake tambaya?", required=True)
q("select_one consent", "consent_given", "Does the respondent consent to the household "
  "interview?", "Wanda ake tambaya ya yarda a yi hira da gidan?", required=True)
q("select_one relationship", "respondent_relationship", "Relationship of the respondent to "
  "the head of household", "Dangantakar wanda ake tambaya da shugaban gida",
  relevant="${consent_given}='1'", required=True)

end_group()

note("consent_refused_note", "Consent was refused. Do not continue. Sign at 7.03 and submit.",
     "An ki amincewa. Kar a ci gaba. Sa hannu a 7.03 sannan a mika.",
     relevant="${visit_result}='1' and ${consent_given}='2'")

# ===========================================================================
# SECTION 3 + 4 + 5: ROSTER, with the child module and specimen section
# NESTED inside each roster member (relevant only when that member is
# age-eligible), instead of a second, separately-counted repeat.
#
# This single structural decision is what resolves requirement 4's second
# cross-check (number of eligible children vs number of child modules
# completed) BY CONSTRUCTION rather than by a post-hoc validation rule: there
# is exactly one child-module block per roster row, shown if and only if that
# row's own age fields say the child is 9-59 months. It is also what resolves
# defect D-01 (the "office use" column 7 / question 3.02 contradiction) and
# defect D-04 (redundant 5.01, restating information already on the roster).
# ===========================================================================
form_active = "${visit_result}='1' and ${consent_given}='1'"

begin_group("s3", "Section 3: Household roster", "Kashi na 3: Jerin gida", relevant=form_active)

q("integer", "hh_size_stated", "How many people usually live in this household?",
  "Mutane nawa suke zaune a wannan gida?", required=True,
  constraint=". >= 1 and . <= 30",
  constraint_message="Enter 1-30. If genuinely larger, flag for supervisor at 7.02.")
constraint_entry("hh_size_stated", "3.01", "range", "1-30",
                  "Zero or absurd entries (e.g. 300 from a stuck key); still permits genuinely "
                  "large compound households up to 30",
                  "My judgement -- no household-size distribution was supplied in the data "
                  "pack for Bansara state, so I set a generous ceiling rather than infer one")

note("roster_instruction", "List every usual resident, beginning with the head of household. "
     "For a resident under five, record age in completed MONTHS. For everyone else, record "
     "age in completed YEARS.",
     "Ka lissafa duk wanda ke zaune a gida, farawa da shugaban gida. Ga wanda ke kasa da "
     "shekara biyar, rubuta shekarunsa da watanni. Ga sauran, rubuta da shekaru.")

begin_repeat("roster", "Household member", "Dan gidan")

q("integer", "line", "Line number", "Lamba", read_only=True,
  calculation="position(..)")

q("text", "member_name", "Name or initials", "Suna ko gajerun haruffa", required=True)

q("select_one relationship_member", "member_relationship", "Relationship to head",
  "Dangantaka da shugaban gida", required=True)

q("select_one sex", "member_sex", "Sex", "Jinsi", required=True)

q("select_one yes_no", "member_under5", "Is this person under five years old?",
  "Wannan mutum yana kasa da shekara biyar?", required=True,
  hint_en="Not on the paper form -- added so the digital form routes to the correct age "
          "field. See defects report D-02.",
  hint_ha=PENDING)
constraint_entry("member_under5", "n/a (added, drives 3(5)/3(6) routing)", "added field",
                  "select_one yes/no gates which of age_years / age_months is asked",
                  "The paper form leaves it to the enumerator's judgement which of columns "
                  "(5)/(6) to fill for a borderline-looking child, which a printed form can "
                  "get away with but a digital form's relevant logic cannot -- it needs an "
                  "explicit branch",
                  "My judgement")

q("integer", "age_years", "Age in completed years", "Shekaru cikakku",
  relevant="${member_under5}='2'", required=True,
  constraint=". >= 5 and . <= 110",
  constraint_message="Enter 5-110 years.")
constraint_entry("age_years", "3(5)", "range", "5-110",
                  "A member coded 'not under five' with an age below 5, or an implausible age "
                  "from a stuck key (e.g. 999)",
                  "Lower bound follows directly from the routing question; upper bound is my "
                  "judgement (no Bansara demographic data supplied)")

q("integer", "age_months", "Age in completed months (under five only)",
  "Watanni cikakku (kasa da shekara biyar kadai)",
  relevant="${member_under5}='1'", required=True,
  constraint=". >= 0 and . <= 59",
  constraint_message="Enter 0-59 completed months.")
constraint_entry("age_months", "3(6)", "range", "0-59",
                  "A member coded 'under five' with a months value that is actually five years "
                  "or older, which would silently misroute Section 4/5 eligibility",
                  "Definitional: 'under five years' cannot exceed 59 completed months")

calc("eligible_s4", "if(${member_under5}='1' and ${age_months} >= 9 and ${age_months} <= 59, "
     "1, 0)")
note("eligible_s4_note", "This is computed automatically from the age just recorded -- it "
     "replaces the paper form's column (7), which was marked 'office use' yet was required "
     "live in the field to route question 3.02 (see defects report D-01).",
     PENDING, relevant="${eligible_s4}=1")

# ---- Section 4 + 5, nested, gated on eligible_s4 ----
begin_group("child_module", "Section 4: Child module", "Kashi na 4: Bayanan yaro",
            relevant="${eligible_s4}=1")

q("text", "c_name", "Name or initials of the child (copied from roster)",
  "Sunan yaro (an dauko daga jeri)", read_only=True, calculation="${member_name}")
q("integer", "c_age_months", "Age of the child in completed months (copied from roster)",
  "Shekarun yaro da watanni (an dauko daga jeri)", read_only=True,
  calculation="${age_months}")
q("select_one sex", "c_sex", "Sex of the child (copied from roster)",
  "Jinsin yaro (an dauko daga jeri)", read_only=True, calculation="${member_sex}")

# --- Anthropometry: sentinel/measurement collision fix (defect D-03) ---
# The paper form puts a "not measured = 99" sentinel inside a continuous
# numeric field (4.05, 4.06). 99 kg and 99.9 cm are not plausible measurements
# for a 9-59 month child, so on paper the collision is harmless to a human
# reader -- but a digital numeric field has no such common sense, and 99 is a
# perfectly typeable, in-range-looking decimal. Split each into a status
# select_one (measured / not measured, with reason) plus a numeric field that
# is only relevant, and only required, when status = measured. The analysis
# team can then never receive a 99 in a column of real weights.
q("select_one measure_status", "weight_status", "Weight measurement status",
  "Halin auna nauyi", required=True)
q("decimal", "c_weight_kg", "Weight of the child (kg)", "Nauyin yaro (kg)",
  relevant="${weight_status}='1'", required=True,
  constraint=". >= 2.0 and . <= 30.0",
  constraint_message="Enter 2.0-30.0 kg.")
constraint_entry("c_weight_kg", "4.05", "sentinel split + range",
                  "Split into weight_status (measured/not measured/refused) + c_weight_kg "
                  "numeric 2.0-30.0, numeric field only relevant if status=measured",
                  "The paper form's '99 = not measured' sentinel living inside a continuous "
                  "kg field, which is analytically indistinguishable from a genuine (if "
                  "unlikely) 99.0kg entry once digitised as a plain decimal field",
                  "Range is my judgement, generously padded around WHO Child Growth Standards "
                  "weight-for-age for 9-59 months to avoid rejecting true severe-malnutrition "
                  "or high-BMI outliers while catching entry blunders (e.g. a misplaced "
                  "decimal point)")

q("select_one measure_status", "height_status", "Length/height measurement status",
  "Halin auna tsawo", required=True)
q("select_one measure_position", "measure_position", "Position in which the child was "
  "measured", "Yanayin da aka auna yaro",
  relevant="${height_status}='1'", required=True)
constraint_entry("measure_position", "4.07", "consistency (documented, not blocked)",
                  "Recorded alongside height so the office can apply the standard 0.7cm "
                  "recumbent/standing correction; a mid-survey change in which position is "
                  "used for a given age band is expected (operating conditions say a "
                  "measurement-position change is likely mid-round) and must not be blocked",
                  "A position switch is a real, expected event this round -- flagging it (via "
                  "the codebook, not a form constraint) is correct; refusing it in-form is not",
                  "Operating conditions: 'A change to the instrument part way through the "
                  "round is likely'")
q("decimal", "c_height_cm", "Length or height of the child (cm)", "Tsawon yaro (cm)",
  relevant="${height_status}='1'", required=True,
  constraint=". >= 45.0 and . <= 130.0",
  constraint_message="Enter 45.0-130.0 cm.")
constraint_entry("c_height_cm", "4.06", "sentinel split + range",
                  "Split into height_status + c_height_cm numeric 45.0-130.0, only relevant "
                  "if status=measured",
                  "Same collision as weight: paper's '99 = not measured' inside a 3-digit "
                  "continuous cm field",
                  "Range is my judgement, padded around WHO length/height-for-age for 9-59 "
                  "months")

q("select_one card_seen", "vacc_card_seen", "May I see the child's vaccination card or "
  "health record?", "Zan iya ganin katin allurar yaro ko bayanin lafiyarsa?", required=True)
q("select_one yes_no", "measles_from_card", "Copy from the card: is a measles dose recorded?",
  "Daga kati: an rubuta an yi wa yaro allurar kyanda?",
  relevant="${vacc_card_seen}='1'", required=True)
q("select_one yes_no_dk", "measles_recall", "Has this child ever received a measles "
  "vaccination?", "Yaro ya taba samun allurar kyanda?",
  relevant="${vacc_card_seen}='2'", required=True)
calc("measles_status", "if(${vacc_card_seen}='1', ${measles_from_card}, ${measles_recall})")
constraint_entry("measles_status", "4.08-4.10", "sentinel/source separation",
                  "measles_status combines card-confirmed and recall answers into one "
                  "analysis field, but the raw vacc_card_seen/measles_from_card/"
                  "measles_recall fields are kept, not overwritten",
                  "Analysts silently losing the card-confirmed-vs-recall distinction, which "
                  "Q4 of this same assessment explicitly requires reporting on for coverage",
                  "My judgement, informed by the Q4 requirement to report coverage 'by "
                  "documented source, distinguishing card confirmed from caregiver recall'")

q("select_one yes_no_dk", "diarrhoea_14d", "Has this child had diarrhoea in the past 14 "
  "days?", "Yaro ya sha gudawa cikin kwanaki 14 da suka wuce?", required=True)

q("select_one yes_no_dk", "antibiotic_30d", "Has this child taken any antibiotic medicine in "
  "the past 30 days?", "Yaro ya sha maganin rigakafin kwayoyin cuta cikin kwanaki 30 da suka "
  "wuce?", required=True)

q("select_one medicine_list", "antibiotic_code", "Which antibiotic was taken?",
  "Wanne maganin rigakafi ne aka sha?",
  relevant="${antibiotic_30d}='1'", required=True,
  hint_en="PLACEHOLDER LIST -- the data pack did not include the ministry medicine list "
          "referenced by the paper form. See defects report D-05.")
constraint_entry("antibiotic_code", "4.13", "data-pack gap, placeholder + escalation",
                  "select_one backed by an internal XLSForm choices list (medicine_list, 14 "
                  "rows), an illustrative WHO-AWaRe-informed list of 13 common oral/injectable "
                  "antibiotics + Other(96), every label prefixed [PLACEHOLDER]",
                  "A blocked or fabricated-looking field where the real ministry-approved "
                  "antimicrobial code list should be",
                  "ESCALATED, not resolved: the questionnaire refers to 'the medicine list' "
                  "but reference_media/ contains no such file. This is a data-pack gap, not "
                  "something I can responsibly invent an authoritative version of. The "
                  "placeholder must be replaced by the ministry/AMR technical working group's "
                  "actual formulary code list before deployment.")

q("text", "antibiotic_other", "If Other, write the name of the medicine as reported",
  "Idan Wani, rubuta sunan maganin", relevant="${antibiotic_code}='96'", required=True)

q("select_one yes_no_dk", "antibiotic_no_rx", "Was the medicine obtained without a "
  "prescription from a health worker?", "An sami maganin ba tare da takardar likita ba?",
  relevant="${antibiotic_30d}='1'", required=True)

q("select_one photo_status", "antibiotic_photo", "Was a photograph of the medicine "
  "packaging taken?", "An dauki hoton fakitin magani?",
  relevant="${antibiotic_30d}='1'", required=True)
q("image", "antibiotic_photo_file", "Photograph of medicine packaging",
  "Hoton fakitin magani", relevant="${antibiotic_photo}='1'")
constraint_entry("antibiotic_photo_file", "4.16", "added evidence field",
                  "image capture attached whenever antibiotic_photo=1 (photo taken)",
                  "The paper form records only whether a photo was taken, not the photo "
                  "itself, so the office has no way to verify the antibiotic_code entry "
                  "against the packaging -- an AMR-survey-specific back-office QA gap",
                  "My judgement")

end_group()  # child_module

# ---- Section 5, nested, gated on eligible_s4 AND age >= 12 months ----
# 5.01 ('Is the child aged 12 completed months or older?') is fully
# redundant with age_months, already captured two questions earlier on the
# very same page. Re-asking it invites a value that contradicts age_months --
# a second, avoidable sentinel-style collision. Computed instead (defect D-04).
begin_group("specimen", "Section 5: Specimen collection", "Kashi na 5: Tattara samfurin",
            relevant="${eligible_s4}=1 and ${age_months} >= 12")

q("select_one yes_no", "specimen_obtained", "Was a stool specimen obtained from this child?",
  "An samu samfurin kashin yaro?", required=True)
constraint_entry("specimen section relevance", "5.01", "computed relevance, question removed",
                  "Section only shown when age_months>=12 (already on file); no separate "
                  "5.01 question is asked",
                  "5.01 restates a fact already captured at 4.03/age_months two questions "
                  "earlier; asking it again lets an enumerator answer 'yes, >=12 months' for "
                  "a child whose age_months says 10, an internal contradiction the paper "
                  "form has no mechanism to prevent",
                  "My judgement -- resolved in form, disclosed in defects report D-04, not "
                  "silently dropped")

# ---- 5.02 has NO skip instruction on the paper form at all: neither branch
# (specimen obtained / not obtained) says what to do next. Resolved in form
# using the only reading that is internally consistent with 5.03-5.07's own
# content (you cannot affix a label to a specimen you do not have, and you
# cannot give a reason none was obtained for one you did obtain). Flagged for
# ministry confirmation regardless -- see defects report D-08.
# NOTE: calculated helper fields below are intentionally listed before the
# specimen_label question that consumes them. specimen_label needs its own
# derived digits/checksum computed from ITS OWN prior value on re-entry
# (constraint re-evaluation), and team-range lookups only depend on
# team_code_auto (already defined at Section 1), not on specimen_label --
# ordering the pulldata/range calcs first keeps the dependency graph acyclic
# and easy to read.
calc("label_range_start", "pulldata('specimen_label_allocation','range_start','team_code',"
     "${team_code_auto})")
calc("label_range_end", "pulldata('specimen_label_allocation','range_end','team_code',"
     "${team_code_auto})")
calc("label_digits", "substr(${specimen_label},3,6)")
calc("label_checksum", "number(substr(${label_digits},0,1))*7 + "
     "number(substr(${label_digits},1,1))*6 + number(substr(${label_digits},2,1))*5 + "
     "number(substr(${label_digits},3,1))*4 + number(substr(${label_digits},4,1))*3 + "
     "number(substr(${label_digits},5,1))*2")
calc("label_check_expected", "if((${label_checksum} mod 11)=10, 'X', "
     "string(${label_checksum} mod 11))")

q("text", "specimen_label", "Specimen label number (affix label, then transcribe in full)",
  "Lambar samfurin (a manne sannan a rubuta gaba daya)",
  relevant="${specimen_obtained}='1'", required=True,
  appearance="numbers",
  constraint="regex(., '^BSN[0-9]{6}-[0-9X]$') and "
             "number(substr(.,3,6)) >= number(${label_range_start}) and "
             "number(substr(.,3,6)) <= number(${label_range_end}) and "
             "substr(.,10,1) = ${label_check_expected} and "
             "count(../../../roster/specimen/specimen_label[. = current()]) <= 1",
  constraint_message="Label must be format BSN######-C, in your team's allocated range, with a "
                      "valid check digit, and not already used for another child in this same "
                      "household submission.")
constraint_entry("specimen_label", "5.03", "format + range + check-digit + within-submission dedup",
                  "regex ^BSN[0-9]{6}-[0-9X]$; 6-digit body inside the enumerator's own team "
                  "range (pulldata from specimen_label_allocation.csv); check character "
                  "recomputed via modulus-11, weights 2-7 right to left, and compared to the "
                  "entered character; must not repeat within this same household's roster "
                  "(count of matching labels across all roster/specimen/specimen_label nodes "
                  "in this submission <= 1)",
                  "Mistyped labels, a label affixed and typed from outside the team's "
                  "allocated block (allocation confirmed contiguous, no gaps/overlaps across "
                  "24 teams x 900 labels each, 480000-501599), transposed-digit-pair errors "
                  "the check digit is specifically designed to catch, and the same physical "
                  "label being typed twice for two different children in the same household",
                  "specimen_label_allocation.csv (24 rows) for the range; check-digit scheme "
                  "text in that same file ('Modulus 11, weights 2 to 7 applied right to left, "
                  "remainder 10 recorded as X'). See documentation/04_specimen_label_"
                  "validation.md for worked test vectors, and documentation/05_duplicate_"
                  "label_detection.md for why a same-submission check only catches labels "
                  "reused within one household and not the full 9-day device history.")

q("time", "specimen_cold_box_time", "Time the specimen was placed in the cold box",
  "Lokacin da aka sa samfurin cikin akwatin sanyi",
  relevant="${specimen_obtained}='1'", required=True)
q("decimal", "specimen_temp_c", "Temperature shown on the cold box thermometer",
  "Zafin da ke akwatin sanyi", relevant="${specimen_obtained}='1'", required=True,
  constraint=". >= 0.0 and . <= 12.0",
  constraint_message="Enter 0.0-12.0 degrees C.")
constraint_entry("specimen_temp_c", "5.05", "range", "0.0-12.0 degrees C",
                  "Miskeyed or unrealistic cold-chain temperatures (e.g. a stuck '99', or a "
                  "positive-but-implausible double-digit reading)",
                  "My judgement -- WHO cold-chain guidance targets 2-8C for specimen "
                  "transport; I padded to 0-12C to admit a plausible faulty-but-real "
                  "thermometer reading rather than only the ideal range, while still "
                  "rejecting clear entry errors")

q("select_one no_specimen_reason", "specimen_no_reason", "Reason no specimen was obtained",
  "Dalilin da ba a samu samfurin ba", relevant="${specimen_obtained}='2'", required=True)
q("text", "specimen_no_reason_other", "If Other, specify", "Idan Wani, bayyana",
  relevant="${specimen_no_reason}='96'", required=True)

end_group()  # specimen

end_repeat()  # roster

calc("roster_count_actual", "count(${roster})")
calc("roster_mismatch_flag", "if(${hh_size_stated} != ${roster_count_actual}, 1, 0)")
note("roster_vs_stated_note",
     "Stated household size was ${hh_size_stated}. The roster you just completed lists "
     "${roster_count_actual} people. Please recheck before continuing if these differ.",
     PENDING,
     relevant="${hh_size_stated} != ${roster_count_actual}")
constraint_entry("roster_count_actual / hh_size_stated", "3.01 vs Section 3 roster",
                  "cross-question consistency (soft, not blocking)",
                  "roster_count_actual = count(roster); roster_mismatch_flag=1 when it "
                  "differs from hh_size_stated; enumerator sees an on-screen note and must "
                  "actively continue past it, but the form is not blocked",
                  "A genuine mismatch between the pre-roster estimate (3.01) and the actual "
                  "listed count is real, common (memory, definitional disputes about who is "
                  "'usually resident'), and analytically important -- it must reach the office "
                  "for review, not be silently forced to agree or hard-blocked in the field",
                  "Q3 requirement 4: 'at minimum reconcile the stated household size against "
                  "the roster'")
constraint_entry("child-module count vs eligible count", "3.02 vs Section 4 pages completed",
                  "structural (by construction)",
                  "Not a validation rule: the child module is nested inside each roster row "
                  "and shown if and only if that row is age-eligible, so the count of "
                  "completed child modules and the count of eligible roster rows are the same "
                  "value by construction. 3.02 itself is no longer asked -- see D-01.",
                  "The paper's separate manual count (3.02) and separate manual line-number "
                  "re-entry (4.01) were themselves the source of the mismatch risk this "
                  "requirement exists to catch",
                  "Q3 requirement 4: 'the stated number of eligible children against the "
                  "number of child modules completed'")

end_group()  # s3

# ===========================================================================
# SECTION 6: HOUSEHOLD ENVIRONMENT
# ===========================================================================
begin_group("s6", "Section 6: Household environment", "Kashi na 6: Muhallin gida",
            relevant=form_active)

q("select_one water_source", "water_source", "Main source of drinking water",
  "Babban tushen ruwan sha", required=True)
q("select_one toilet_type", "toilet_type", "Kind of toilet facility usually used",
  "Irin bayan gida da ake amfani da shi", required=True)
q("select_one yes_no", "livestock_in_compound", "Does this household keep poultry or "
  "livestock inside the compound?", "Gidan yana da kaji ko dabbobi a cikin gida?",
  required=True)
q("select_one yes_no_dk", "animal_antibiotics_12m", "Have any antibiotic medicines been "
  "given to these animals in the past 12 months?", "An bawa dabbobin magungunan rigakafi "
  "cikin watanni 12 da suka wuce?", relevant="${livestock_in_compound}='1'", required=True)
q("select_one handwash", "handwash_station", "Handwashing station with soap and water "
  "available?", "Akwai wurin wanke hannu da sabulu da ruwa?", required=True)
q("select_one yes_no_dk", "hh_diarrhoea_2w", "Has any member of this household had "
  "diarrhoea in the past two weeks?", "Wani a gida ya sha gudawa cikin makonni biyu da suka "
  "wuce?", required=True)

q("select_multiple assets", "hh_assets", "Which of the following does this household own?",
  "Wanne daga cikin wadannan gidan yake da su?", required=True,
  constraint="not(selected(., 'H')) or count-selected(.)=1",
  constraint_message="'None of these' cannot be selected together with any other item.")
constraint_entry("hh_assets", "6.07", "mutual exclusivity", "selected('H') implies "
                  "count-selected=1 (None of these excludes every other option)",
                  "A response set that includes both 'None of these' and a specific asset "
                  "(e.g. mobile telephone), which is self-contradictory and breaks any "
                  "asset-index construction downstream",
                  "The paper form is a 'select all that apply' multi-select with no stated "
                  "exclusivity rule for its own 'None of these' category -- identified as "
                  "defect D-09 (data that cannot be analysed as printed), resolved in form")

end_group()  # s6

# ===========================================================================
# SECTION 7: CLOSE-OUT AND SUPERVISOR REVIEW
# ===========================================================================
begin_group("s7", "Section 7: Close-out and supervisor review", "Kashi na 7: Kammalawa",
            relevant=form_active)

calc("duration_minutes", "(decimal-date-time(${end}) - decimal-date-time(${start})) * 1440")
note("interview_end_note", "Interview end time is captured automatically when you submit; "
     "the form no longer asks you to type it separately (paper 7.01). See defects report and "
     "fabrication-detection doc.", PENDING)
constraint_entry("duration_minutes", "7.01", "added field, replaces manual entry",
                  "duration_minutes = (end - start) in minutes, computed from the system "
                  "start/end metadata rather than the enumerator typing a clock time",
                  "The manually-typed 7.01 time can be edited/guessed by an enumerator "
                  "wanting to disguise a short interview; the system timestamp cannot",
                  "Directly answers Q3 requirement 11 (fabrication detection) using the "
                  "operating-conditions fraud case as the design driver")

q("text", "supervisor_note", "Observation that may help the office interpret this form",
  "Bayani da zai taimaka wa ofis")
q("select_one enumerator", "supervisor_signoff_enum_code", "Enumerator signature (select "
  "your code again to confirm)", "Tabbatar da lambar ka", required=True)

end_group()  # s7

begin_group("s7sup", "Supervisor review (completed after handover, not by the enumerator)",
            "Bitar mai kula", appearance="field-list")

q("select_one enumerator", "supervisor_code", "Supervisor code", "Lambar mai kula")
q("select_one supervisor_decision", "supervisor_decision", "Supervisor decision on this "
  "form", "Shawarar mai kula")

end_group()

# ===========================================================================
# CHOICES
# ===========================================================================
def yn(list_name="yes_no"):
    choice(list_name, "1", "Yes", "Ee")
    choice(list_name, "2", "No", "A'a")


yn("yes_no")
choice("yes_no_dk", "1", "Yes", "Ee")
choice("yes_no_dk", "2", "No", "A'a")
choice("yes_no_dk", "8", "Do not know", "Ban sani ba")

choice("consent", "1", "Consent given", "An yarda")
choice("consent", "2", "Consent refused", "An ki")

# ---------------------------------------------------------------------------
# Below: real Hausa for every SHORT, HIGH-FREQUENCY, UNAMBIGUOUS choice list --
# family-relationship terms, water/toilet/asset categories, administrative
# decisions -- consistent with the language policy actually stated in
# documentation/06_language_and_translation.md. PENDING is reserved for full
# clinical/procedural SENTENCES (question text, constraint messages) and for
# the enumerator list, which needs no translation at all (see below), not for
# short everyday vocabulary. An earlier build broke this rule by defaulting
# every choice() call to PENDING and only overriding a handful -- caught by
# testing the form live in KoboToolbox, where a 120-option select_one
# (question 1.08) rendered the same placeholder string 120 times over in
# Hausa, the form's own default language. Fixed here, not papered over.
# ---------------------------------------------------------------------------
for code, label, ha in [("1", "Head", "Shugaban gida"), ("2", "Spouse", "Miji ko Matar aure"),
                         ("3", "Son or daughter", "Da ko 'Ya"), ("4", "Parent", "Uba ko Uwa"),
                         ("5", "Other relative", "Sauran dangi"),
                         ("6", "Not related", "Ba dangi ba")]:
    choice("relationship", code, label, ha)

for code, label, ha in [("1", "Head", "Shugaban gida"), ("2", "Spouse", "Miji ko Matar aure"),
                         ("3", "Son or daughter", "Da ko 'Ya"), ("4", "Parent", "Uba ko Uwa"),
                         ("5", "Other relative", "Sauran dangi"),
                         ("6", "Not related", "Ba dangi ba"), ("7", "Self", "Kansa/Kanta")]:
    choice("relationship_member", code, label, ha)

choice("sex", "1", "Male", "Namiji")
choice("sex", "2", "Female", "Mace")

choice("visit_result", "1", "Completed", "An kammala")
choice("visit_result", "2", "Refused", "An ki")
choice("visit_result", "3", "No competent adult after three visits",
       "Babu babba mai iya bayar da amsa bayan ziyara uku")
choice("visit_result", "4", "Dwelling vacant or demolished", "Gidan babu kowa ko an rushe shi")

choice("measure_status", "1", "Measured", "An auna")
choice("measure_status", "2", "Not measured", "Ba a auna ba")
choice("measure_status", "3", "Caregiver/child declined", "Mai kula ko yaro ya ki")

choice("measure_position", "1", "Recumbent length", "Tsawo, kwance")
choice("measure_position", "2", "Standing height", "Tsawo, a tsaye")

choice("card_seen", "1", "Card, card copy, or electronic record seen",
       "An ga katin, kwafinsa, ko bayanin lantarki")
choice("card_seen", "2", "No card seen", "Ba a ga kati ba")

choice("photo_status", "1", "Photograph taken", "An dauki hoto")
choice("photo_status", "2", "Not available", "Babu")
choice("photo_status", "3", "Caregiver declined", "Mai kula ya ki")

choice("no_specimen_reason", "1", "Caregiver refused", "Mai kula ya ki")
choice("no_specimen_reason", "2", "Child absent", "Yaro ba ya nan")
choice("no_specimen_reason", "3", "Unable to produce", "Ba a iya samu ba")
choice("no_specimen_reason", "4", "Container spoiled", "Akwatin ya lalace")
choice("no_specimen_reason", "96", "Other", "Wani")

water_opts = [
    ("Piped into dwelling", "Famfo a cikin gida"),
    ("Piped into compound", "Famfo a filin gida"),
    ("Public tap or standpipe", "Famfon jama'a"),
    ("Tube well or borehole", "Rijiyar bututu"),
    ("Protected dug well", "Rijiya mai kariya"),
    ("Unprotected dug well", "Rijiya marar kariya"),
    ("Protected spring", "Maɓulɓula mai kariya"),
    ("Unprotected spring", "Maɓulɓula marar kariya"),
    ("Rainwater", "Ruwan sama"),
    ("Tanker or cart", "Ruwan tanka ko keken ruwa"),
    ("Surface water", "Ruwan bude (kogi ko tafki)"),
]
for i, (label, ha) in enumerate(water_opts, start=1):
    choice("water_source", str(i), label, ha)

toilet_opts = [
    ("Flush to sewer", "Fasa ruwa zuwa magudanar ruwa"),
    ("Flush to septic tank", "Fasa ruwa zuwa tankin najasa"),
    ("Flush to pit latrine", "Fasa ruwa zuwa rami"),
    ("Ventilated improved pit", "Rami mai iska (VIP)"),
    ("Pit latrine with slab", "Rami mai bene"),
    ("Pit latrine without slab", "Rami marar bene"),
    ("Composting toilet", "Bayan gida na taki"),
    ("Bucket", "Bokiti"),
    ("No facility or bush", "Babu wurin, daji"),
]
for i, (label, ha) in enumerate(toilet_opts, start=1):
    choice("toilet_type", str(i), label, ha)

choice("handwash", "1", "Observed, soap and water", "An gani, akwai sabulu da ruwa")
choice("handwash", "2", "Reported only, not observed", "An fada kawai, ba a gani ba")
choice("handwash", "3", "Not present", "Babu")

for code, label, ha in [("A", "Radio", "Rediyo"), ("B", "Television", "Talabijin"),
                         ("C", "Mobile telephone", "Wayar hannu"), ("D", "Bicycle", "Keke"),
                         ("E", "Motorcycle", "Babur"), ("F", "Car or truck", "Mota ko babbar mota"),
                         ("G", "Refrigerator", "Firji"),
                         ("H", "None of these", "Babu ko daya daga cikin wadannan")]:
    choice("assets", code, label, ha)

choice("supervisor_decision", "1", "Accept", "An amince")
choice("supervisor_decision", "2", "Return for correction", "A mayar don gyara")
choice("supervisor_decision", "3", "Void", "An soke")

# Enumerator choice list sourced from staff_roster.csv (verified 120 rows,
# 24 teams x 5 staff, team codes 1:1 with specimen_label_allocation.csv).
# Small enough (120 rows) to sit in the survey's own choices sheet safely --
# unlike settlements (2,524 rows), this does not need external-file treatment.
# The Hausa column deliberately repeats the English label rather than PENDING:
# "Enumerator 003 (TM03, Ilela)" is a code/team identifier, not prose -- it
# needs no translation, and defaulting it to a placeholder was the actual bug
# (see the block comment above).
import csv as _csv
_staff_path = os.path.join(ROOT, "form", "media", "staff_roster.csv")
with open(_staff_path, encoding="utf-8-sig") as f:
    for r in _csv.DictReader(f):
        _enum_label = f"{r['label']} ({r['team_code']}, {r['assigned_lga']})"
        choice("enumerator", r["name"], _enum_label, _enum_label)

# Medicine list: PLACEHOLDER for a MISSING DATA PACK FILE, not a translation
# gap -- see constraint_register.csv and documentation/01_defects_report.md,
# defect D-05. Uses its own distinct placeholder so it cannot be mistaken for
# an ordinary pending-translation item when read in the field.
MEDICINE_PENDING = "[JERI BAI ISA BA — ana jira daga Ma'aikatar Lafiya]"
medicine_placeholder = [
    ("01", "Amoxicillin"), ("02", "Amoxicillin-clavulanate"),
    ("03", "Co-trimoxazole (sulfamethoxazole-trimethoprim)"), ("04", "Ampicillin"),
    ("05", "Ampicillin-cloxacillin combination"), ("06", "Erythromycin"),
    ("07", "Cefixime"), ("08", "Cefuroxime"), ("09", "Ciprofloxacin"),
    ("10", "Metronidazole"), ("11", "Gentamicin (injectable)"),
    ("12", "Chloramphenicol"), ("13", "Doxycycline/Tetracycline"),
]
for code, label in medicine_placeholder:
    choice("medicine_list", code, f"[PLACEHOLDER] {label}", MEDICINE_PENDING)
choice("medicine_list", "96", "Other", "Wani")

print(f"{len(rows)} survey rows, {len(choices)} choice rows, {len(register)} register rows")

# ===========================================================================
# WRITE THE XLSFORM WORKBOOK
# ===========================================================================
SURVEY_COLS = [
    "type", "name", "label::English (en)", "label::Hausa (ha)",
    "hint::English (en)", "hint::Hausa (ha)", "required", "relevant",
    "constraint", "constraint_message::English (en)", "calculation",
    "appearance", "default", "read_only", "choice_filter",
]
CHOICE_COLS = ["list_name", "name", "label::English (en)", "label::Hausa (ha)"]
SETTINGS_COLS = list(settings.keys())

wb = openpyxl.Workbook()
ws_survey = wb.active
ws_survey.title = "survey"
ws_survey.append(SURVEY_COLS)
for r in rows:
    ws_survey.append([r.get(c, "") for c in SURVEY_COLS])

ws_choices = wb.create_sheet("choices")
ws_choices.append(CHOICE_COLS)
for r in choices:
    ws_choices.append([r.get(c, "") for c in CHOICE_COLS])

ws_settings = wb.create_sheet("settings")
ws_settings.append(SETTINGS_COLS)
ws_settings.append([settings[c] for c in SETTINGS_COLS])

os.makedirs(os.path.dirname(FORM_PATH), exist_ok=True)
wb.save(FORM_PATH)
print(f"wrote {FORM_PATH}")

# ===========================================================================
# WRITE THE CONSTRAINT REGISTER
# ===========================================================================
REG_COLS = ["id", "field_name", "questionnaire_no", "rule_type", "rule_added",
            "prevents", "source_or_judgement"]
with open(REGISTER_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=REG_COLS)
    w.writeheader()
    for r in register:
        w.writerow(r)
print(f"wrote {REGISTER_PATH} ({len(register)} rows)")

