# Photo branch integration into Compiler sync

Source: `claude/photo-exports-neuro` at `1e53f002b679970827dcbc49320dfdbb48e76f6b`.
Destination: `claude/compiler-bma-nfe-sync-ike6uq`.

The complete source branch was merged with both histories retained. The source
branch was not edited. The pre-merge sync tip is retained in
`codex/backup-sync-before-photo-merge-20261101` (`a9006a45`). BMA-NFE code and
storage configuration were not changed by this integration.

## Compatibility changes

- Keep `datasync`, `wellbeing` and `figures` installed together.
- Use the incoming `Registration.profile_picture` first, then the linked legacy
  `Student.std_image`. Select one deterministic Makani photo per shared child.
  Record explicit clears so they do not restore a legacy photo on the next sync.
- Keep photo transport in registration events, using the existing hashing,
  verification, reusable HTTP connections and bounded parallel uploads.
  Update the photo audit/backfill to recognize both sources and deduplicate
  shared child IDs. That audit does not queue photo removals.
- Map incoming `Referral.public_school` to the existing `referred_school` wire
  reference by CERD and name. Source PublicSchool primary keys are never used
  as NFE School primary keys. A missing public school is sent as an empty
  reference. No replacement value is invented for the removed
  `referred_formal_education` field; existing NFE values remain untouched.
- Load TLS cycle filter choices at form use rather than querying during import.
- Add follow-up migrations for the photo clear marker, Packages TLS choice,
  Outreach Child country of birth and Student Teacher country of birth. Existing
  incoming migration files are unchanged.

The NFE contract remains unchanged. Compiler-only fields, including newly added
birth, youth, retention and transition fields without NFE columns, are not stored
in NFE. Wellbeing, figures, TLS and other additional source modules are not added
to replication. Existing documented contract exclusions continue to apply.

## Verification on 1 November 2026

Verification used the original two checkouts, isolated PostgreSQL databases,
local files and a local receiver. No Azure data was modified by these checks.

- Compiler regression suite: 410 tests passed, plus 429 subtests; the photo
  compatibility suite was then expanded and all 20 tests passed.
- Attendance API suite: 6 tests passed in a separate process because its legacy
  test module replaces database settings during import.
- NFE receiver sync suite: 172 tests passed, including photo failure rollback,
  storage validation, identity, relationship boundaries and replay handling.
- Real migration graph: no conflicting leaves or model-state differences.
- The four follow-up migrations applied to populated minimal tables in a private
  PostgreSQL schema. Existing rows and a photo reference were preserved. This
  is a targeted operation check, not a replay of the entire historical schema.
- Browser: three complete all-category runs each delivered 19/19 events. NFE
  generated IDs from 100 while source IDs started at 1; all relationships resolved
  correctly. The receiver retained exactly the same 23 source mappings.
- First bulk copied 3,682 photo bytes (new registration and legacy Student
  images). Repeating it uploaded zero photo bytes. A repeat after explicit clear
  also uploaded zero photo bytes and did not restore the legacy image.
- Browser photo form: replace, clear, repeat-after-clear and upload-after-clear
  all updated the same NFE child. File SHA-256 checks matched the source image.
- TLS registration/image excluded. Empty image, ProgramStaff centre relationship,
  attendance child links and public-school CERD mapping checked against NFE.

## Deployment requirements and limits

Run migrations as part of deployment. The incoming source branch intentionally
removes old Compiler Referral fields in migrations 0101 and 0102:
`referred_formal_education`, `cerd_number`, `formal_education_school_type` and
`referred_school`. Back up the database and retain any old referral values needed
for transition before those migrations run. This merge does not automatically
convert those deleted historical fields into PublicSchool relationships.

Compiler keeps the incoming Django `STORAGES` Azure fix and media container/signed
URL configuration. Existing local media can be handled by the incoming
`upload_media_to_storage` command; start with its dry run. Nothing in this merge
moves existing media automatically.

NFE's deployed file share still needs a real readable/writable mount and media
serving configuration. A receiver error saying "Photo storage unavailable" is
not resolved by Compiler's Azure storage fix. Verify the deployed NFE share with
`datasync_photo_storage_check --require-share --write-test` and a staging photo
sync. Local success does not establish that the Azure/VM mount is configured.

The separately requested hardcoded SIT URL/token override is retained. Restore
environment-based receiver settings before production; no token value is
included in this document. The merge does not deploy either project.
