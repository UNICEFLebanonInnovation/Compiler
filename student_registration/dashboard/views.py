# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User
from student_registration.backends.djqscsv import render_to_csv_response
from django.utils.translation import gettext as _
from django.contrib import messages
from django.shortcuts import render
from datetime import datetime
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.shortcuts import render
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
from import_export.formats import base_formats
import logging

logger = logging.getLogger(__name__)

from student_registration.mscc.models import (
    PACKAGE_TYPES,
    Round,
    EducationService,
    Registration
)
from student_registration.schools.models import PartnerOrganization
from student_registration.locations.models import Center, Location


class ChartBuilderView(LoginRequiredMixin, TemplateView):
    """Interactive page for end users to create D3 charts."""

    template_name = 'dashboard/chart_builder.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "package_types": PACKAGE_TYPES,
                "partners": PartnerOrganization.objects.all(),
                "rounds": Round.objects.all(),
                "centers": Center.objects.all(),
                "governorates": Location.objects.filter(type_id=1),
                "cazas": Location.objects.filter(type_id=2),
                "cadasters": Location.objects.filter(type_id=3),
                "programme_types": EducationService.EDUCATION_PROGRAM,
            }
        )
        return context

class PivotDashboardView(LoginRequiredMixin, TemplateView):
    """Display a PivotTable.js dashboard for MSCC registrations."""

    template_name = 'dashboard/pivot_dashboard.html'


def pivot_data(request):
    """Return minimal MSCC registration data for the pivot table."""
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    qs = (
        Registration.objects.filter(deleted=False)
        .select_related('child__nationality', 'center', 'round')
    )
    data = [
        {
            'center': reg.center.name if reg.center else '',
            'gender': reg.child.gender if reg.child else '',
            'nationality': reg.child.nationality.name if reg.child and reg.child.nationality else '',
            'age': reg.child.age if reg.child else '',
            'type': reg.type,
            'round': reg.round.name if reg.round else '',
        }
        for reg in qs
    ]
    return JsonResponse(data, safe=False)

