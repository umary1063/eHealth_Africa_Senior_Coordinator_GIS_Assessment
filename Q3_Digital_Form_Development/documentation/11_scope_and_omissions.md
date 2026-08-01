# What was deliberately not implemented, and why

Q3 requirement 14. Everything below was considered and left out on purpose, not missed.

1. **ODK Entities for full cross-submission duplicate-label detection — implemented and verified,
   2026-08-01.** Originally scoped out here because it could not be tested against a real ODK
   Central/Collect instance. That instance later became available; the feature is now implemented
   (an `entities` sheet, `save_to` bindings, and an added constraint clause on `specimen_label`)
   and its create-side mechanism verified end to end against a live Central instance — full detail
   and the one remaining unverified piece (a live client-side rejection click-through, inconclusive
   due to browser-automation limits in the verification session, not a form defect) in
   `05_duplicate_label_detection.md`. Left listed here, updated rather than deleted, so the record
   shows this item moved from "deliberately out of scope" to "done" rather than quietly
   disappearing.

2. **Full Hausa translation of question text and constraint messages — escalated, not resolved.**
   Structural support (language columns, default language) is complete; the translations
   themselves are marked pending professional translation and back-translation, per
   `06_language_and_translation.md`. A confidently wrong clinical translation is a worse outcome
   for a low-English-confidence enumerator corps than a visible placeholder. The
   `constraint_message` gap specifically is flagged there as a pre-deployment blocker: it matches
   the assessment's own automatic-loss-of-marks condition on constraint messages left in a
   language the enumerator cannot read, and must be resolved with a reviewed professional
   translation before fieldwork, not left as-is.

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
   check — the same validator ODK Central runs before accepting a form. Since that conversion,
   the form has also been deployed to a live KoboToolbox project (a KoboToolbox/ODK-family
   platform) with all six media CSVs attached and exercised through KoboToolbox's own Enketo
   preview in a desktop browser — this confirmed the LGA→Ward→Settlement cascade resolves
   correctly against `select_one_from_file` with the real CSVs attached, the GPS/geopoint widget
   renders with an OpenStreetMap picker, and the default-language switch to Hausa takes effect.
   That same live test is what surfaced the language-policy bug documented in
   `06_language_and_translation.md` (the 120-row enumerator list rendering an identical
   placeholder string in Hausa) — a genuine defect found by functional testing, not a hypothetical
   one, now fixed.

   A self-hosted ODK Central instance (Oracle Cloud "Always Free" tier VM) is being provisioned to
   continue this testing properly — Central, unlike a bare XLSForm-to-XForm converter or
   KoboToolbox's shared hosting, is the actual target deployment platform this form is designed
   for, and lets the specimen-label check digit, the within-household duplicate constraint, the
   `medicine_list.csv` stub behaviour (defect D-05), and real ODK Collect Android behaviour all be
   exercised against the same project the 24 teams would actually use. Central correctly listed
   `medicine_list.csv` among the form's seven required attachments during setup — confirming the
   stub's dependency is declared correctly — but an attachment with zero data rows is a dead end
   for manually clicking through the rest of the form during a walkthrough, since question 4.13
   then has nothing to select. `testing/medicine_list_DUMMY_FOR_CENTRAL_TESTING_ONLY.csv` was
   created at the candidate's explicit request, purely to unblock that one field on the Central
   test project so the remaining sections can be exercised end to end; it uses deliberately fake,
   unmistakable placeholder entries, is documented as a testing aid only in `testing/README.md`,
   is not referenced by `scripts/build_form.py`, and does not replace the committed
   `form/media/medicine_list.csv` stub, which remains the empty file that ships with the actual
   deliverable.

   This live rendering also surfaced a real bug that static review of the script had not caught:
   the Section 7 group carrying `supervisor_note` (7.02) and the enumerator's own sign-off
   (`supervisor_signoff_enum_code`, 7.03) was gated behind `form_active`
   (`visit_result='1' and consent_given='1'`) — meaning it was unreachable whenever the interview
   ended early. Two on-screen notes elsewhere in the form (`end_note_no_further`,
   `consent_refused_note`) both instruct the enumerator to "sign at 7.03 and submit" in exactly
   those cases, which is also what the paper form itself says to do for a refused, vacant, or
   no-competent-adult outcome. The group's `relevant` condition has been removed — 7.02/7.03 are
   now always reachable, version `2026073101` — see `constraint_register.csv`. Nothing else in
   the form's logic depends on this change; it only affects when that one group is shown.

   What remains genuinely untested as of this build: runtime behaviour on an actual 2 GB Android
   tablet specifically
   (rendering performance of the settlement cascade against 2,524 real rows on low-end hardware,
   ODK Collect's own offline handling of the attached CSVs, and real-world GPS capture in the
   field rather than a desktop browser's location API), and the specimen-label check-digit and
   within-household-duplicate constraints, which have not yet been exercised through the running
   form by a human tester. A device pretest with a small enumerator sample, covering at least the
   specimen label entry (including a deliberate transposition) and one full end-to-end
   household+child+specimen interview, should still happen before the full 24-team rollout.

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
