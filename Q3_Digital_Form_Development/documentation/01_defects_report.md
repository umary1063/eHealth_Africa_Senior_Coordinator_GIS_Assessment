# Questionnaire defects report

Q3 requirement 5. Nine defects were found while converting `Household_Questionnaire_HH2026v1.docx`
into `form/HH2026_v1.xlsx`. For each: what it is, where it lives in the paper form and/or the
build script, whether it was **resolved in the form** or **escalated** (not silently fixed), and
why. Field/constraint IDs refer to `constraint_register.csv` and `scripts/build_form.py`.

---

## D-01 — Internal contradiction: question 3.02 needs "office use" data live in the field

Section 3's roster table has a column **(7) "Eligible for Section 4 (office use)"**, explicitly
labelled as filled in later, off-field, by office staff. But question **3.02** ("From column (7),
how many children in this household are aged 9 to 59 completed months?") routes the skip to
Section 6 versus Section 4, **in the field, at interview time** — which requires column (7) to
already be populated live, contradicting its own "office use" label. The paper form cannot be
completed consistently as printed: either the enumerator computes eligibility live (contradicting
the column's stated purpose) or 3.02 cannot be answered.

**Resolved in form.** `eligible_s4` is a `calculate` field, computed live from `member_under5` and
`age_months` as each roster row is entered (`scripts/build_form.py`, roster repeat). Question 3.02
itself is no longer asked — see `constraint_register.csv` row C023. This removes the contradiction
by removing its cause, rather than papering over it with a note.
**Justification:** the "office use" instruction only made sense on paper, where a clerk really
could revisit the form later; a digital form can compute eligibility instantly and correctly at
zero cost to the enumerator, so keeping the paper's manual, contradictory version would have been
strictly worse.

---

## D-02 — Ambiguous instruction: which age column to fill for a borderline child

The roster's INTERVIEWER instruction says record age in months if under five, in years otherwise,
but gives no procedure for a child near the boundary (e.g. reported as "about five") beyond
enumerator judgement. Paper tolerates this; a digital form's `relevant` logic needs an explicit
branch or it cannot decide which field to show.

**Resolved in form**, by adding an explicit routing question (`member_under5`, not on the paper
form) asked before either age field. **Escalated in part:** the underlying ambiguity — how an
enumerator should decide "under five" for a child whose birth date is unknown and who looks
borderline — is a fieldwork judgement call the form cannot resolve and the questionnaire does not
address; recommend the ministry add a short probe sequence (e.g. relate age to a local
seasonal/event calendar) to the enumerator manual, not the form itself.

---

## D-03 — Sentinel/measurement collision: "99 = not measured" inside a continuous field

Questions **4.05** (weight) and **4.06** (height/length) use the code **99** for "not measured"
inside what is otherwise a continuous decimal field (`⌷⌷.⌷ kg`, `⌷⌷⌷.⌷ cm`). On paper this is
harmless — a human reader recognises 99.0 kg as impossible for a 9–59 month child. In a digital
numeric field, 99 is simply a valid, in-range-looking decimal; nothing distinguishes a genuine
(if extreme) measurement from the sentinel. This is the central sentinel-handling defect this
assessment asks for (Q3 requirement 3) and is discussed in full, with every other coding
collision checked, in `02_sentinel_coding_scheme.md`.

**Resolved in form.** Each measurement is split into a `select_one` status field
(`weight_status` / `height_status`: measured / not measured / caregiver or child declined) plus a
numeric field that is only `relevant` (and only `required`) when status = measured. The analysis
team can never receive a `99` in a column of real weights or heights — a non-response is a missing
value in the numeric column and an explicit reason code in the status column, not a magic number
mixed into the measurements. See `constraint_register.csv` rows C013, C015.

---

## D-04 — Redundant question invites a second sentinel-style contradiction

Question **5.01** ("Is the child aged 12 completed months or older?") restates a fact already
captured two questions earlier at **4.03** (age in completed months, copied from the roster). On
paper, re-asking this is merely redundant. In a digital form it is a live hazard: nothing stops an
enumerator answering "yes, ≥12 months" for a child whose `age_months` is 10, creating a value that
directly contradicts data already on the same form.

**Resolved in form.** Section 5 (specimen collection)'s `relevant` condition is
`${eligible_s4}=1 and ${age_months} >= 12` — computed directly from the age already on file. 5.01
is not asked. See `constraint_register.csv` row C019.
**Justification:** the paper question adds no information the form does not already have, and
removing it removes a contradiction the paper form has no mechanism to prevent, catch, or resolve.

---

## D-05 — Data-pack gap: no medicine list was supplied

The paper form (4.13) instructs: "Record from the medicine list." No such file exists anywhere in
`reference_media/` (the pack's own `README.md` mentions "a medicine list" among the external
lookups the form depends on, but does not include one — confirmed by directory listing and a
full-text search of the pack for "medicine"/"antibiotic").

**Reported, not resolved, and not substituted for.** Earlier drafts of this form filled the gap
with an illustrative list of common antibiotics composed from general clinical knowledge — first
presented with every choice prefixed `[PLACEHOLDER]`, then, after that was found to make the
running form unreadable during live testing on KoboToolbox, with the placeholder wording moved to
the question level and the drug names shown plainly ("WHO AWaRe-informed"), and briefly a plain
free-text field. All three were reviewed and rejected as the same underlying mistake: inventing a
substitute for missing data-pack content, which is exactly what the assessment's own instructions
caution against — the common data-pack conditions call for *identifying and reporting* defects,
not filling them in with material of my own choosing, however clinically plausible, however
clearly labelled, or however unstructured. A list sourced from a real public document (WHO AWaRe,
a national Essential Medicines List) would still not be *this survey's* ministry-approved
formulary code list; free text avoids inventing drug names but still lets the field be answered
at all, which is not accurate to the actual state of the data pack.

`antibiotic_code` is now `select_one_from_file medicine_list.csv` — wired exactly like the
LGA/Ward/Settlement cascade (an external CSV attached as form media, `name`/`label` columns) —
but `form/media/medicine_list.csv` ships as a **stub**: a header row only, zero data rows. No
antibiotic name, invented or cited, appears anywhere in the running form. The field is structured
to receive the ministry's actual coded list the moment it is supplied and the CSV is repopulated
and reattached — no other change to the form is needed — but until then it has, correctly, no
answer to offer. This is the concrete meaning of "we will ask for the missing choice list": the
form stays honestly blocked at this one question rather than working around the gap.

---

## D-06 — The paper form cannot support the exact fraud pattern in the operating conditions

The paper form has **no interview start-time field at all** — only **7.01**, "Time the interview
ended." The operating conditions describe an enumerator who submitted 94 interviews with a mean
duration of 4 minutes, discovered only after fieldwork closed. That signal is *duration*
(end − start). As printed, the paper form cannot compute a duration, because it never records a
start time; the fraud pattern that motivates requirement 11 (fabrication detection) cannot be
detected from the paper form's own fields, at any point, retrospectively or live.

**Resolved in form.** Standard ODK `start`/`end` metadata timestamps are captured automatically
(no respondent or enumerator burden), and `duration_minutes` is calculated from them
(`constraint_register.csv` row C025). 7.01 itself is replaced by the automatic `end` timestamp —
an enumerator can no longer type a flattering end time. See `08_fabrication_detection.md` for the
daily check this feeds.

---

## D-07 — The fieldwork window disagrees with itself across two documents

The questionnaire's own header states: *"Form HH/2026/v1 · Fieldwork period 1 to 30 June 2026"* —
a 30-day window. The assessment's operating conditions state fieldwork runs **14 days**. These are
two different documents (the ethics-approved instrument vs. the assessment brief) and I cannot
determine from the data pack which is authoritative, or which 14 days within June are meant if the
brief is correct.

**Escalated, with a stated working assumption.** `visit_date` is constrained to `2026-06-01`
through `2026-06-30` (`constraint_register.csv` row C006) because that is the text printed on the
ethics-approved form itself, which I judged more authoritative than the assessment brief's summary
of operating conditions. If the true intended fieldwork window is a 14-day sub-period, the
ministry must confirm which 14 days, and the constraint's bounds should be tightened accordingly —
a one-line change, flagged here so it is not missed.

---

## D-08 — Missing/ambiguous skip instruction at question 5.02

Question **5.02**, "Was a stool specimen obtained from this child?", has **no skip instruction at
all** in the SKIP column — neither branch says what to do next. Questions 5.03–5.05 (label, cold
box time, temperature) only make sense if a specimen was obtained; question 5.06 ("Reason no
specimen was obtained") only makes sense if one was not. The paper form is silent on this routing.

**Resolved in form, with escalation.** I judged the only internally consistent reading —
`specimen_label`/`specimen_cold_box_time`/`specimen_temp_c` relevant only when
`specimen_obtained='1'`; `specimen_no_reason`/`specimen_no_reason_other` relevant only when
`specimen_obtained='2'` — and implemented it (`constraint_register.csv`, Section 5 fields). This
reading has high confidence because the alternative (asking 5.03–5.07 unconditionally) produces
nonsensical required fields on every specimen-refused case. It should still be put to the ministry
for confirmation before the next print run of the paper form, since a missing skip instruction on
an ethics-approved instrument should not be corrected there without sign-off, even though the
digital form must resolve it to be usable at all.

---

## D-09 — Data that cannot be analysed as printed: an unconstrained "select all" with a "none" option

Question **6.07** ("Which of the following does this household own? Record all that apply") is a
multi-select over eight items (A–H), where **H = "None of these."** The paper form states no
exclusivity rule. An enumerator can tick both H and, say, C ("Mobile telephone") — a
self-contradictory response. As printed, nothing prevents this, and once it occurs, standard
asset-index construction (e.g. for a wealth quintile) has no defensible way to treat that row: is
it an asset-owning household or not?

**Resolved in form.** `hh_assets` carries `constraint: not(selected(., 'H')) or count-selected(.)=1`
— H excludes every other option (`constraint_register.csv` row C024).
**Justification:** this is a case where "the paper design permits data that cannot be analysed"
(Q3 requirement 5) in a very literal sense — there is no post-hoc coding rule that recovers a
sensible value from H-plus-something-else, so preventing it at entry is the only option that does
not either discard the response outright at cleaning time or force an arbitrary tie-break the
paper form never specified.

---

## Summary table

| ID | Type | Resolved in form? | Escalated? |
|---|---|---|---|
| D-01 | Internal contradiction | Yes | — |
| D-02 | Ambiguous instruction | Partially | Yes (enumerator-manual guidance needed) |
| D-03 | Sentinel/measurement collision | Yes | — |
| D-04 | Redundant/contradiction-prone question | Yes | — |
| D-05 | Data-pack gap (missing medicine list) | No — field staged (`select_one_from_file` against an empty stub CSV), no substitute content | Yes |
| D-06 | Unanalysable data (no duration signal) | Yes | — |
| D-07 | Cross-document inconsistency (fieldwork window) | Working assumption used | Yes |
| D-08 | Missing/ambiguous skip instruction | Yes | Yes (confirm before next paper print run) |
| D-09 | Unanalysable data (multi-select exclusivity) | Yes | — |

Every requirement-5 category is covered by more than one instance: internal contradiction
(D-01, and arguably D-04/D-08), missing/ambiguous skip (D-08, and D-02), and data that cannot be
analysed (D-09, D-06).
