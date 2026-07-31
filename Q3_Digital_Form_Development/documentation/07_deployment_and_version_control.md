# Deployment and version control for 120 enumerators, offline up to 9 days

Q3 requirement 10.

## Baseline mechanism

- **`form_id` is fixed**: `hh2026_v1`. This never changes for the round; it is what ties every
  submission, regardless of which edit of the form produced it, back to the same dataset.
- **`version`** (`settings` sheet, currently `2026073100`) changes on every published edit. I used
  a sortable `YYYYMMDDNN` string rather than a bare integer so the version itself is
  human-readable evidence of *when* a change went out, useful when reconciling a field report
  against the release timeline without cross-referencing a separate change log.
- Every submission ODK Central receives carries the exact `formVersion` it was filled under, as a
  normal system attribute of the submission — **this is not something I had to add**; it is how
  Central already distinguishes which edit of the form produced which record. `10_codebook.md`
  documents this attribute as a primary-key-adjacent field the analysis team should always keep.

## Why a mid-round change cannot lose or corrupt data already collected

This is a property of how ODK Collect binds a saved instance to a form version, not something
this XLSForm has to implement:

1. Every instance (draft or finalized-but-not-yet-submitted) that an enumerator has already
   started is saved locally bound to the exact form version it was opened under. Downloading a
   new form version onto the device does **not** touch, migrate, or invalidate in-flight drafts of
   the old version — a household interview started on Monday under version `...01` continues to
   open, edit, and finalize under `...01` even if the device downloads `...02` on Wednesday.
2. Only *new* instances started after the update use the new version. There is no in-place
   schema migration of already-collected data, so there is nothing for a mid-round change to
   corrupt.
3. Consequently, at any point in the round, submissions in Central can legitimately carry a mix of
   form versions — this is expected, not an anomaly, and `10_codebook.md`'s advice to always
   retain `formVersion` in every analysis extract is what lets the analysis team split or pool
   across versions deliberately rather than by accident.

## Publishing a mid-round change safely

1. Edit `scripts/build_form.py` (not the `.xlsx` by hand — keeps the constraint register and the
   form in sync, see the header comment in that script), bump `version`, rebuild, and reconvert
   (`documentation` folder's own conversion log shows the exact command).
2. Publish the new version to ODK Central as a **draft** first, and pilot it with one team (one
   supervisor + up to 5 devices) for at least one working day before promoting it to the
   production form used by all 24 teams. This is the practical mitigation for exactly the kind of
   change the operating conditions say is likely mid-round ("it has happened in every previous
   round") — catching a broken constraint or a mistyped choice list on 5 devices is recoverable in
   a way that catching it on 120 devices, several days offline, is not.
3. Promote to production once the pilot day's submissions look correct in Central.

## How the change actually reaches 120 devices that are offline for up to 9 days

Devices only pick up a new form version when they have connectivity to Central. Given the stated
condition (up to 9 consecutive offline days), I assume — this is a judgement call, not stated in
the data pack — that teams have periodic connectivity windows (e.g. returning to a ward or LGA
hub to charge devices, hand off specimens for the cold chain, and report to a supervisor), and
recommend those windows double as scheduled sync checkpoints. Under this assumption, a form update
published mid-round will reach different teams on different days as each team's own sync window
comes around — **staggered adoption is the expected outcome, not a fault condition**, and is
exactly what the `formVersion` attribute lets the analysis team account for rather than be
surprised by.

## Live test deployment: self-hosted ODK Central

To validate this form on its actual target platform rather than a bare converter or shared
hosting, the candidate provisioned a production-ready self-hosted ODK Central instance. In the
candidate's own words:

> We deployed a production-ready ODK Central instance on the IDDSL ARM64 Oracle Cloud VM using
> Docker Compose, integrated with the existing platform architecture. The deployment included
> cloning the ODK Central repository with all required Git submodules, configuring the environment
> for `odk.iddsl.com.ng` behind an existing Cloudflare Tunnel (SSL upstream mode), building ARM64-
> compatible images, resolving legacy PostgreSQL upgrade checks, initializing the database,
> starting all required services, and creating and promoting the initial system administrator
> account. The deployment was carefully validated at each stage using Docker health checks, service
> logs, and HTTP endpoint verification.
>
> Following the application deployment, we completed end-to-end infrastructure validation by
> extending the existing Cloudflare Tunnel configuration to expose the ODK service, verifying
> public HTTPS access, and troubleshooting a VM-specific DNS resolution issue. Investigation showed
> the problem was not with Cloudflare or ODK but with a stale negative cache in `systemd-resolved`;
> flushing the resolver cache restored correct hostname resolution. Final verification confirmed
> successful DNS resolution, HTTPS connectivity (`HTTP/2 200 OK`), and full operational availability
> of ODK Central at `https://odk.iddsl.com.ng`, fully integrated into the IDDSL platform stack.

This is infrastructure work the candidate carried out independently, not generated by or verified
through this AI-assisted build process — recorded here as part of the deployment record because it
is the environment `form/HH2026_v1.xlsx` version `2026073100` was actually uploaded to and tested
against, per `documentation/11_scope_and_omissions.md`, item 9.

## What the analysis team needs, concretely

- Always export `formVersion` alongside every record; never assume a single-version dataset for a
  14-day round.
- If a mid-round change altered a variable's meaning, range, or coding (rather than only adding a
  validation rule), `10_codebook.md`'s variable table should carry a "valid from version" note so
  a version-blind pooled analysis is not run on that variable inadvertently. No such
  meaning-changing edit is included in this submission (all v1 constraints tighten validity, none
  redefine a code), so this note applies to future rounds' changes, not to the current build.
