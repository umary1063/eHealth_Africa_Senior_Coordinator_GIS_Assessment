# Sentinel/non-response coding scheme

Q3 requirement 3. The paper form's "Notes on completion" set a standard, uniform sentinel
convention: **8 / 98 = don't know**, **9 / 99 = asked but no answer obtained**, and any coding list
ending in **96 = Other (specify)**. This document goes through every question on the form and
states how each is stored, and flags every place a sentinel collides with a real measurement.

## The rule applied throughout the digital form

**A sentinel is never stored in the same column as a measurement.** Every field that could
receive a non-response code is one of:

1. A `select_one` field whose choice list *includes* the sentinel as an explicit, named option
   (e.g. `8 = Do not know`) — safe by construction, because a `select_one`'s stored value is
   always one of its declared choices; there is no numeric range for a sentinel to collide with.
2. A continuous numeric field with **no sentinel value at all**, paired with a separate
   `select_one` status field that carries the non-response reason. The numeric field is only
   `relevant` when the status field says a real value was obtained.

Category 2 is the fix for the one real collision on this form (below). Category 1 covers every
other yes/no/don't-know question, and needs no special handling — a `select_one`'s XML value is
one of `1`/`2`/`8` etc., an opaque code, not a number the analyst could confuse with a
measurement.

## Places checked for a coding-category / non-response collision

| Question(s) | Field(s) | Type used | Collision risk | Resolution |
|---|---|---|---|---|
| 1.12, 1.14(no), 3.01(dk n/a) | `prev_round_visited` | `select_one` (1/2/8) | None — categorical | — |
| 4.09/4.10/4.11/4.12, 6.04, 6.06 | `measles_from_card` etc. | `select_one` (1/2/8) | None — categorical | — |
| **4.05 weight** | `c_weight_kg` | was: decimal with sentinel 99 embedded | **Yes — 99 kg reads as a plausible-looking value in an unconstrained decimal field** | Split: `weight_status` (select_one: measured/not measured/declined) + `c_weight_kg` (decimal, `relevant` only if measured, range 2.0–30.0, no sentinel value exists in this field) |
| **4.06 height/length** | `c_height_cm` | was: decimal with sentinel 99 embedded | **Yes — same issue, 99.9 cm** | Split: `height_status` + `c_height_cm` (decimal, `relevant` only if measured, range 45.0–130.0) |
| 4.13 antibiotic code | `antibiotic_code` | `select_one_from_file medicine_list.csv` (stub, no rows — see defect D-05) | Not applicable — no coded list exists yet | No content to collide with a sentinel; the CSV ships empty rather than with fabricated categories, so this question has no answer to give until the ministry supplies the real list |
| 5.06 reason no specimen | `specimen_no_reason` | `select_one` incl. `96 = Other` | None — categorical | `specimen_no_reason_other`, same pattern |
| 6.07 asset ownership | `hh_assets` | `select_multiple` incl. `H = None of these` | Structural, not sentinel (see defect D-09) | Mutual-exclusivity constraint, `01_defects_report.md` |
| 3.01 household size, 3.02 (removed), 1.06/1.07 structure/serial numbers | integers | `integer` | None stated on paper (no DK/refusal code offered for these counts) | Left as required, ranged integers; no sentinel to collide with because the paper form does not define one here |

No other numeric (integer/decimal) field on the paper form carries a stated non-response sentinel.
4.05 and 4.06 were the only two places where a genuine measurement column and a genuine
non-response code shared the same field on paper.

## Why a split field rather than a reserved out-of-range sentinel

An alternative fix would keep one field and reserve a value clearly outside the plausible range
(e.g. `-1` for "not measured"). Rejected: it still requires every downstream user of the raw
export (the analysis team, working in English, per the operating conditions) to know and correctly
apply that convention before they can treat the column as numeric, which is exactly the kind of
tacit knowledge that caused the original collision. A separate status field is self-documenting in
the codebook (`10_codebook.md`) and requires no special-casing in analysis code — `c_weight_kg` is
either a real number or genuinely missing (NA), never a coded stand-in.
