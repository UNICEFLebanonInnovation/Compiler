"""The education figures API, for NeuroDB, which decides when they are counted.

* GET /api/figures/ : the education programmes (Makani, Bridging), their payload format, their years,
  and per year whether it is counted, in which format, and whether it is stale (snapshots.stale).
* GET /api/figures/<programme>/?year= : the latest stored counts (one indexed SELECT; it never counts;
  404 when not counted yet). Education programmes only: youth answers 404.
* POST /api/figures/runs/ : ask for a count. 202 with the run; 200 with the run already queued or running.
  - {"targets": [[programme, year or null], ...]}: at most MAX_TARGETS, any programme a run can count
    (mscc, bridging, youth; youth's year may be "all"), null for its current year; wins over the keys below;
  - {"programme": optional, "year": optional}: one programme, else every education programme's current
    year (also without a body).
* GET /api/figures/runs/<id>/ : how that count is going (queued, running, succeeded, failed).

Youth is never in the index nor at /api/figures/<programme>/, so an older NeuroDB, which stores every
programme of the index as education figures, keeps working; its snapshots are read through
/api/youth/indicator-figures/.

Only the NeuroDB service account (the group named by YOUTH_FIGURES_API_GROUP, "NeuroDB API") or a
superuser may call it, at most FIGURES_API_RATE times.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from student_registration.youth.indicator_figures_api import CanReadIndicatorFigures

from . import snapshots


MAX_TARGETS = 20


class FiguresThrottle(UserRateThrottle):
    scope = 'neurodb_figures'

    def get_rate(self):
        return getattr(settings, 'FIGURES_API_RATE', '120/hour')


class FiguresView(APIView):
    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (FiguresThrottle,)

    def get(self, request, programme):
        definitions = snapshots.programmes()
        if programme not in definitions:
            return Response({'detail': 'Unknown programme', 'programmes': sorted(definitions)}, status=404)
        definition = definitions[programme]
        requested = (request.query_params.get('year') or '').strip()
        year = requested or definition.current_year()
        if year is None or (requested and not definition.has_year(requested)):
            return Response({'detail': 'No such year: %s' % (requested or 'current')}, status=404)
        snapshot = snapshots.latest(programme, year)
        if snapshot is None:
            return Response({'detail': 'Not counted yet: ask for a count (POST /api/figures/runs/).',
                             'year': year}, status=404)
        return Response(dict(snapshot.payload, counted_at=snapshot.created_at.isoformat(),
                             counting_seconds=snapshot.seconds))


class FiguresIndexView(APIView):
    """The programmes, their years and which of them have figures."""

    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (FiguresThrottle,)

    def get(self, request):
        out = []
        for name, definition in snapshots.programmes().items():
            counted = snapshots.counted_years(name)
            current = definition.current_year()
            readable = snapshots.readability(name)  # asked at most once, for a year counted without the view
            years = []
            for year in definition.years():
                format_version, created_at, base = counted.get(year, (None, None, None))
                years.append({'year': year, 'counted': year in counted, 'format': format_version,
                              'stale': snapshots.stale(definition, year, format_version, created_at, current,
                                                       base=base, readable=readable)})
            out.append({
                'programme': name,
                'label': definition.label,
                'format_version': definition.format_version,
                'current_year': current,
                'years': years,
            })
        return Response({'programmes': out})


def _text(value):
    return '' if value is None else str(value).strip()


def read_targets(given, definitions):
    """The targets of a run body as [(programme, year or None)], or (None, the 400 answer)."""
    if not isinstance(given, (list, tuple)) or not given:
        return None, {'detail': 'targets must be a non-empty list of [programme, year or null]'}
    if len(given) > MAX_TARGETS:
        return None, {'detail': 'At most %d targets' % MAX_TARGETS}
    targets = []
    for target in given:
        if not isinstance(target, (list, tuple)) or len(target) not in (1, 2):
            return None, {'detail': 'A target is [programme, year or null]: %s' % str(target)[:60]}
        programme = _text(target[0])
        year = _text(target[1]) if len(target) == 2 else ''
        if programme not in definitions:
            return None, {'detail': 'Unknown programme', 'programmes': sorted(definitions)}
        if year and not definitions[programme].has_year(year):
            return None, {'detail': 'No such year: %s %s' % (programme, year[:40])}
        if year and hasattr(definitions[programme], 'year_name'):  # youth: "ALL" is "all"
            year = definitions[programme].year_name(year)
        if (programme, year or None) not in targets:
            targets.append((programme, year or None))
    return targets, None


class FiguresRunsView(APIView):
    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (FiguresThrottle,)

    def post(self, request):
        definitions = snapshots.all_programmes()
        data = request.data if hasattr(request.data, 'get') else {}
        if data.get('targets') is not None:
            targets, error = read_targets(data.get('targets'), definitions)
            if error is not None:
                return Response(error, status=400)
        else:
            programme = _text(data.get('programme'))
            year = _text(data.get('year')) or None
            if programme and programme not in definitions:
                return Response({'detail': 'Unknown programme', 'programmes': sorted(definitions)}, status=400)
            if year and not programme:
                return Response({'detail': 'A year needs its programme'}, status=400)
            if year and not definitions[programme].has_year(year):
                return Response({'detail': 'No such year: %s' % year[:40]}, status=400)
            if year and hasattr(definitions[programme], 'year_name'):
                year = definitions[programme].year_name(year)
            targets = [(programme, year)] if programme else [(name, None) for name in snapshots.programmes()]
        run, created = snapshots.start_run(targets, requested_by=request.user.get_username())
        return Response(run.as_dict(), status=202 if created else 200)


class FiguresRunView(APIView):
    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (FiguresThrottle,)

    def get(self, request, run_id):
        from .models import FiguresRun

        run = FiguresRun.objects.filter(pk=run_id).first()
        if run is None:
            return Response({'detail': 'No such run'}, status=404)
        return Response(run.as_dict())
