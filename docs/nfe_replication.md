# Replicating MSCC data to BMA-NFE

Partners using the Compiler's MSCC module should not have to key the same
registration into BMA-NFE as well. This integration copies MSCC records there
automatically, as they are saved.

The channel is **one-way**: the Compiler is the system of record, BMA-NFE
holds a replica, and nothing is ever read back.

## What is replicated

| Compiler model | Resource name | BMA-NFE model |
| --- | --- | --- |
| `mscc.Round` | `mscc.round` | `mscc.Round` |
| `locations.Center` | `locations.center` | `locations.Center` |
| `students.Teacher` | `mscc.teacher` | `mscc.Teacher` |
| `mscc.Registration` (with its `child.Child`) | `mscc.registration` | `mscc.Registration` |
| `mscc.EducationService` (child education situation) | `mscc.education_service` | `mscc.EducationService` |
| `mscc.EducationProgrammeAssessment` (grading) | `mscc.education_grading` | `mscc.EducationProgrammeAssessment` |
| `mscc.Referral` | `mscc.referral` | `mscc.Referral` |
| `attendances.MSCCAttendance` (+ `MSCCAttendanceChild`) | `attendances.mscc_attendance` | the same pair |

Scope is the whole MSCC module: every record, every partner, every round.

## How it works

Change capture is on the **models**, not the views, so every path that writes
a replicated record is covered — the MSCC forms, the Django admin, the import
tools, management commands.

1. A `post_save` / `post_delete` receiver writes a `datasync.SyncEvent` row in
   the same transaction as the change.
2. On commit, a Celery task (`datasync.deliver_sync_event`) pushes the record
   to BMA-NFE. If the broker is down the push runs inline in the web process
   instead, so the record still lands as the partner presses save.
3. `datasync.flush_sync_outbox` runs on Celery beat every five minutes and
   re-sends anything that failed.

The payload is built **at delivery time**, not at save time. Three
consequences worth knowing:

* a burst of edits to one record collapses into a single push;
* what arrives is always the record's latest state;
* an event whose record was deleted before delivery is abandoned, because the
  matching delete event carries the removal.

Deletes are the exception — there is nothing left to read — so they carry only
the resource and the id.

Related-table changes republish their parent: editing a `Child` republishes
every registration that carries it, an attendance row republishes its day, and
changing a teacher's training topics republishes the teacher.

## No shared primary keys

The two databases were never seeded together, so nothing crosses the wire as a
local id. Relations travel as natural keys — a round's name, a centre's
P-code, a school's CERD number, a child's UNICEF unique id — and BMA-NFE
resolves them into its own rows. See `docs/compiler_replication.md` in the
BMA-NFE repository for the resolution table and the full wire contract.

## Setup

1. **On BMA-NFE**, create the service account and copy its token:

   ```
   python manage.py datasync_create_client
   ```

2. **Here**, set the environment and switch it on:

   ```
   DATASYNC_ENABLED=True
   DATASYNC_TARGET_URL=https://<bma-nfe-host>/api/sync/events/
   DATASYNC_TARGET_TOKEN=<the token printed above>
   ```

   `DATASYNC_ENABLED` defaults to **off**, so an unconfigured deployment never
   queues events it cannot deliver.

3. Run the migration and confirm the link:

   ```
   python manage.py migrate datasync
   python manage.py datasync_status
   ```

4. Map schools to centres for teacher replication (see *Teachers* below), in
   **Data replication → School to centre links**.

5. Seed BMA-NFE with everything that already exists:

   ```
   python manage.py datasync_backfill
   ```

   Records are queued in dependency order — rounds and centres first — so a
   BMA-NFE database can be built from empty. Use `--dry-run` first to see the
   volume, `--resource` to do one resource at a time, and `--no-send` to fill
   the outbox and leave delivery to the sweep.

### Celery

Replication tasks use their own `datasync` queue. The `worker` process
consumes it alongside `default`; split it into its own process if you would
rather isolate it:

```
celery -A student_registration.taskapp.celery worker -Q datasync --loglevel=info
```

`beater` must be running for the retry sweep.

### Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `DATASYNC_ENABLED` | `False` | Master switch |
| `DATASYNC_TARGET_URL` | *(empty)* | BMA-NFE's `/api/sync/events/` |
| `DATASYNC_TARGET_TOKEN` | *(empty)* | Its service account token |
| `DATASYNC_TIMEOUT` | `30` | Request timeout, seconds |
| `DATASYNC_BATCH_SIZE` | `100` | Events per request |
| `DATASYNC_RETRY_DELAY` | `60` | First retry delay; doubles each failure |
| `DATASYNC_MAX_RETRY_DELAY` | `3600` | Cap on the backoff |
| `DATASYNC_MAX_ATTEMPTS` | `12` | Tries before an event is parked |
| `DATASYNC_SWEEP_SECONDS` | `300` | Retry sweep interval |
| `DATASYNC_INLINE_FALLBACK` | `True` | Send in-process when the broker is down |
| `DATASYNC_VERIFY_TLS` | `True` | Leave on |

## Operating it

`python manage.py datasync_status` gives the outbox breakdown and checks
connectivity in one go.

**Data replication → Sync events** in the admin shows every event, its status,
attempt count and the reply from BMA-NFE. Filter by `failed` or `abandoned` to
see what is stuck. Once the cause is fixed — an expired token, a firewall
rule, a missing centre — select the events and use **Send selected events
again**.

Turning `DATASYNC_ENABLED` off stops capture and delivery; anything already in
the outbox stays there and drains when it is switched back on.

Two fields are worth watching on a sent event: `conflict` means the update
overwrote something a BMA-NFE user had edited (BMA-NFE logs the detail), and
`ignored_fields` lists columns BMA-NFE does not store.

## Teachers

This is the one mapping that is not one-to-one, and it needs a human decision
per school.

The Compiler stores teachers as `students.Teacher`, tied to a **school** and a
`CLMRound` — a Dirasa concept. BMA-NFE stores them as `mscc.Teacher`, tied to
a **centre** and an MSCC round. Nothing in either schema connects a school to a
centre, so:

* **Set the centre yourself.** Fill in **Data replication → School to centre
  links**. Until a school appears there, its teachers replicate without a
  centre, which makes them of limited use on the BMA-NFE side.
* The Compiler translates what it can: the three birthday columns become a
  single `birthdate`, `teaching_hours_dirasa` becomes `teaching_hours_mscc`,
  and "Dirasa only" / "Private and Dirasa" become "Makani only" /
  "Private and Makani". The Dirasa round is matched by name against BMA-NFE's
  rounds.
* `years_of_experience` and `training_date_of_completion` have no source here
  and stay empty in BMA-NFE.
* Attachment **files** are not copied — only each attachment's description and
  type. The files stay in the Compiler.

## What is deliberately not sent

BMA-NFE runs a subset of this schema. Columns it does not have are reported
back in each event's `ignored_fields` rather than silently dropped, so the
loss is visible in the admin. Currently that means:

* `Registration.child_is_idp`, `Registration.consent`,
  `Registration.child_outreach`
* `EducationService.ppl_sector`
* `EducationProgrammeAssessment.mid_test`, `youth_pre_test`, `youth_post_test`
* `Center.active_during_emergency`, `is_tarl`, `is_tls`,
  `provide_french_language`
* `Round.start_date`, `Round.end_date`

Grading covers `EducationProgrammeAssessment` only. The Compiler's
`EducationProgrammeWLAssessment`, `EducationProgrammeSummerRSAssessment` and
`TarlAssessment` have no counterpart in BMA-NFE and are not replicated; that
would need those models to be added there first.
