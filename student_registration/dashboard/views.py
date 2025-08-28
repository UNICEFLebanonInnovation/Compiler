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
from django.db.models import OuterRef, Subquery, F
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
    Registration,
    EducationProgrammeAssessment,
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
    filters = {}
    partner = request.GET.get("partner")
    if partner:
        filters["center__partner__name"] = partner
    center = request.GET.get("center")
    if center:
        filters["center__name"] = center
    round_name = request.GET.get("round")
    if round_name:
        filters["round__name"] = round_name
    governorate = request.GET.get("governorate")
    if governorate:
        filters["center__governorate__name"] = governorate
    caza = request.GET.get("caza")
    if caza:
        filters["center__caza__name"] = caza
    district = request.GET.get("district")
    if district:
        filters["center__cadaster__name"] = district
    gender = request.GET.get("gender")
    if gender:
        filters["child__gender"] = gender
    nationality = request.GET.get("nationality")
    if nationality:
        filters["child__nationality__name"] = nationality
    package_type = request.GET.get("package_type")
    if package_type:
        filters["type"] = package_type

    latest_prog_type = (
        EducationProgrammeAssessment.objects.filter(
            registration=OuterRef("pk")
        )
        .order_by("-id")
        .values_list("programme_type", flat=True)[:1]
    )

    qs = (
        Registration.objects.filter(deleted=False, **filters)
        .annotate(
            programme_type=Subquery(latest_prog_type),
            center_name=F("center__name"),
            partner_name=F("center__partner__name"),
            round_name=F("round__name"),
            governorate=F("center__governorate__name"),
            caza=F("center__caza__name"),
            district=F("center__cadaster__name"),
            gender=F("child__gender"),
            nationality=F("child__nationality__name"),
            package_type=F("type"),
        )
    )

    programme_type = request.GET.get("programme_type")
    if programme_type:
        qs = qs.filter(programme_type=programme_type)

    data = [
        {
            "center": getattr(row, "center_name", "") or "",
            "partner": getattr(row, "partner_name", "") or "",
            "governorate": getattr(row, "governorate", "") or "",
            "caza": getattr(row, "caza", "") or "",
            "district": getattr(row, "district", "") or "",
            "gender": getattr(row, "gender", "") or "",
            "nationality": getattr(row, "nationality", "") or "",
            "package_type": getattr(row, "package_type", "") or "",
            "round": getattr(row, "round_name", "") or "",
            "programme_type": getattr(row, "programme_type", "") or "",
        }
        for row in qs
    ]

    return JsonResponse(data, safe=False)

