# Remove pending bulk syncs

Large-round validation runs before the request's write lock is taken. A waiting
request can therefore be removed while that validation is running, including a
request saved on an earlier day. The worker rechecks that the request still
exists and is waiting before it writes any queue rows. Two workers validating
the same request cannot both create its outbox set.

During the atomic queue-write phase, removal keeps a locked request. The page
now explains that it was kept and asks the operator to refresh status; it does
not display a green "Removed 0" success message.

In **Data replication → Bulk sync**, select a partner. Under **Recent bulk
requests**, select **Remove pending bulk syncs**. The confirmation lists the
exact requests, including their rounds, categories and IDs. Confirm removal or
select **Keep requests** to leave them saved.

This removes only requests in **Waiting to queue** with no events and no queued
counts. It permanently removes those request records from bulk history. Source
entities and NFE records are preserved. Queued, failed-preparation, delivered
and partially processed requests retain their audit records.

Operators need the existing bulk-view and bulk-start permissions and can remove
their own waiting requests for an accessible partner. Superusers can manage
waiting requests across operators for the selected partner. There is no global
cross-partner removal action.

The confirmation is signed, operator/partner-specific and valid for 15 minutes.
Requests created after the review are preserved. State and ownership are checked
again under the same database row locks used by the worker. Busy requests are
skipped; a removed request cannot subsequently be prepared by a queued sweep.

Deploy the Compiler update and restart its web application. No schema migration
is needed for this button.

Validation on 2026-10-28: all 193 Compiler sync tests passed, including 20
removal checks covering confirmation, ownership, partner changes, CSRF,
expiration, new requests after review, replay, and races with preparation.
The browser preview used a separate disposable test database and verified
the selected-partner button, the two-request confirmation, and Keep requests.
