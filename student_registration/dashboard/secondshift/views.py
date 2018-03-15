# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from student_registration.locations.models import (
    Location,
)
from student_registration.schools.models import (
    EducationYear,
    ClassRoom,
)

from student_registration.enrollments.models import Enrollment
from student_registration.students.models import Nationality


class GovernorateGradeView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/governorate.grade.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)

        queryset = self.queryset.filter(education_year_id=current)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
        }


class GovernorateAgeView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/governorate.age.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)

        queryset = self.queryset.filter(education_year_id=current)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
        }


class GovernorateNationalityView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/governorate.nationality.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)

        queryset = self.queryset.filter(education_year_id=current)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
        }


class GradeAgeView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/grade.age.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)
        queryset = self.queryset.filter(education_year_id=current)

        selected_gov = None
        governorate = int(self.request.GET.get('gov', 0))
        if governorate:
            selected_gov = Location.objects.get(id=governorate)
            queryset = queryset.filter(school__location__parent_id=selected_gov.id)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
            'selected_gov': selected_gov
        }


class GradeNationalityView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/grade.nationality.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)
        queryset = self.queryset.filter(education_year_id=current)

        selected_gov = None
        governorate = int(self.request.GET.get('gov', 0))
        if governorate:
            selected_gov = Location.objects.get(id=governorate)
            queryset = queryset.filter(school__location__parent_id=selected_gov.id)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
            'selected_gov': selected_gov,
        }


class NationalityAgeView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/nationality.age.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)
        queryset = self.queryset.filter(education_year_id=current)

        selected_gov = None
        governorate = int(self.request.GET.get('gov', 0))
        if governorate:
            selected_gov = Location.objects.get(id=governorate)
            queryset = queryset.filter(school__location__parent_id=selected_gov.id)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'nationalities': Nationality.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
            'selected_gov': selected_gov
        }
