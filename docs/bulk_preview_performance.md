# Bulk preview and waiting-request recovery

The attendance preview previously built global `NOT IN` subqueries over all
attendance children. Large data sets could exceed PostgreSQL's working memory
and rescan materialized results until Gunicorn timed out. Attendance eligibility
now uses correlated `EXISTS` checks through the indexed attendance-day foreign
key. Registration and centre dependencies avoid redundant subqueries when the
whole category is already selected. Pagination reuses the category counts.

Preview queries share a five-second database budget, including database lock
waits. A cancelled query rolls back its preview transaction and renders a useful
message without creating a bulk request or events. The caller's database timeout
is restored. Queue notifications have the same protection. Worker validation
has a twenty-second budget and runs before the request's queue-write lock.

A waiting request can be removed while validation reads are in progress. The
worker rechecks its existence, state and selection under a lock before writing
the outbox, preserving atomic preparation and preventing duplicate events from
concurrent workers. Once queue rows are being written, removal keeps a busy
request and explains why instead of reporting a green zero-removed success.

## Deployment

Deploy the Compiler code and restart its web and Celery worker processes so old
workers release any transactions held by the earlier implementation. No new
database migration is required. Existing waiting requests can then be removed
or processed normally. This change does not modify the receiver contract or
either project's media storage configuration.

## Verification

- Reproduced the old attendance query timeout with 2,001 selected days, 60,000
  unrelated TLS attendance rows, and constrained PostgreSQL working memory.
- Reproduced the old zero-removed outcome while yesterday's request was locked
  during validation.
- All 204 Compiler sync tests pass, covering eligibility, scoping, outbox
  atomicity, photo handling, concurrent preparation, cancellation, permissions,
  signed confirmation and timeout recovery.
- A separate disposable live-server database verifies real HTTP confirmation
  during paused validation, large previews and pagination. The large preview
  took approximately 0.29 seconds on the local test machine; staging timings
  depend on its data and infrastructure.
- Browser checks cover large preview, next page, multiple categories, removal
  review/Keep requests, and a useful response under a real exclusive database
  table lock. The preview recovers after the lock is released.
