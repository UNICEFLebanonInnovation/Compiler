# Bulk sync by partner

Current mapping and Makani-only rules: [Makani ProgramStaff sync](makani_program_staff_sync.md).

In Compiler admin, open **Data replication → Bulk sync**:

1. Choose a **Partner**. Every new request requires one partner; there is no All partners option.
2. Select one or more **Element categories**.
3. Choose an MSCC **Round** for registrations, education records, referrals,
   attendance, or the round category. Centres and teachers do not require a round.
4. Click **Preview records** and review the read-only category counts and records.
5. Click **Sync this selection**, then **Refresh status** to review delivery.

Selecting **All categories** means every supported category for the chosen
partner, with round-based records limited to the chosen round. It never means
all partners. Individual category selection still supports multiple checkboxes.

## Scope

| Category | Selection rule |
| --- | --- |
| Centres, including embedded partner | Centres belonging to the selected partner, across all rounds. |
| Teachers | Makani locations.ProgramStaff whose centre belongs to the selected partner, across all rounds. Staff has no round association. |
| Registrations, including child and photo | The selected partner and selected MSCC round. |
| Education services, assessments and grading | Registrations belonging to the selected partner and round. |
| Referrals | Registrations belonging to the selected partner and round. |
| Attendance, including child rows | Attendance days whose centre belongs to the selected partner and whose stored MSCC round matches the selection. |
| Round | Shared round metadata needed by the selection; it does not include another partner's registrations. |

Required supporting registrations and centres stay within the chosen partner.
Shared child identity and photo handling are unchanged. Partners continue to
travel embedded in centre/registration events; no second endpoint is used.

For teachers, the ProgramStaff centre determines the partner directly.
Dirasa students.Teacher and the old school-to-centre links are not sync sources.

Conflicting links block queue preparation. Examples include a registration
whose centre belongs to another partner, attendance carrying another partner's
registration, and an education service using a different round from its
registration. Attendance rows are never silently filtered from a day: the
whole day is sent consistently after its links are corrected. Mixed Makani/TLS
days are excluded until corrected; TLS registrations and dependent records
are excluded from every category.

## Delivery and duplicate prevention

A POST saves the partner, optional round, exact categories and requesting
operator in a durable request. The existing worker queues the current matching
records in bounded database batches. Queue preparation is locked and idempotent.
Repeated submission of the same form creates one request. A request UUID cannot
be reused for a different partner, round, category set or operator.

The dispatcher rechecks partner ownership and the operator's current partner
access before sending each bulk event. It also checks serialized centre and
attendance references. Records moved to another partner after queueing are
blocked before HTTP delivery and require a corrected/new request.

The existing outbox, dependency order, HTTP connection pools, bounded upload
parallelism and retry policy remain in use. Photos are still part of registration
delivery, with verified reuse to avoid uploading unchanged image bytes. Compiler's
Azure storage configuration is unchanged.

This selector scopes **bulk requests**. Ordinary individual record saves still
use the existing automatic change-capture pipeline.

## Permissions and history

Superusers may select any partner. Other staff need
`schools.view_partnerorganization` or `schools.change_partnerorganization`,
in addition to `datasync.view_bulksyncrun` and the source view/change permissions
for their selected and supporting categories. Starting requires
`datasync.add_bulksyncrun`.

A staff operator assigned to a partner or centre can select only the matching
partner. Saved-run access is checked against the operator's current assignments.
Staff see only their own authorized requests; superusers can inspect all requests.
Preview pagination, status and history retain the partner selection.

Centres/teachers-only operators do not need round permissions. Grant
`datasync.view_syncevent` and `datasync.change_syncevent` as appropriate for
delivery details and existing retry actions.

## Deployment

Deploy Compiler, run `python manage.py migrate`, and restart its web app,
Celery worker and beat. The worker must consume the existing `datasync` queue
and the periodic outbox sweep must remain scheduled. `DATASYNC_ENABLED`,
`DATASYNC_TARGET_URL` and `DATASYNC_TARGET_TOKEN` must be configured.

Migration `datasync.0008_bulk_sync_partner` adds the saved request's partner.
Earlier completed requests retain their audit history and are labelled
**All partners (legacy)**. Historical partnerless requests cannot prepare new
events or continue pending bulk delivery. Start a new request with an explicit
partner selection instead of retrying an old global request. Legacy history is
available to superusers; it is not exposed to partner-assigned staff.

No BMA-NFE schema or API change is required. Receiver storage, authentication,
idempotency, conflict auditing and photo reuse keep their existing contract.
Local integration tests do not verify deployed Azure or VM file-share connectivity.

## Local verification — 27 October 2026

**133 Compiler sync tests passed**, including 27 new partner-isolation checks. Coverage includes every category, shared-round metadata, supporting parents, missing mappings, cross-partner attendance, duplicate form submission, permissions, pagination, legacy requests, requester reassignment/revocation, and changes between queue preparation and delivery.

The actual `0008_bulk_sync_partner` operations were applied to the isolated local Compiler schema. The migration loader reported no model-state differences.

Two synthetic partners shared one round. The browser selected Partner A and All categories; its 11 events completed successfully. Database checks then proved that no Partner B partner, centre, teacher, child, registration, education, referral or attendance record had arrived in NFE. The other-round registration of Partner A was also excluded. A teacher without a round remained roundless, and another teacher retained its existing different-round metadata.

Seven end-to-end assertions passed using real admin HTTP forms, a real Celery worker, the existing receiver API, downloaded photo bytes and independent databases:

1. Browser Partner A run delivered its exact entity set and no Partner B records.
2. Centres and teachers include the selected partner across rounds; the other-round registration is excluded.
3. Two simultaneous submissions create one partner-scoped run; unchanged photos upload zero bytes.
4. Partner-only centres/teachers sync without a round and still exclude Partner B.
5. Explicit Partner B selection delivers its own records and photo without changing Partner A.
6. Assigned operator sees only Partner A; a forged Partner B POST cannot create a run.
7. Assigned operator can deliver its own partner successfully.

| Run | Sent events | Uploaded image bytes |
| --- | ---: | ---: |
| browser_a | 11 | 2085 |
| repeat_a | 11 | 0 |
| partner_masters_a | 4 | 0 |
| partner_b | 9 | 2269 |
| assigned_operator_a | 4 | 0 |

All 39 events from these five requests were Sent. No request contained duplicate resource/source-ID pairs. Repeated Partner A delivery reused existing NFE records and uploaded zero image bytes. Partner B was delivered only after a separate explicit Partner B selection; Partner A child and registration data stayed unchanged.

Manual browser checks:

1. Partner A preview excludes Partner B and the other-round registration.
2. Partner A browser request completed with 11/11 events.
3. Centres and teachers preview stays within Partner A and disables the round selector.
4. Partner-assigned operator dropdown offers only its own partner.
5. Assigned operator can preview all categories for its own partner.

The older local demo schema lacked the default bulk-run permissions for the restricted test account. Those local fixture permissions were created before repeating its successful checks. Application permission checks were retained. The synthetic operator was disabled after all its events were Sent, and the browser was restored to the local administrator.

Compiler Azure storage settings and all BMA-NFE code/settings were unchanged. The work is saved in the original Compiler clone on `claude/compiler-bma-nfe-sync-ike6uq`; no commits, pushes or deployments were performed.

![Partner selection and preview](images/partner-bulk-preview.jpg)

![Completed Partner A bulk sync](images/partner-bulk-completed.jpg)

![Partner-only masters without a round](images/partner-bulk-masters-preview.jpg)

![Assigned operator limited to its own partner](images/partner-bulk-assigned-operator.jpg)
