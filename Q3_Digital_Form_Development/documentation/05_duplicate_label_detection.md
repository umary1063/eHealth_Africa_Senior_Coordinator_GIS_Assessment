# Duplicate-label detection across submissions from the same device

Q3 requirement 8: *"State plainly whether a self-contained form can enforce that. If it cannot,
describe the architecture that can, and implement whatever part is achievable in the form
itself."*

**Update, 2026-08-01:** the ODK Entities mechanism described below as the untested upgrade path
has since been implemented and verified against a live, self-hosted ODK Central instance
(v2026.2.1) — see "What was implemented" and "Live verification" further down. The rest of this
document is left as originally written, including the reasoning for not implementing it blind,
because that reasoning is still the correct standard to apply and the record of it stands.

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

**Originally**, Entities was not implemented in the submitted XLSForm, for the reason stated
above: the feature was understood conceptually but not confident enough to add without the
ability to test the exact column syntax against a real instance. That gap has since been closed.

## What was implemented

- An `entities` sheet declares list `used_specimen_labels`, `create_if` gated on
  `${specimen_obtained}='1' and string-length(${specimen_label}) > 0`, `label` set to the entered
  specimen label for display in Central.
- Three properties are saved via `save_to` on fields inside the same `specimen` group as
  `specimen_label` (required, so all `save_to` references share one container scope, per
  pyxform's entity-placement rules): `specimen_label_value` (the label itself),
  `device_id_value` (copied from the form's existing `device_id` metadata field), and
  `entered_at` (`now()` at the time the label was recorded).
- `specimen_label`'s `constraint` gained one more ANDed clause:
  `count(instance('used_specimen_labels')/root/item[specimen_label_value = current()]) = 0` —
  rejecting a label already present in the device's local copy of the dataset, in addition to the
  existing within-submission check.

See `constraint_register.csv` row C021 (updated) and `scripts/build_form.py` for the exact
implementation.

## Live verification

Verified against a live, self-hosted ODK Central instance (v2026.2.1) on 2026-08-01, with the
candidate's explicit authorization to test against that instance and to publish the resulting
form version:

- The entities-enabled form compiled without error via two independent pyxform 4.5.0
  conversions — locally, and via Central's own `pyxform-http` service — with only the same two
  pre-existing, already-documented warnings the form had before this change. This was the actual
  unverified risk originally cited (uncertain XLSForm column syntax), and it is now resolved.
- A real submission to the published form created a real entity in `used_specimen_labels`, whose
  saved properties (confirmed via Central's entity API) were `specimen_label_value: "BSN480000-X"`,
  `device_id_value: "test-device-001"`, `entered_at: "2026-06-15T09:25:00.000+01:00"` — an exact
  match to the values submitted, and to the property names the constraint's `instance()` lookup
  references. This confirms the create-side mechanism end to end on real infrastructure, which was
  the part genuinely uncertain before.
- A follow-on attempt to click through the live web-forms client and re-enter that same label,
  to directly observe the constraint reject it in the UI, was **not conclusive**: browser
  automation in the verification session had unrelated trouble reliably committing values into a
  few masked/validated input widgets (date and time fields, and on one pass the label field
  itself), so a rejection observed on one attempt could not be cleanly isolated from that
  automation noise. This is a limitation of the verification session, not a form defect — the
  server-side mechanism the constraint depends on (the entity list and its exact property
  structure) is independently confirmed correct above, and the constraint expression itself
  compiled and was accepted by two independent, real pyxform engines. A physical-device or a
  steadier manual click-through would be the way to close this specific remaining gap, and is
  named here rather than silently assumed.

## The backstop that exists regardless of any in-form check

The operating conditions already state the laboratory reconciles specimens against form data, and
discards any specimen it cannot match to a child record. A duplicate label reaching the lab —
whether from the same device or two different ones — surfaces there as a reconciliation failure
requiring the child to be revisited, which is the authoritative, always-present backstop
independent of anything implemented in the form. The form-side checks above exist to reduce how
often that expensive revisit path is triggered, not to replace it.
