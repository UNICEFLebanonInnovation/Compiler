# Start one bulk sync

1. Choose a partner and one or more categories.
2. Choose a round for round-based categories. Centres and ProgramStaff teachers
   include all rounds for the selected partner.
3. Click **Start sync**. The page shows progress and any error.

There is no preview step or list for adding multiple queued requests. The web
request saves the selection without counting source records, reading attendance
children or opening photos. The existing worker prepares and delivers it through
the same record and photo sync pipeline.

Only one unfinished bulk job can run across all users. PostgreSQL serializes
admission, so double clicks, different tabs and simultaneous users cannot add
overlapping jobs. An identical request ID returns its existing job. Old saved
requests are retained and processed one at a time; they are not silently deleted.
Ordinary single-record saves continue through their existing sync path.

**Retry sync** continues the same job and brings retryable failures forward;
it does not create a second set of events. **Stop sync** prevents new delivery
attempts and preserves source records, NFE records already received, and the
audit history. An upload already in progress may finish. A new bulk job cannot
start until such in-flight deliveries finish or release their locks. A later
sweep cleans up stopped events if a worker disconnects.

Completed jobs, terminal validation failures and stopped jobs release the slot.
Retryable receiver failures keep the current slot until recovery or Stop. The
page shows the failure and offers Retry/Stop. Previous syncs remain available in
a collapsed, read-only history.

## Deployment

Run the normal migrations and restart the Compiler web, Celery worker and beat
processes together. Migration `datasync.0010_bulk_sync_stopped` updates only the
model's choice labels and adds the Stopped choice; it executes no schema-changing
SQL. Existing data and outbox entries are retained.

Background delivery still requires the worker and message broker. Removing the
preview does not replace those services. The existing Procfile includes the
datasync worker queue and scheduler. NFE, the wire contract, Compiler Azure
storage and NFE file-share configuration are unchanged.
