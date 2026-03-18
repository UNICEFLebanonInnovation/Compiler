# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import OuterRef, Subquery, F
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)

from django.db import models
from student_registration.mscc.models import (
    PACKAGE_TYPES,
    Round,
    EducationService,
    EducationAssessment,
    Registration,
    EducationProgrammeAssessment,
    InclusionService,
    PSSService,
    HealthNutritionService,
)
from student_registration.attendances.models import MSCCAttendanceChild
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

    latest_prog_type = (
        EducationProgrammeAssessment.objects.filter(
            registration=OuterRef("pk")
        )
        .order_by("-id")
        .values_list("programme_type", flat=True)[:1]
    )

    qs = (
        Registration.objects.filter(deleted=False)
        .annotate(
            programme_type=Subquery(latest_prog_type),
            center_name=F("center__name"),
            partner_name=F("center__partner__name"),
            round_name=F("round__name"),
            round_year=F("round__year"),
            governorate=F("center__governorate__name"),
            caza=F("center__caza__name"),
            district=F("center__cadaster__name"),
            gender=F("child__gender"),
            nationality=F("child__nationality__name"),
            package_type=F("type"),
        )
    )

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
            "round_year": getattr(row, "round_year", "") or "",
            "programme_type": getattr(row, "programme_type", "") or "",
        }
        for row in qs
    ]

    return JsonResponse(data, safe=False)


class WellbeingDashboardView(LoginRequiredMixin, TemplateView):
    """Display the advanced wellbeing dashboard."""

    template_name = 'dashboard/wellbeing_dashboard.html'


def wellbeing_data(request):
    """Return aggregated wellbeing and correlation data for the dashboard."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Get MSCC Registrations - Limit to last 5000 for performance
    registrations = Registration.objects.filter(deleted=False).select_related(
        'child', 'center', 'round', 'child__nationality'
    ).order_by('-id')[:5000]

    reg_ids = [r.id for r in registrations]

    # Latest education assessments
    latest_assessments = EducationProgrammeAssessment.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    assessments_dict = {a.registration_id: a for a in latest_assessments}

    # Education Service (status at entry)
    edu_services = EducationService.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    edu_services_dict = {e.registration_id: e for e in edu_services}

    # Education Assessment (barriers and subject grades)
    edu_assessments = EducationAssessment.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    edu_assessments_dict = {e.registration_id: e for e in edu_assessments}

    # Inclusion (dropout)
    inclusions = InclusionService.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    inclusions_dict = {i.registration_id: i for i in inclusions}

    # PSS (living arrangement, distress)
    pss_services = PSSService.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    pss_dict = {p.registration_id: p for p in pss_services}

    # Health and Nutrition
    health_services = HealthNutritionService.objects.filter(registration_id__in=reg_ids).order_by('registration_id', '-id').distinct('registration_id')
    health_dict = {h.registration_id: h for h in health_services}

    # Attendance aggregation
    attendance_qs = MSCCAttendanceChild.objects.filter(registration_id__in=reg_ids).values('registration').annotate(
        total_days=models.Count('id'),
        attended_days=models.Count('id', filter=models.Q(attended='Yes'))
    )
    attendance_dict = {a['registration']: a for a in attendance_qs}

    data = []
    for reg in registrations:
        assessment = assessments_dict.get(reg.id)
        edu_service = edu_services_dict.get(reg.id)
        edu_assessment = edu_assessments_dict.get(reg.id)
        inclusion = inclusions_dict.get(reg.id)
        pss = pss_dict.get(reg.id)
        health = health_dict.get(reg.id)
        att = attendance_dict.get(reg.id, {'total_days': 0, 'attended_days': 0})

        attendance_rate = (att['attended_days'] / att['total_days'] * 100) if att['total_days'] > 0 else None

        edu_improvement = 0
        if assessment and assessment.pre_test and assessment.post_test:
            try:
                pre_scores = [float(v) for k, v in assessment.pre_test.items() if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit()]
                post_scores = [float(v) for k, v in assessment.post_test.items() if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit()]
                if pre_scores and post_scores and len(pre_scores) == len(post_scores):
                    pre_avg = sum(pre_scores) / len(pre_scores)
                    post_avg = sum(post_scores) / len(post_scores)
                    if pre_avg > 0:
                        edu_improvement = ((post_avg - pre_avg) / pre_avg) * 100
            except Exception:
                pass

        # Subject specific improvement
        arabic_imp = 0
        math_imp = 0
        lang_imp = 0
        if edu_assessment:
            if edu_assessment.pre_arabic_grade and edu_assessment.post_arabic_grade and edu_assessment.pre_arabic_grade > 0:
                arabic_imp = ((edu_assessment.post_arabic_grade - edu_assessment.pre_arabic_grade) / edu_assessment.pre_arabic_grade) * 100
            if edu_assessment.pre_math_grade and edu_assessment.post_math_grade and edu_assessment.pre_math_grade > 0:
                math_imp = ((edu_assessment.post_math_grade - edu_assessment.pre_math_grade) / edu_assessment.pre_math_grade) * 100
            if edu_assessment.pre_language_grade and edu_assessment.post_language_grade and edu_assessment.pre_language_grade > 0:
                lang_imp = ((edu_assessment.post_language_grade - edu_assessment.pre_language_grade) / edu_assessment.pre_language_grade) * 100

        data.append({
            "id": reg.id,
            "gender": reg.child.gender if reg.child else "",
            "have_labour": reg.have_labour or "No",
            "attendance_rate": attendance_rate,
            "edu_improvement": edu_improvement,
            "arabic_improvement": arabic_imp,
            "math_improvement": math_imp,
            "language_improvement": lang_imp,
            "living_arrangement": pss.child_living_arrangement if pss else "",
            "caregivers_distress": pss.caregivers_distress if pss else "",
            "child_distress": pss.child_distress if pss else "",
            "education_status": edu_service.education_status if edu_service else "",
            "barriers": edu_assessment.barriers if edu_assessment else "",
            "muac": health.muac_malnutrition_screening if health else "",
            "meals": health.eating_minimum_meals if health else "",
            "vaccinated": health.child_vaccinated if health else "",
            "dropout": inclusion.dropout if inclusion else "No",
        })

    return JsonResponse(data, safe=False)


class CenterMapView(LoginRequiredMixin, TemplateView):
    """Display the centers geo map."""

    template_name = 'dashboard/centers_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partners'] = PartnerOrganization.objects.all().order_by('name')
        return context


def center_map_data(request):
    """Return center location data and registration counts for the map."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    from django.db.models.functions import Coalesce

    partner_id = request.GET.get('partner_id')

    registration_count = Registration.objects.filter(
        center=OuterRef('pk'),
        deleted=False
    ).values('center').annotate(
        count=models.Count('id')
    ).values('count')

    centers = Center.objects.filter(latitude__isnull=False, longitude__isnull=False).select_related(
        'partner', 'governorate', 'caza'
    ).annotate(
        children_count=Coalesce(Subquery(registration_count, output_field=models.IntegerField()), 0)
    )

    if partner_id:
        centers = centers.filter(partner_id=partner_id)

    data = [
        {
            "id": center.id,
            "name": center.name,
            "latitude": center.latitude,
            "longitude": center.longitude,
            "partner": center.partner.name if center.partner else "",
            "governorate": center.governorate.name if center.governorate else "",
            "caza": center.caza.name if center.caza else "",
            "total_children": center.children_count,
        }
        for center in centers
    ]

    return JsonResponse(data, safe=False)


def center_children_data(request):
    """Return children registered in a specific center."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    center_id = request.GET.get('center_id')
    if not center_id:
        return JsonResponse({"error": "Center ID is required"}, status=400)

    latest_prog_type = (
        EducationProgrammeAssessment.objects.filter(
            registration=OuterRef("pk")
        )
        .order_by("-id")
        .values_list("programme_type", flat=True)[:1]
    )

    registrations = Registration.objects.filter(
        center_id=center_id,
        deleted=False
    ).annotate(
        programme_type=Subquery(latest_prog_type),
        center_name=F("center__name"),
        partner_name=F("center__partner__name"),
        round_name=F("round__name"),
    ).select_related('child', 'child__nationality').order_by('child__first_name', 'child__last_name')

    data = [
        {
            "id": reg.id,
            "full_name": reg.child.full_name if reg.child else "N/A",
            "gender": reg.child.gender if reg.child else "N/A",
            "age": reg.child.age if reg.child else "N/A",
            "nationality": reg.child.nationality.name if reg.child and reg.child.nationality else "N/A",
            "programme_type": reg.programme_type or "N/A",
            "round": reg.round_name or "N/A",
            "partner": reg.partner_name or "N/A",
            "center": reg.center_name or "N/A",
        }
        for reg in registrations
    ]

    return JsonResponse(data, safe=False)
