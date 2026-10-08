# MSCC sync to BMA-NFE

The `datasync` app copies Compiler MSCC data to BMA-NFE so partners can enter
it once. Sync is **one-way**: Compiler owns the source records; changes in
BMA-NFE are never pulled back.

For the complete model coverage, field mappings, and receiver limitations,
see [the replication guide](../../docs/nfe_replication.md).

## Changes introduced by this branch

Previously, partners had to enter Compiler MSCC data again in BMA-NFE.
This branch adds automatic outbound replication when supported records are
saved or deleted.

| Change | Purpose |
| --- | --- |
| New `student_registration.datasync` Django app | Registers model signal handlers and the sync components |
| `SyncEvent` model and migration | Stores queued events, attempts, retry times, receiver responses, and delivery status |
| `SchoolCenterLink` model and admin | Maps Compiler schools to centres for BMA-NFE teachers |
| Serializers and resource registry | Builds receiver payloads and translates relations and teacher fields |
| HTTP client and dispatcher | Authenticates to BMA-NFE, sends events, and records per-event results |
| Save/delete and related-object signal handlers | Captures supported changes and republishes registration or attendance aggregates |
| `datasync.deliver_sync_event` and `datasync.flush_sync_outbox` tasks | Provides Celery delivery and scheduled recovery |
| `datasync` Celery queue, routing, beat schedule, and worker configuration | Allows workers to consume sync work and retry due events |
| `DATASYNC_*` settings | Controls activation, endpoint, delivery mode, batching, and retries |
| `datasync_backfill` and `datasync_status` commands | Seeds existing data and reports connectivity and outbox health |
| Sync-event admin and requeue action | Lets operators inspect failures and retry corrected events |

This is the **sending side** of the integration. Deploying this Compiler
branch alone does not create the BMA-NFE receiver. The compatible ingest
endpoint, its authentication, receiver migrations, and required reference
data must be deployed in BMA-NFE separately.

## Sync process

1. Django model save/delete signals queue a `SyncEvent` in the outbox.
   Within a transaction, the event is written alongside the source change.
2. A `transaction.on_commit` callback schedules delivery after the change
   commits. A rolled-back transaction does not trigger delivery.
3. Delivery reads the current record, builds its payload, and posts it to
   BMA-NFE's `/api/sync/events/` endpoint with service-account token
   authentication. Delete events carry the resource and source ID with an
   empty payload.
4. BMA-NFE returns an outcome for each event. `applied` and `skipped`
   outcomes are marked `sent`; failures are deferred or abandoned.
5. Celery beat runs `datasync.flush_sync_outbox` every 300 seconds by default
   to retry due events and recover deliveries interrupted by process failures.

Pending upserts for the same resource and source ID are reused. Payloads are
built at delivery time, so queued edits send the current state rather than a
historical snapshot. Background delivery can still be pending when the
browser receives the save response. Replication errors do not roll back a
successful source save.

Source IDs identify Compiler records in the sync contract; they are not
assigned as BMA-NFE database primary keys. Related objects use natural keys
such as centre P-codes, round names, school CERD numbers, and child UNICEF IDs.

## What travels together

- Rounds, packages, centres, teachers, registrations, shared MSCC service,
  assessment, grading, referral, and follow-up tables are replicated.
- Child details, the services checklist, and education history are embedded
  in registration payloads. Checklist contents are replaced as a set.
- MSCC attendance days include their child attendance rows.
- Child edits republish registrations; attendance-row edits republish the
  attendance day; teacher training changes republish the teacher.

CLM/Dirasa attendance, administrative geography, and assessment models with
no BMA-NFE counterpart are outside this channel. Attachment files are not
transferred. See the linked guide for the full coverage table.

## Concerns before enabling sync

| Concern | Impact and action |
| --- | --- |
| Compiler is the source of truth | Replicated updates can overwrite edits made in BMA-NFE. Agree that replicated records are maintained in Compiler; inspect receiver conflict reports. |
| Scope includes every partner and round | Activation captures supported model changes across the deployment. The default backfill selects all records, not a partner-specific subset. Confirm that the target is the intended BMA-NFE environment. |
| Child and service data crosses systems | Payloads include child details and service history. Use HTTPS, keep the token in secret configuration, and verify receiver access is limited to the intended users. |
| Receiver compatibility and reference data | Missing natural-key matches or unsupported fields can cause rejection or partial representation. Check centre P-codes, round names, school numbers, child identifiers, and receiver contract support. |
| Teacher mapping is lossy | Map schools to centres before sending teachers. Birthday, assignment, and hours fields are translated; some destination fields have no source. Attachment files stay in Compiler. |
| Coverage is incomplete by design | Some assessment models and fields have no receiver counterpart. Review the full coverage guide and `ignored_fields`; a sent event does not mean every source field was stored. |
| Save success does not mean sync success | Thread and Celery delivery are asynchronous. Check the outbox and the corresponding BMA-NFE records rather than using the browser save response as confirmation. |
| Outages and process restarts | Background work can be interrupted. Keep the retry worker and beat running, monitor pending/failed counts, and investigate abandoned events. |
| Delivery order and duplicate attempts | The sweep/backfill orders resources by dependency, but separate save-time pushes can run concurrently. Do not assume exactly-once delivery; the receiver must handle repeated events and missing dependencies according to the contract. |
| Deletes propagate | Deleting a supported Compiler record queues a receiver delete. Backfill republishes existing records; it does not recreate delete events missed while capture was disabled. |
| Bulk writes can bypass capture | Signal-less updates, bulk operations, and direct SQL need explicit enqueueing or a suitable backfill. Capture failures can be logged without preventing the source save. |
| Backfill can be large | Preview counts first. Backfill reads record IDs and queues events; sending also flushes other due work. Plan database and receiver capacity, and monitor progress. |

Queued upserts represent the current state at delivery, not an audit history
of every edit. Normal sync does not perform a full comparison of the two
databases; validate representative records in BMA-NFE after the initial
backfill.

## How to start sending data to BMA-NFE

Run Compiler commands below from the repository root in the application's
configured Python environment.

The requested BMA-NFE target is
[https://leb-container-test-sector-api.azurewebsites.net/](https://leb-container-test-sector-api.azurewebsites.net/).
Compiler needs the full sync endpoint, not only the site's root URL:

```text
https://leb-container-test-sector-api.azurewebsites.net/api/sync/events/
```

This path follows the sync contract described in this repository. Verify that
the compatible receiver is deployed at this host with `datasync_status`
before sending. Adding the URL to this README does not update a running
deployment or send records; apply the environment configuration below and
complete the activation steps.

### 1. Prepare the BMA-NFE receiver

Deploy the compatible receiver and apply its migrations using the BMA-NFE
deployment procedure. Make sure its ingest endpoint is enabled and that
required administrative geography/reference data is available.

On **BMA-NFE**, create the sync service account:

```bash
python manage.py datasync_create_client
```

Keep the resulting token for Compiler's secret configuration. This command
belongs to BMA-NFE, not to this Compiler app.

### 2. Deploy Compiler and prepare its database

Deploy branch `claude/compiler-bma-nfe-sync-ike6uq` with the application's
normal dependencies and configuration. Keep sync disabled during preparation:

```dotenv
DATASYNC_ENABLED=False
DATASYNC_TARGET_URL=https://leb-container-test-sector-api.azurewebsites.net/api/sync/events/
DATASYNC_TARGET_TOKEN=<BMA-NFE service-account token>
DATASYNC_DELIVERY_MODE=thread
DATASYNC_VERIFY_TLS=True
```

Apply the Compiler outbox migration:

```bash
python manage.py migrate datasync
```

Restart application processes to load the deployed code and environment.
Sync defaults to disabled; records changed while disabled can be republished
with backfill after activation.

### 3. Verify connectivity and mappings before sending

```bash
python manage.py datasync_status
python manage.py datasync_backfill --dry-run
```

The status command checks connectivity even when Compiler capture is disabled.
Confirm that the URL is the intended environment, the receiver is reachable,
and it reports ingest enabled. The dry run reports counts without queueing
or sending records.

In Django admin, open **Data replication → School to centre links** and map
schools to centres. Teachers without a link are sent without a centre.
Verify natural-key reference data in both systems before the first send.

### 4. Start recovery processes and enable sync

Run a worker consuming `datasync` and Celery beat. Under the deployment's
process manager, the commands are:

```bash
celery -A student_registration.taskapp.celery worker -Q default,datasync --loglevel=info
celery -A student_registration.taskapp.celery beat --loglevel=info
```

The branch's worker process already includes the `datasync` queue. Use the
deployment's existing beat process rather than starting an additional scheduler.

Set `DATASYNC_ENABLED=True` in Compiler's deployment configuration and restart
web, worker, and beat processes so they all load the same settings.
**Supported saves and deletes now start sending automatically**; enabling
sync does not by itself queue all existing records.

### 5. Send the existing data

For a first check, send a small sample of parent resources:

```bash
python manage.py datasync_backfill --resource mscc.round --resource locations.center --limit 1
python manage.py datasync_status
```

This sends up to one record per selected resource; it is not a partner filter
and also flushes other due outbox events. Check those records in BMA-NFE.
For a fresh receiver, send all required parents before testing individual
registrations or services.

When ready to seed all supported existing data:

```bash
python manage.py datasync_backfill --dry-run
python manage.py datasync_backfill
python manage.py datasync_status
```

Backfill queues resources in dependency order and sends due events. If the
receiver is unavailable or dependencies fail, events may be deferred or
abandoned; inspect the command output and admin rather than treating command
completion as proof that every record arrived.

### 6. Verify normal use and monitor

Save a supported MSCC registration in Compiler. In **Data replication →
Sync events**, find its `mscc.registration` event by source ID and confirm it
becomes `sent`. Check the registration, child profile, services checklist,
and education history in BMA-NFE. Also verify representative service,
attendance, and mapped teacher records after backfill.

Continue using Compiler forms normally; there is no separate send button
required for each save. Monitor failed/abandoned events, conflicts,
`ignored_fields`, and capture errors in application logs.

If delivery must be paused, disable sync in the deployment configuration and
restart processes. This stops new capture and scheduled tasks after they load
the setting; already submitted or in-flight background deliveries may finish.
Outbox rows remain for later processing. Backfill current records after
re-enabling to cover updates made during the pause; missed deletions need
separate reconciliation.

## Delivery modes

| `DATASYNC_DELIVERY_MODE` | Behaviour |
| --- | --- |
| `thread` (default) | Pushes from a background pool in the application process after commit; the response does not wait for the HTTP request. |
| `inline` | Performs the push after commit before returning from the callback; adds the network round trip to save latency. Delivery failures still do not fail the save. |
| `celery` | Sends the event to a worker consuming `datasync`. If submitting to the broker fails, falls back to the application background pool. |

Every mode needs beat and a worker on the `datasync` queue for automatic retry
sweeps. Save-time delivery is separate from the sweep.

## Backfill options

```bash
# Preview a resource without writing or sending anything.
python manage.py datasync_backfill --dry-run --resource mscc.registration

# Queue at most ten records per selected resource and send due events.
python manage.py datasync_backfill --resource mscc.round --resource locations.center --limit 10

# Queue all existing records and leave sending to the scheduled sweep.
python manage.py datasync_backfill --no-send
```

`--resource` is repeatable; omit it to include all supported resources.
`--limit` applies per resource, with zero meaning unlimited. Outside a dry
run, backfill requires `DATASYNC_ENABLED=True`. For a fresh receiver, send
parents before selecting registrations or dependent service resources.

## Settings

| Setting | Default | Purpose |
| --- | --- | --- |
| `DATASYNC_ENABLED` | `False` | Enables normal change capture and scheduled tasks |
| `DATASYNC_TARGET_URL` | empty | BMA-NFE sync endpoint |
| `DATASYNC_TARGET_TOKEN` | empty | BMA-NFE service-account token |
| `DATASYNC_DELIVERY_MODE` | `thread` | Save-time delivery strategy |
| `DATASYNC_MAX_WORKERS` | `4` | Background delivery pool size |
| `DATASYNC_TIMEOUT` | `30` | HTTP timeout in seconds |
| `DATASYNC_VERIFY_TLS` | `True` | Verify the receiver's TLS certificate |
| `DATASYNC_BATCH_SIZE` | `100` | Maximum events per outgoing batch |
| `DATASYNC_SWEEP_SECONDS` | `300` | Beat retry interval in seconds |
| `DATASYNC_RETRY_DELAY` | `60` | Initial retry delay in seconds |
| `DATASYNC_MAX_RETRY_DELAY` | `3600` | Maximum retry delay in seconds |
| `DATASYNC_MAX_ATTEMPTS` | `12` | Attempt budget for retryable failures |

Retry delay doubles after each failure up to the configured cap. Receiver
rejections marked non-retryable are abandoned after at most three attempts
(or the configured attempt budget if smaller). An upsert whose source record
no longer exists is abandoned; a separate delete event represents its removal.

## Monitoring and recovery

```bash
python manage.py datasync_status
python manage.py datasync_status --no-ping
```

Status reports `pending`, `failed`, `abandoned`, and `sent` counts. The
default command also checks endpoint connectivity; `--no-ping` reports only
the local outbox.

In **Data replication → Sync events**, inspect `last_error`,
`remote_detail`, `attempts`, and `next_attempt`. A sent event can report
`conflict` (receiver edits were overwritten) or `ignored_fields` (columns
the receiver does not store).

| Symptom | Check |
| --- | --- |
| Not configured | Target URL and service-account token |
| Unreachable, authentication, or TLS errors | Endpoint, network access, token validity, and certificate trust |
| Pending events do not drain | Worker consumes `datasync`, beat is running, and sync is enabled |
| Missing dependencies or rejected payloads | Receiver error detail, prerequisite records, and compatible contract |
| Teachers appear without centres | School-to-centre links |

After fixing the cause, select affected events in the admin and choose
**Send selected events again**. This resets them to pending, clears the
attempt count/backoff/error, and leaves delivery to the next sweep.

Disabling sync stops new capture and scheduled tasks; it retains existing
outbox rows. Re-enable it to resume scheduled processing. Use backfill to
republish records changed while capture was disabled.

## Capture limitations for maintainers

Capture relies on Django signals. `QuerySet.update()`, `bulk_create()`,
bulk updates, and direct SQL do not generally emit model save signals.
The existing checklist service-save receiver covers its specific
`update_service` path; it is not generic bulk-change capture. New write paths
that bypass signals must explicitly enqueue changes or be followed by an
appropriate backfill. Raw fixture saves are skipped.

Capture failures are logged and swallowed to preserve source saves, so
monitor application logs for `datasync: could not queue` as well as monitoring
the outbox. An empty outbox alone does not prove that every write was captured.
