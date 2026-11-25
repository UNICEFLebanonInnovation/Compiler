"""GET /api/youth/indicator-figures/?year=2026 — the youth indicator figures for NeuroDB.

Counts only (see indicator_figures.py). The figures cover every partner, so the endpoint is not
open to partner accounts: the caller must be a superuser or belong to the group named by the
YOUTH_FIGURES_API_GROUP setting ("NeuroDB API" by default). NeuroDB signs in with a token
(Authorization: Token <key>) of a service account in that group.

``?year=`` is a reporting year's name (the current one by default) or ``all`` (every year). The answer
is the latest snapshot the night task stored for that year (figures/snapshots.py, programme ``youth``)
when it has the current format and is not stale; otherwise a year's figures are counted now, under the
same read-only limits as the night task (so a NeuroDB that never asks for a youth count still gets
current figures). ``all`` is never counted during a request (every year at once is the heaviest count):
its latest snapshot of the current format is served however old (``counted_at`` says when), else 404
until a run counts it. A count on the spot that fails answers 503 with the error's class (logged by its
class and first line, never with the exception, whose frames hold the view's ids); the worker's timeout
during it still stops the worker, without the count's frames (``count_now``). At most
YOUTH_FIGURES_API_RATE requests (default 120/hour), counted apart from the education figures API's.
"""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from . import indicator_figures

logger = logging.getLogger(__name__)


def api_group() -> str:
    return getattr(settings, 'YOUTH_FIGURES_API_GROUP', 'NeuroDB API')


class CanReadIndicatorFigures(permissions.BasePermission):
    message = 'Only the NeuroDB service account can read the youth indicator figures.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        return user.is_superuser or user.groups.filter(name=api_group()).exists()


class YouthFiguresThrottle(UserRateThrottle):
    """A scope of its own: youth reads never use up the education scope NeuroDB's run polling draws on."""

    scope = 'neurodb_youth'

    def get_rate(self):
        return getattr(settings, 'YOUTH_FIGURES_API_RATE', '120/hour')


class YouthIndicatorFiguresView(APIView):
    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (YouthFiguresThrottle,)

    def get(self, request):
        from student_registration.figures import snapshots
        from student_registration.figures.youth import Youth

        requested = (request.query_params.get('year') or '').strip()
        if requested.lower() == indicator_figures.ALL:
            name = indicator_figures.ALL
        else:
            year = indicator_figures.resolve_year(requested)
            if year is None:
                return Response({'detail': 'No such reporting year: %s' % (requested[:40] or 'current')},
                                status=404)
            name = year.name
        snapshot = snapshots.latest(Youth.name, name)
        fresh = snapshot is not None and not snapshots.is_stale(snapshot, Youth.name)
        if name == indicator_figures.ALL and snapshot is not None:  # never counted during a request
            fresh = (snapshot.payload or {}).get('format') == indicator_figures.FORMAT_VERSION
        if fresh:
            return Response(dict(snapshot.payload, counted_at=snapshot.created_at.isoformat(),
                                 counting_seconds=snapshot.seconds))
        if name == indicator_figures.ALL:
            return Response({'detail': 'Not counted yet: ask for a count (POST /api/figures/runs/ with the target '
                                       '["youth", "all"]).', 'year': name}, status=404)
        return count_now(name)


def count_now(name):
    """The year counted on the spot; when the count fails, 503 with the error's class, the failure logged by
    its class and first line only: never raised to the error reporter (Sentry sends the variables of every
    frame, and those of the count hold the view's registration ids and enrolment rows: SPEC §7).

    An abort is not a failure of the count: gunicorn's worker timeout (Procfile ``--timeout``) raises
    SystemExit wherever the count is, and the worker must still exit. It is raised again, as a new exception
    of its class raised here, outside the handler: no frame of the count and no chained exception go with it."""
    from student_registration.figures import power_bi
    from student_registration.figures.youth import Youth

    failure = abort = None
    try:
        return Response(Youth().build(name))
    except Exception as exc:  # every failure: see above
        failure = power_bi.error_class(exc), power_bi.error_line(exc)
    except BaseException as exc:  # SystemExit (the worker's timeout), KeyboardInterrupt: raised again below
        abort = type(exc), exc.args, power_bi.error_line(exc)
    if abort is not None:
        logger.error('youth figures %s: counting on the spot was stopped: %s', name, abort[2])
        raise _raised_again(*abort[:2])
    logger.error('youth figures %s: counting on the spot failed: %s', name, failure[1])
    return Response({'detail': 'The figures could not be counted now; ask for a count (POST /api/figures/runs/).',
                     'year': name, 'error': failure[0]}, status=503)


def _raised_again(kind, args):
    """A new exception of ``kind`` with the same arguments (SystemExit keeps its exit code): no traceback, no
    context. The one caught held the frames of the count."""
    try:
        return kind(*args)
    except Exception:  # a class that does not take its arguments back
        return SystemExit(1)
