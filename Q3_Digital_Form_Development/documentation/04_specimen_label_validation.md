# Specimen label validation

Q3 requirement 7. Implemented in `form/HH2026_v1.xlsx`, field `specimen_label` (question 5.03),
using the scheme stated in `reference_media/specimen_label_allocation.csv`: *"Modulus 11, weights
2 to 7 applied right to left, remainder 10 recorded as X."*

## The scheme, made explicit

Label format: `BSN` + 6 digits + `-` + 1 check character (matches the paper form's boxes:
`BSN ⌷⌷⌷⌷⌷⌷ - ⌷`).

For the 6 body digits `d1 d2 d3 d4 d5 d6` (left to right), the weights read right to left starting
at 2 mean `d6` (rightmost) gets weight 2, `d5` gets 3, ... `d1` (leftmost) gets weight 7:

```
checksum = 7*d1 + 6*d2 + 5*d3 + 4*d4 + 3*d5 + 2*d6
check_value = checksum mod 11
check_digit = 'X' if check_value == 10 else str(check_value)
```

Implemented in the form as calculated fields (`label_digits`, `label_checksum`,
`label_check_expected`), reproduced in `scripts/checkdigit_reference.py` in this repository for
independent verification outside ODK.

## Why this scheme actually catches a transposed pair — not just asserts it

This is provable, not just empirically demonstrated: swapping two **adjacent** digits at
positions carrying weights `w` and `w+1` (every pair of adjacent positions in this scheme differs
by exactly 1: weights are 7,6,5,4,3,2 in sequence) changes the checksum by exactly
`(a − b) × 1 = (a − b)`, where `a`, `b` are the two swapped digit values. Because digits are 0–9,
`a − b` ranges from −9 to 9 and is 0 only when `a = b` — i.e. only when there was no real error.
Since 11 is prime and larger than the maximum possible non-zero change of 9, `(a − b) mod 11` can
never be 0 for a genuine transposition, so the checksum — and therefore the check digit — always
changes. **This scheme catches every adjacent-digit transposition in the 6-digit body,
unconditionally**, not just the specific example below.

## Worked test vectors (computed by `scripts/checkdigit_reference.py`, not hand-typed)

| Body | Checksum | mod 11 | Check digit | Full label |
|---|---|---|---|---|
| 480000 | 76 | 10 | **X** | `BSN480000-X` |
| 480001 | 78 | 1 | **1** | `BSN480001-1` |
| 480012 | 83 | 6 | **6** | `BSN480012-6` |
| 480021 (480012 with last two digits transposed) | 84 | 7 | **7** | `BSN480021-7` |
| 480899 (TM01 range end) | 153 | 10 | **X** | `BSN480899-X` |
| 480900 (TM02 range start — outside TM01's block) | 112 | 2 | **2** | `BSN480900-2` |

## The transposition case, spelled out

The physical label affixed to the specimen reads **`BSN480012-6`**. Suppose the enumerator
transposes the last two body digits while transcribing it into the text field and types
**`BSN480021-6`** (correctly copying the check character they saw, but mistyping the body).
The form recomputes the expected check digit for body `480021`, which is **7**, not **6**. The
entered check character (`6`) does not match the recomputed one (`7`), so the `constraint` on
`specimen_label` fails and the enumerator is asked to re-enter the label — exactly the failure
mode requirement 7 asks to be demonstrated, not just a case where a valid label is accepted.

## Full constraint (from `form/HH2026_v1.xlsx`)

```
regex(., '^BSN[0-9]{6}-[0-9X]$')
and number(substr(.,3,6)) >= number(${label_range_start})
and number(substr(.,3,6)) <= number(${label_range_end})
and substr(.,10,1) = ${label_check_expected}
and count(../../../roster/specimen/specimen_label[. = current()]) <= 1
```

Four independent checks combine with `and`, each catching a different real failure mode:
1. **Format** — catches stray characters, wrong length, missing hyphen.
2. **Team range** (`label_range_start`/`label_range_end`, pulled via `pulldata()` from
   `specimen_label_allocation.csv` keyed on the enumerator's own `team_code_auto`) — catches a
   label affixed and typed from a block allocated to a different team (e.g. TM02's stock used on
   a TM01 form), which the check digit alone would never catch since the label itself is
   internally valid.
3. **Check digit** — catches transpositions and most single-digit miskeys, as proven above.
4. **Within-submission duplicate** — catches the same physical label being typed for two
   different children in the same household. See `05_duplicate_label_detection.md` for why this
   is the achievable part of requirement 8, and what it does not cover.

See `test_plan.csv` for the full set of pass/fail cases run against this field, including the
boundary values (`480899` inside TM01's block, `480900` just outside it).
