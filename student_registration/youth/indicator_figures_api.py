"""GET /api/youth/indicator-figures/?year=2026 — the youth indicator figures for NeuroDB.

Counts only (see indicator_figures.py). The figures cover every partner, so the endpoint is not
open to partner accounts: the caller must be a superuser or belong to the group named by the
YOUTH_FIGURES_API_GROUP setting ("NeuroDB API" by default). NeuroDB signs in with a token
(Authorization: Token <key>) of a service account in that group.
"""

from __future__ import annotations

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import indicator_figures


def api_group() -> str:
    return getattr(settings, 'YOUTH_FIGURES_API_GROUP', 'NeuroDB API')


class CanReadIndicatorFigures(permissions.BasePermission):
    message = 'Only the NeuroDB service account can read the youth indicator figures.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        return user.is_superuser or user.groups.filter(name=api_group()).exists()


class YouthIndicatorFiguresView(APIView):
    permission_classes = (permissions.IsAuthenticated, CanReadIndicatorFigures)

    def get(self, request):
        requested = request.query_params.get('year')
        year = indicator_figures.resolve_year(requested)
        if year is None:
            return Response({'detail': 'No such reporting year: %s' % (requested or 'current')}, status=404)
        return Response(indicator_figures.build(year))
