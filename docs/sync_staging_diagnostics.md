# Investigating a waiting staging sync without SSH

Deploy the Compiler changes and restart its web application, sync worker and
Celery beat. This change needs no database migration. The worker must consume
`datasync` and use the same broker and database as the web application.

Open an existing Bulk sync request and select **Check sync diagnostics**.
Operators need the existing permission to add bulk sync runs; request ownership
and partner access still apply. The check sends no records and creates no runs.

The report checks the web sync switch, connection to the broker, worker replies
on `datasync`, whether the worker loaded the current sync tasks, and an authenticated
GET to the NFE API. Connection waits are bounded. Passwords, service tokens, URL
credentials and query parameters are excluded from displayed diagnostics.

A responding worker does not establish that a particular run has been processed,
that the worker's own sync switch is enabled, or that Celery beat is running.
Missing replies are inconclusive if remote control is disabled or workers are busy.
Filesystem/local demo brokers do not support the Redis/AMQP worker inspection.

For a waiting request, **Retry queue notification** wakes the existing outbox
sweep. It retains the request ID, partner, round and categories. It never prepares
records or calls the receiver in the web request. A successful notification means
the broker accepted it; refresh to establish actual worker progress. Preparation
continues to use the existing transaction and duplicate-prevention rules.

If publication fails, the sanitized error is saved on the waiting request, so
it remains available after the live log window has passed. The periodic sweep
can still recover it later. If the broker accepts the notification but no worker
consumes it, the request remains waiting; the diagnostic report is the next check.

An old `503 Service Unavailable` delivery error describes the receiver response
at that time. It does not establish the receiver's current state or explain a
new request whose events have not yet been prepared.

## Verification on 2026-10-28

All 173 Compiler sync tests passed, including 23 diagnostic and portal checks.
Live local browser testing reproduced a request remaining at `0/0` while the web
apps and broker were available and the worker was stopped. Diagnostics and a
retry notification created no extra runs or record events. After restoring the
worker, the same request completed `1/1`, with one event and one target round.
An unavailable receiver was also reported in the browser, and a new check
reported its recovery. These local checks do not establish the Azure staging
worker, broker, scheduler or receiver configuration.
