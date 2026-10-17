"""What an error report may carry from a count of the NeuroDB figures (SPEC §7: the population of a Power BI
view is never logged or sent).

Sentry (config/settings/production.py) sends the local variables of every frame of an exception it reports
(``include_local_variables``, on by default). The variables of a count's frames hold the view's population:
the registration ids of the period, the rows and the partner per id (SQL parameters, dicts of the Python loops)
and the rows being read. Every count catches its own failures and logs them by their class and first line, so
none should reach the reporter; but an exception that passes through a count anyway (an abort of the worker
inside a query, a failure in code added later) must not carry them. ``drop_count_variables`` is Sentry's
``before_send``: for an event whose stack passes through the counting code, it drops the variables of every
frame (the frames of Django and psycopg below a count hold the same parameters) and keeps the rest (files,
functions, lines, the exception's class and message). Other events are left as they are.

No Django import here: the production settings import this module.
"""

COUNTING_MODULES = (
    'student_registration.figures',
    'student_registration.youth.indicator_figures',
    'student_registration.youth.indicator_figures_api',
)
COUNTING_PATHS = ('student_registration/figures/', 'student_registration/youth/indicator_figures')


def _stacktraces(event):
    for part in ('exception', 'threads'):
        for value in (event.get(part) or {}).get('values') or ():
            if isinstance(value, dict) and isinstance(value.get('stacktrace'), dict):
                yield value['stacktrace']
    if isinstance(event.get('stacktrace'), dict):
        yield event['stacktrace']


def _frames(event):
    for stacktrace in _stacktraces(event):
        for frame in stacktrace.get('frames') or ():
            if isinstance(frame, dict):
                yield frame


def is_counting(frame):
    """Whether ``frame`` (a Sentry event's frame) is of the counting code."""
    module = str(frame.get('module') or '')
    if any(module == name or module.startswith(name + '.') for name in COUNTING_MODULES):
        return True
    path = str(frame.get('abs_path') or frame.get('filename') or '').replace('\\', '/')
    return any(part in path for part in COUNTING_PATHS)


def drop_count_variables(event, hint=None):
    """Sentry's ``before_send``: the event without the variables of its frames when its stack passes through
    the counting code (see above); any other event unchanged."""
    frames = list(_frames(event))
    if any(is_counting(frame) for frame in frames):
        for frame in frames:
            frame.pop('vars', None)
    return event
