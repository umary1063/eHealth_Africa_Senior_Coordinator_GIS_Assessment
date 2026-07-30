# Duplicate-label detection across submissions from the same device

Q3 requirement 8: *"State plainly whether a self-contained form can enforce that. If it cannot,
describe the architecture that can, and implement whatever part is achievable in the form
itself."*

## Plainly: no, a single self-contained XLSForm instance cannot enforce this in full

A running ODK form instance only has reliable access to: (a) its own data, and (b) — via the
`instance('last-saved')` feature — a snapshot of the **single most recent** submission finalised
on that device. It has no built-in access to the full history of everything that device has
submitted over a 9-day offline stretch. There is no standard, low-risk XLSForm construct that
queries "every specimen_label this device has ever submitted" from inside a form definition. Any
claim otherwise for a plain XLSForm would be a claim I could not actually verify compiles and
behaves correctly without production testing against real ODK Collect devices, which I do not
have available for this assessment — so I have not implemented one, and say so here rather than
present something untested as working (see `11_scope_and_omissions.md`).

## What was implemented (achievable in the form itself)

`specimen_label`'s `constraint` includes:

```
count(../../../roster/specimen/specimen_label[. = current()]) <= 1
```

This checks, **within the current submission**, whether the label just entered already appears
against another child in the same household's roster. It catches the same physical label being
typed twice for two different children in one household — a realistic and, unlike the full
cross-submission case, entirely safe-to-implement check (no cross-form-instance state, no
dependency on device history or connectivity). See `04_specimen_label_validation.md` for the full
constraint and `constraint_register.csv` row C020.

I deliberately did not implement an `instance('last-saved')`-based cross-submission check. An
earlier draft attempted one (comparing the entered label against the specimen label on the
device's single previous submission), but on review this only ever catches the *immediately*
preceding submission — a label reused three households ago on the same device would pass — while
adding real risk of an XPath error if the previous submission had no specimen recorded at that
repeat position at all (e.g. the last household had no eligible children). The narrow benefit did
not justify the fragility, so it was removed in favour of the honest architecture description
below.

## The architecture that can enforce this in full: ODK Entities + server-side reconciliation

**ODK Entities** (a feature of recent ODK Central/Collect) let a form both *create* records into a
named, versioned dataset and *read* that same dataset back — including entries created by earlier
submissions **on the same device while still offline**, because Collect maintains a local copy of
each entity list and updates it immediately after every local finalize, syncing to Central only
when connectivity returns. The production design:

1. Declare an entity list `used_specimen_labels` (properties: `label`, `device_id`, `timestamp`).
2. On finalizing a household submission, each `specimen_label` value creates one entity.
3. At label entry, the form checks the local entity list for an existing entity with that
   `label` value before accepting it — catching duplicates from *any* earlier submission on that
   same device, offline, not just the immediately preceding one.
4. On sync, Central merges every device's entity list into one canonical dataset and can flag
   (not necessarily block, since the specimen is already collected and irreversible by then)
   any label that two different devices both created — the only case a single device's local
   Entities list can never see by itself, since two tablets that never sync cannot know about each
   other's local state.

I did not implement Entities in the submitted XLSForm. The reason is the same standard applied to
the last-saved attempt above: I know the feature exists and roughly how its XLSForm-side columns
work, but I am not confident enough in the exact column syntax to add it without the ability to
test it against a real ODK Central/Collect instance, and an Entities declaration that fails to
compile or silently misbehaves would be worse than not claiming it. This is recorded as a
deliberate scope decision in `11_scope_and_omissions.md`, with Entities named as the concrete
upgrade path.

## The backstop that exists regardless of any in-form check

The operating conditions already state the laboratory reconciles specimens against form data, and
discards any specimen it cannot match to a child record. A duplicate label reaching the lab —
whether from the same device or two different ones — surfaces there as a reconciliation failure
requiring the child to be revisited, which is the authoritative, always-present backstop
independent of anything implemented in the form. The form-side checks above exist to reduce how
often that expensive revisit path is triggered, not to replace it.
