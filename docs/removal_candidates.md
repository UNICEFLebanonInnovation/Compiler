# Removal Candidates for Non-Makani / Non-CLM-Bridging Code

The paths below belong to programmes outside Makani/MSCC and CLM Bridging. Removing them will slim the platform down to just those two modules while keeping the shared infrastructure both apps still need (e.g. `students`, `locations`, `backends`, `taskapp`, etc.).

## Django apps under `student_registration/`
Delete the following application directories – neither Makani MSCC nor CLM Bridging import them:

- `student_registration/accounts/`
- `student_registration/adolescent/`
- `student_registration/alp/`
- `student_registration/child/`
- `student_registration/contrib/`
- `student_registration/dashboard/`
- `student_registration/enrollments/`
- `student_registration/helpdesks/`
- `student_registration/staffenroll/`
- `student_registration/staffs/`
- `student_registration/user_activity/`
- `student_registration/winterization/`
- `student_registration/youth/`

Keep `student_registration/attendances/`, `student_registration/outreach/`, `student_registration/schools/`, `student_registration/students/`, `student_registration/users/`, and shared middleware because both Makani and Bridging depend on them.

## CLM submodules unrelated to Bridging
Inside `student_registration/clm/` remove the files below to drop non-bridging programme logic. Bridging relies on `bridging_forms.py`, `bridging_views.py`, the Bridging parts of `models.py`, `serializers.py`, `filters.py`, `tables.py`, and the dedicated templates – keep those.

- `student_registration/clm/attendance_views.py`
- `student_registration/clm/forms.py` *(after extracting the Bridging forms to `bridging_forms.py`, the remainder supports other programmes)*
- `student_registration/clm/inclusion_filters.py`
- `student_registration/clm/inclusion_forms.py`
- `student_registration/clm/inclusion_serializers.py`
- `student_registration/clm/inclusion_tables.py`
- `student_registration/clm/inclusion_views.py`
- `student_registration/clm/management/`
- `student_registration/clm/tasks.py`
- `student_registration/clm/tests.py`
- `student_registration/clm/views.py`
- `student_registration/clm/api_views.py`

## Templates
Within `student_registration/templates/`, only Makani/MSCC and CLM Bridging templates are required. You can delete these directories entirely:

- `student_registration/templates/account/`
- `student_registration/templates/alp/`
- `student_registration/templates/attendances/`
- `student_registration/templates/dashboard/`
- `student_registration/templates/enrollments/`
- `student_registration/templates/outreach/`
- `student_registration/templates/pages/`
- `student_registration/templates/staffenroll/`
- `student_registration/templates/staffs/`
- `student_registration/templates/youth/`

Inside `student_registration/templates/clm/` delete every template whose filename does **not** start with `bridging` (keep shared bases such as `base.html`, `base4.html`, and `landing_page.html`). Templates under `student_registration/templates/mscc/` are part of the Makani module and should be retained.

## Static assets
Review `student_registration/static/` and remove scripts or styles whose filenames reference retired programmes (e.g. ABLN, BLN, CBECE, Inclusion, Dashboard). MSCC and Bridging only use the shared theme assets plus any files with `mscc` or `bridging` in the path or filename.

## Celery and configuration follow-up
After deleting the code above, update Celery (`student_registration/taskapp`) and Django settings/URL registrations to drop references to the removed modules.
