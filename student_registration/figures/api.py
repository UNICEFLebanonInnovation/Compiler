"""GET /api/figures/<programme>/?year= : the stored counts of a programme, for NeuroDB.

The view reads one stored snapshot (one indexed SELECT); it never counts. When the snapshot is
older than FIGURES_MAX_AGE_HOURS it still answers with it and queues one background count; when
there is none yet it queues one and answers 202. Only the NeuroDB service account (the group named
by YOUTH_FIGURES_API_GROUP, "NeuroDB API") or a superuser may read, at most FIGURES_API_RATE times.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from student_registration.youth.indicator_figures_api import CanReadIndicatorFigures

from . import snapshots


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
        if snapshots.is_stale(snapshot):
            snapshots.request_refresh(programme, year)
        if snapshot is None:
            return Response({'detail': 'The figures are being counted; ask again later.', 'year': year},
                            status=202)
        return Response(dict(snapshot.payload, counted_at=snapshot.created_at.isoformat(),
                             counting_seconds=snapshot.seconds))


class FiguresIndexView(APIView):
    """The programmes, their years and which of them have figures."""

    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)
    throttle_classes = (FiguresThrottle,)

    def get(self, request):
        out = []
        for name, definition in snapshots.programmes().items():
            counted = set(
                snapshots.FiguresSnapshot.objects.filter(programme=name).values_list('year', flat=True)
            )
            out.append({
                'programme': name,
                'label': definition.label,
                'current_year': definition.current_year(),
                'years': [{'year': y, 'counted': y in counted} for y in definition.years()],
            })
        return Response({'programmes': out})
