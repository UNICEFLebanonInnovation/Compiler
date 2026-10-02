# Makani child wellbeing — phase 1 (`student_registration.wellbeing`)

Rule-based flags on Makani children who may need a follow-up, the follow-up recorded on each flag,
and monthly centre summaries. No machine learning: every flag says in words why it was raised, and
a person decides what to do. A flag means "check on this child", never a label.

## Flags

Worked out every night for the registrations of the current round(s) (not deleted, not TLS), from
data the centres already record. Thresholds are in admin → Flag settings.

| Code | Flag | From | Default rule |
|---|---|---|---|
| A1 | Absent several class days in a row | daily attendance | 3 class days in a row, up to the latest one |
| A2 | Low attendance | daily attendance | under 70 % of class days in the last 28 days (at least 8 days) |
| A3 | Attendance dropped | daily attendance | 30 points lower in the last 14 days than in the 28 before |
| S1 | Required service not received | service checklist | a required service not completed 6 weeks after joining the round (core package) |
| D1 | Dropout without follow-up | referral, inclusion, youth kit | dropout recorded and no follow-up recorded |
| H1 | Malnutrition screened, not referred | health & nutrition | MAM/SAM screening, no malnutrition referral (SAM is urgent) |
| H2 | Developmental delay, not referred | health & nutrition | a delay identified, no referral |
| P1 | Protection concern, not referred | PSS | a concern recorded, no CP referral or CP follow-up (suicidal ideation is urgent) |
| L1 | No learning progress | TaRL, World Learning BLN, Summer RS tests | no subject better at the latest test than at the first |

- **Attendance sheets with every child present** (at least 5 children) are left out: the form fills
  "present" in advance, so such a sheet may not have been filled in. They count neither as present
  nor as absent, and the centre summary shows how many there are.
- Children recorded as having **left the programme** get no flag but D1.
- **Priority** (shown next to a flag, never a flag on its own): the child works, lives without
  parents (unaccompanied, separated, child-headed household) or has a disability.
- A protection concern follows the child protection referral procedure straight away; P1 only
  shows that no referral is recorded.
- Not in phase 1: the main programme assessment (raw form data, unvalidated scores; a missing test
  can look like a 0) and anything predictive.

## BMA calculates, NeuroDB shows

BMA has no page for this: it works out the flags and summaries and serves them through an API that
only the NeuroDB service account (group "NeuroDB API", token authentication) can call. NeuroDB
shows them and records the follow-ups (UNICEF administrators and section editors).

- `GET /api/wellbeing/flags/?modified_since=<ISO date-time>&after=<id>&limit=<n>`: flags in id
  order, `next_after` for the next page; with `modified_since`, only the flags changed since then.
  Each flag carries the BMA **registration number**, the centre, partner and round, and the child's
  gender, age band and nationality: no name, contact detail or date of birth. `bma_path` is the
  child's profile in BMA, opened with the user's own BMA access. The response also has the flag
  kinds, follow-up results and thresholds.
- `POST /api/wellbeing/flags/<id>/follow-up/` with `follow_up_type`, `result` (one of the
  results), `followed_up_on`, `note` and `by` (the NeuroDB user's name): the flag closes (409 when
  it is no longer open). It opens again only when newer data shows the problem continues (e.g. new
  absences after the follow-up date, a new PSS record); a flag whose condition clears by itself
  closes as "resolved by itself".
- `GET /api/wellbeing/summaries/?month=YYYY-MM-01`: the centre summaries of a month (latest by
  default) and the months available. Per centre: children, dropouts, attendance rate, children with
  an open flag, flags raised and followed up within 7 days, median days to follow-up, flags open
  past 7 days, required services completed, learning tests compared, and data quality
  (all-present sheets, core-package children without a service checklist). Counts only.

## Running it

- **NeuroDB decides when** (it holds the schedule; BMA keeps none): `POST /api/wellbeing/runs/`
  (optionally `{"center": id}`) queues a calculation for the Celery worker and returns the run (202),
  or the run already queued or running (200); `GET /api/wellbeing/runs/<id>/` tells how it went
  (queued, running, succeeded with the totals, or failed with the error). A run left unfinished for
  3 hours (worker restarted) is marked failed so it does not block the next one. A Celery **worker**
  must be running; beat is not needed.
- Now: `python manage.py refresh_wellbeing_flags [--center ID]`.
- Back-test on a past round (read-only, counts only):
  `python manage.py wellbeing_backtest --round ID [--every 7] [--silence-days 28]` — replays the
  attendance flags week by week and reports how many children who left (recorded dropout, or no
  class day attended in the last 28 days of the round) had been flagged beforehand, how many flagged
  children stayed, and the median days of warning. Use it with the programme team to set the
  thresholds before the pilot.

## Data limits to know

- Makani attendance gets an index on `(center_id, attendance_date)` (migration `attendances.0069`,
  built concurrently so the table stays writable); the nightly run reads 120 days per centre, one centre at a time.
- PSS and digital services have no record date; service rows are not unique per child (the latest
  one is used).
- Dropout is recorded in several places (referral, follow-up, inclusion, youth kit); all are used.
