# Fabrication detection, daily, during fieldwork

Q3 requirement 11, directly driven by the operating-conditions case: one enumerator submitted 94
interviews with a mean duration of 4 minutes and almost no vaccination cards sighted, discovered
only after fieldwork closed. A design that can only detect this after the fact has failed this
requirement — the fields and the daily check below exist specifically so it is caught inside the
14-day window, while revisits are still possible.

## Fields that exist solely to enable this (not asked of the respondent)

| Field | What it captures | Why it exists |
|---|---|---|
| `start` / `end` (system) | ODK's own open/finalize timestamps | The paper form has no start time at all (defect D-06) — without these, duration cannot be computed, ever, from any export |
| `duration_minutes` (calculated) | `(end - start)` in minutes | The single metric that identifies the exact fraud pattern described in the operating conditions |
| `device_id` (system) | Which tablet produced the submission | Groups submissions by device/enumerator for the daily check below |
| `roster_mismatch_flag` (calculated) | 1 if stated household size ≠ actual roster count | A fabricated interview is more likely to show a stated/actual mismatch, since the two numbers are supplied at different points and a fabricator has less reason to keep them consistent |
| `vacc_card_seen` (`card_seen` choice list) | Card seen / not seen, per child | Directly the second signal named in the operating conditions ("almost no vaccination cards sighted") |
| `antibiotic_photo_file` (added; not on paper form) | Photograph of medicine packaging | 4.16 on paper only records *whether* a photo was taken; without the photo itself the office cannot verify that claim at all, fabricated or not |
| `enumerator_code`, `team_code_display` | Who collected it | Needed to aggregate every check below per enumerator, not just per form |

None of these are shown to or answered by the respondent; they exist purely for back-office QA,
which is what requirement 11 asks for explicitly.

## The daily check

Run once per day against everything synced from the field so far (Central's OData/submission API,
or a scheduled export), grouped by `enumerator_code`:

1. **Mean and distribution of `duration_minutes`.** Flag any enumerator whose mean interview
   duration falls under a threshold implausible for a household+roster+child-module+specimen
   interview. I did not find a stated minimum plausible duration anywhere in the data pack, so I
   propose (my judgement, not a data-pack figure) flagging **any enumerator whose day's mean
   `duration_minutes` is under 12 minutes**, and separately flagging **any individual interview
   under 4 minutes** for supervisor spot-check regardless of that enumerator's overall mean — the
   94-interview case in the operating conditions is described by exactly this pattern (mean ~4
   minutes), so the threshold is set to catch that case with margin, not tuned to it exactly.
2. **Card-sighting rate.** Flag any enumerator whose share of `vacc_card_seen = 1` ("card seen")
   falls far below the day's team/ward average — the second half of the same case ("almost no
   vaccination cards sighted"). A short interview *and* a near-zero card-sighting rate together is
   a strong joint signal; either alone is weaker and should prompt review, not an automatic
   accusation.
3. **`roster_mismatch_flag` rate.** Flag any enumerator whose share of mismatched
   stated-vs-actual household size is an outlier against the day's team average.
4. **Volume vs. duration together.** Flag any enumerator whose daily interview count is high while
   their mean duration is low — the combination (not either alone) is what made the 94-interview
   case implausible; a genuinely fast, competent enumerator with a normal duration is not a
   fabrication signal by itself, and neither is a single long day if durations look normal.
5. **Specimen photo/label cross-check.** Any enumerator with a high rate of `specimen_obtained=1`
   but `antibiotic_photo=2` ("not available") where `antibiotic_30d=1` (antibiotic reported)
   deserves a supervisor look — not proof of fabrication on its own, but a pattern worth
   correlating with (1)-(4) rather than ignoring in isolation.

None of these five is proposed as a standalone hard rule that blocks or discards data
automatically; each produces a flagged enumerator/day for a supervisor to actually review (e.g.
call the enumerator, spot-check a revisit), consistent with the data pack's own instruction not to
silently drop records that a defect makes hard to interpret.

## Why "daily," not "after fieldwork closes"

Every input above (`duration_minutes`, `vacc_card_seen`, `roster_mismatch_flag`, `device_id`) is
present on every submission as soon as it syncs, not computed retrospectively from a full-round
export. Running the same five checks as a scheduled daily job against Central's submission API
(rather than as a one-off analysis after the round closes) is what turns this from a
retrospective finding into an in-fieldwork catch — the actual requirement.
