# MSCC sync to BMA-NFE

The `datasync` app copies Compiler MSCC data to BMA-NFE so partners can enter
it once. Sync is **one-way**: Compiler owns the source records; changes in
BMA-NFE are never pulled back.

For the complete model coverage, field mappings, and receiver limitations,
see [the replication guide](../../docs/nfe_replication.md).

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

## Setup

Run Compiler commands below from the repository root in the application's
configured Python environment.

1. Deploy the compatible BMA-NFE receiver. On **BMA-NFE**, create its sync
   service account:

   ```bash
   python manage.py datasync_create_client
   ```

2. Configure **Compiler** using deployment environment variables. Store the
   token in the deployment's secret configuration.

   ```dotenv
   DATASYNC_ENABLED=True
   DATASYNC_TARGET_URL=https://<bma-nfe-host>/api/sync/events/
   DATASYNC_TARGET_TOKEN=<BMA-NFE service-account token>
   DATASYNC_DELIVERY_MODE=thread
   ```

   Sync defaults to disabled. Saves made while disabled are not captured;
   backfill existing records after enabling it.

3. Apply the outbox migration, restart application processes to load the
   configuration, and check the endpoint:

   ```bash
   python manage.py migrate datasync
   python manage.py datasync_status
   ```

   Confirm the target is reachable and reports ingest enabled.

4. In Django admin, open **Data replication → School to centre links** and
   map schools to centres for teacher replication. Teachers without a link
   are sent without a centre. Teacher fields are translated from the
   Compiler's Dirasa vocabulary to BMA-NFE's Makani vocabulary.

5. Run a Celery worker consuming `datasync` and run Celery beat for recovery
   sweeps:

   ```bash
   celery -A student_registration.taskapp.celery worker -Q default,datasync --loglevel=info
   celery -A student_registration.taskapp.celery beat --loglevel=info
   ```

   The branch's worker process already includes the `datasync` queue.

6. Preview and then send existing records:

   ```bash
   python manage.py datasync_backfill --dry-run
   python manage.py datasync_backfill
   python manage.py datasync_status
   ```

   Backfill queues resources in dependency order and flushes due outbox events,
   including previously queued work. Normal saves then sync automatically.

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
