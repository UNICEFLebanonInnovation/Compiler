# Bulk sync verification — 29 October 2026

Passed in isolated local Compiler and BMA-NFE environments using the original application code, real HTTP requests, PostgreSQL and three Celery workers.

The load test exposed attendance requests exceeding the 30-second HTTP timeout. Compiler now sends at most ten complete attendance days per request by default. NFE resolves registrations in one query and inserts/updates attendance child rows in SQL batches, keeping existing row IDs and event-level rollback.

It also exposed repeated outbox scans while identifying the active job in a large completed history. The selector now obtains outstanding job IDs in one indexed pass. The measured query improved from about 424 ms to 1.3 ms without a migration.

| Test data / coverage | Result |
| --- | --- |
| Synthetic source rows | 81,772 |
| Compiler accounts / partners | 21 / 4 |
| NFE role accounts plus admin | 8 + 1 |
| Large operator batches | 12 × 4,209 = 50,508 events |
| Eligible registrations / children | 6,400 / 6,400 |
| Centres / ProgramStaff teachers | 32 / 320 |
| Service, assessment, grading and referral rows | 25,600 |
| Attendance days / child rows | 960 / 38,400 |
| Eligible photos checked by SHA-256 | 1,600 |
| Excluded TLS / unknown registrations | 960 |
| Excluded TLS / unknown photos | 32 |
| Final contract values and references compared | 790,601 |
| Automated regression tests | 438 (228 + 172 + 38) passed |
| Normal completed-run peak concurrent requests | 4 |
| Normal completed-run longest receiver request | 8.192 seconds |

## Large batches

| Actor | Round | Events | Seconds | Photo bytes |
| --- | --- | ---: | ---: | ---: |
| load_p1_op1 | 1 | 4,209 | 314.3 | 149,722 |
| load_p1_op2 | 2 | 4,209 | 179.6 | 163,306 |
| load_p1_op3 | 1 | 4,209 | 186.2 | 0 |
| load_p2_op1 | 1 | 4,209 | 212.9 | 151,359 |
| load_p2_op2 | 2 | 4,209 | 228.6 | 169,362 |
| load_p2_op3 | 1 | 4,209 | 239.0 | 0 |
| load_p3_op1 | 1 | 4,209 | 216.2 | 148,057 |
| load_p3_op2 | 2 | 4,209 | 354.1 | 164,658 |
| load_p3_op3 | 1 | 4,209 | 223.1 | 0 |
| load_p4_op1 | 1 | 4,209 | 288.7 | 149,531 |
| load_p4_op2 | 2 | 4,209 | 304.7 | 169,040 |
| load_p4_op3 | 1 | 4,209 | 407.7 | 0 |

The first batch includes attendance timeout/retry recovery before the fix. The second resumes the saved job after a worker restart and includes an injected receiver outage. The other ten batches completed with one attempt per event. Timings include deliberate interventions and are not a production benchmark. All four third-operator repeat batches uploaded zero image bytes. The history-query optimization was then exercised by the saved repair job and the large-photo recovery/repeat jobs against the full event history.

## Verified scenarios

- Ten admission races, each with twelve simultaneous operators: exactly one job admitted. Replaying each winning form five times reused its UUID. Five races were repeated after the history-query fix against the full 58,219-event outbox, without adding any sync events.
- Seventy-two forged cross-partner starts blocked across the two full matrices. Other operators could not view, retry or stop the winning job. Viewers could not start jobs; missing CSRF, invalid category, invalid round and invalid UUID were rejected.
- Receiver outage and worker restart: saved job resumed, event count stayed unchanged, and receiver identities remained unique.
- Stop during live large delivery: in-flight requests settled, remaining events stopped, repeated Stop was harmless, and another user could start. Source and receiver records were preserved.
- Wrong source centre/partner relationship failed preparation before any event was sent. Repair and Retry completed the same job.
- File-share outage rolled back child and photo together. Restore and Retry replaced 100 changed 640×480 JPEGs (27597252 bytes of image content). A local NFE child edit was overwritten and reported.
- One missing receiver photo triggered exactly one replacement upload. Repeating the large-image batch uploaded zero image bytes.
- Eight real non-staff NFE roles checked partner/centre teacher boundaries, ministry access, unassigned scope and missing-role denial.
- Two sets of 72 concurrent authenticated admin reads passed while delivery was active, including an outbox above 25,000 events.
- Browser checks covered a partner operator, viewer and administrator, completed 4,209/4,209 status, the NFE teacher portal and a fetched child image.
- A new round containing Arabic text was created through the ordinary admin during a large job and synced automatically.
- All final receiver BMA-ID sets, registration foreign keys, attendance values, photo hashes and stable local entity IDs were checked. The approved 11 contract exclusions remain.
- A 2,000-child single attendance day was tested for create, overwrite, removal, preserved row IDs and full rollback on a bad final row or duplicate registration.

## Deployment

Deploy the attendance fixes in both repositories and restart their web/sync worker processes. The new attendance change requires no migration. `DATASYNC_ATTENDANCE_BATCH_SIZE` defaults to `10` and is capped by `DATASYNC_BATCH_SIZE`.

These checks use isolated local databases, broker and media folders. Compiler Azure storage configuration was not changed. This does not verify Azure worker startup, Azure networking or the VM file-share mount; run one staging batch after deployment to verify those environment settings.

This is broad test coverage, not a claim that every possible input or deployment condition can be exhausted.
