# What was deliberately not implemented, and why

Q3 requirement 14. Everything below was considered and left out on purpose, not missed.

1. **ODK Entities for full cross-submission duplicate-label detection.** Described in full in
   `05_duplicate_label_detection.md` as the correct production architecture. Not implemented
   because I cannot test it against a real ODK Central/Collect instance in this environment, and
   an untested Entities declaration risks either failing to convert or silently not behaving as
   claimed — worse than the honest gap. What *is* achievable without that risk (a same-submission
   duplicate check) is implemented.

2. **Full Hausa translation of question text and constraint messages.** Structural support
   (language columns, default language) is complete; the translations themselves are marked
   pending professional translation and back-translation, per `06_language_and_translation.md`. A
   confidently wrong clinical translation is a worse outcome for a low-English-confidence
   enumerator corps than a visible placeholder.

3. **Audio prompts.** The operating conditions describe a workforce with a mean of six years of
   schooling and low English confidence — audio-recorded Hausa prompts (ODK supports per-question
   audio media) would likely help more than translated text alone. No audio assets were supplied
   in the data pack and recording/vetting them is outside a data-engineering deliverable; flagged
   as a recommended follow-up investment, not attempted here.

4. **Section 8, "Office use only" (8.01–8.03).** This describes a paper-file receipt and
   double-entry verification workflow (form received date, data entry clerk code, second-entry
   verification) that has no equivalent meaning once submissions arrive in ODK Central already
   timestamped, attributed, and structured — there is no second manual data-entry pass to verify
   in a digital pipeline. Implementing it as inert digital fields would misrepresent a paper-era
   control as still operative. Digital equivalents (submission-received timestamp, reviewer
   identity) already exist as Central system metadata and are documented as such in
   `10_codebook.md` rather than duplicated as form fields.

5. **A stated procedure for households with more than 12 usual residents.** The paper roster
   table is physically ruled for exactly 12 lines with no continuation-sheet instruction. The
   digital `roster` repeat has no hard cap tied to that paper artefact — it is a normal dynamic
   ODK repeat, constrained only by the generous judgement ceiling on `hh_size_stated` (1–30, see
   `constraint_register.csv` row C009) — so the digital form does not inherit the paper
   limitation. I did not add a formal continuation-sheet *procedure document* for the (now
   largely moot) paper form, since that is a ministry administrative decision, not a form-design
   one.

6. **Device-storage tuning for the evidence photo field** (`antibiotic_photo_file`, added per
   D-06/requirement 11). `conversion/conversion_log.txt` records pyxform's own suggestion to set a
   `max-pixels` appearance parameter to bound image size given the 2 GB device constraint. I did
   not set a specific value because the right ceiling depends on per-device storage headroom
   across a 9-day offline stretch with potentially many photographed packages, which the data pack
   does not state — picking an arbitrary number here would be presented as calibrated when it is
   not. Flagged as a pre-deployment tuning task with the actual device storage budget in hand.

7. **A guidance hint on `supervisor_note` discouraging identifying free text.** Named as a
   recommendation in `09_data_protection.md`. Left out of the submitted form to keep this
   submission's changes scoped to what the numbered requirements ask for, rather than
   accumulating unscoped extra edits alongside them.

8. **Encryption at rest, Central access control, and a formal data management plan.**
   Infrastructure/governance matters outside anything an XLSForm configures, and outside the
   reference media supplied — named in `09_data_protection.md` as out of scope rather than
   silently unaddressed.

9. **Field-testing on physical Android hardware.** `conversion/conversion_log.txt` documents a
   real, successful XLSForm→XForm conversion including the Java-based ODK Validate structural
   check — the same validator ODK Central runs before accepting a form. It does not, and cannot,
   confirm runtime behaviour on an actual 2 GB Android tablet (rendering performance of the
   settlement cascade with 2,524 real rows in `select_one_from_file`, exact behaviour of
   `pulldata()` against the shipped CSVs, real GPS/geopoint capture). A device pretest with a
   small enumerator sample, covering at least the settlement search, the specimen label entry,
   and one full end-to-end household+child+specimen interview, should happen before the full
   24-team rollout.

10. **A resolution to the operating-conditions vs. staff-roster headcount mismatch.** The
    operating conditions state "120 enumerators in 24 teams." `reference_media/staff_roster.csv`
    actually has 120 rows total, but only 96 carry `role = Enumerator`; the remaining 24 carry
    `role = Team supervisor` (one per team, matching "24 teams" exactly). I treated 120 as the
    total field-staff headcount (`enumerator` choice list, Section 1) since that is what the
    roster supports, rather than assuming 120 enumerators *plus* 24 supervisors (144 total, not
    matched by any file in the pack). This is recorded here rather than silently resolved because
    it changes the denominator for any per-enumerator workload calculation (e.g. specimen labels
    per enumerator: 900 labels ÷ 5 staff per team, not ÷ a hypothetical larger team).

11. **A duplicate PIN in `staff_roster.csv`** (`pin = 1785` appears twice, for two different
    `name` values) was found during data exploration but is not used anywhere in the digitised
    form — the form authenticates nobody by PIN, it only looks enumerators up by `enumerator_code`
    via a `select_one`, so the duplicate has no effect on this deliverable. Noted here in case the
    PIN field is intended for a login/authentication mechanism elsewhere in the programme, where a
    duplicate would matter.
