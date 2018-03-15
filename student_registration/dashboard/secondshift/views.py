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
    School,
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

        selected_district = None
        district = int(self.request.GET.get('district', 0))
        if district:
            selected_district = Location.objects.get(id=district)
            queryset = queryset.filter(school__location_id=selected_district.id)

        selected_school = None
        school = int(self.request.GET.get('school', 0))
        if school:
            selected_school = School.objects.get(id=school)
            queryset = queryset.filter(school_id=selected_school.id)

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
            'districts': Location.objects.filter(parent__isnull=False),
            'selected_district': selected_district,
            'schools': School.objects.filter(is_2nd_shift=True),
            'selected_school': selected_school,
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

        selected_district = None
        district = int(self.request.GET.get('district', 0))
        if district:
            selected_district = Location.objects.get(id=district)
            queryset = queryset.filter(school__location_id=selected_district.id)

        selected_school = None
        school = int(self.request.GET.get('school', 0))
        if school:
            selected_school = School.objects.get(id=school)
            queryset = queryset.filter(school_id=selected_school.id)

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
            'districts': Location.objects.filter(parent__isnull=False),
            'selected_district': selected_district,
            'schools': School.objects.filter(is_2nd_shift=True),
            'selected_school': selected_school,
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

        selected_district = None
        district = int(self.request.GET.get('district', 0))
        if district:
            selected_district = Location.objects.get(id=district)
            queryset = queryset.filter(school__location_id=selected_district.id)

        selected_school = None
        school = int(self.request.GET.get('school', 0))
        if school:
            selected_school = School.objects.get(id=school)
            queryset = queryset.filter(school_id=selected_school.id)

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
            'districts': Location.objects.filter(parent__isnull=False),
            'selected_district': selected_district,
            'schools': School.objects.filter(is_2nd_shift=True),
            'selected_school': selected_school,
        }


class SchoolGradeView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/school.grade.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        schools = []

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)
        queryset = self.queryset.filter(education_year_id=current)

        selected_gov = None
        governorate = int(self.request.GET.get('gov', 0))
        if governorate:
            selected_gov = Location.objects.get(id=governorate)
            queryset = queryset.filter(school__location__parent_id=selected_gov.id)
            schools = School.objects.filter(location__parent_id=selected_gov.id, is_2nd_shift=True)

        selected_district = None
        district = int(self.request.GET.get('district', 0))
        if district:
            selected_district = Location.objects.get(id=district)
            queryset = queryset.filter(school__location_id=selected_district.id)
            schools = School.objects.filter(location_id=selected_district.id, is_2nd_shift=True)

        return {
            'registrations': queryset.count(),
            'males': queryset.filter(student__sex='Male').count(),
            'females': queryset.filter(student__sex='Female').count(),
            'education_levels': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all(),
            'current_year': current_year,
            'governorates': Location.objects.exclude(parent__isnull=False),
            'enrollments': queryset,
            'selected_year': selected_year,
            'selected_gov': selected_gov,
            'districts': Location.objects.filter(parent__isnull=False),
            'selected_district': selected_district,
            'schools': schools,
        }


class SchoolNationalityView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            TemplateView):
    model = Enrollment
    queryset = Enrollment.objects.exclude(moved__isnull=True)\
        .exclude(dropout_status__isnull=True)\
        .exclude(disabled__isnull=True)
    template_name = 'dashboard/2nd-shift/school.nationality.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        schools = []

        current_year = EducationYear.objects.get(current_year=True)
        current = int(self.request.GET.get('current', current_year.id))
        selected_year = EducationYear.objects.get(id=current)
        queryset = self.queryset.filter(education_year_id=current)

        selected_gov = None
        governorate = int(self.request.GET.get('gov', 0))
        if governorate:
            selected_gov = Location.objects.get(id=governorate)
            queryset = queryset.filter(school__location__parent_id=selected_gov.id)
            schools = School.objects.filter(location__parent_id=selected_gov.id)

        selected_district = None
        district = int(self.request.GET.get('district', 0))
        if district:
            selected_district = Location.objects.get(id=district)
            queryset = queryset.filter(school__location_id=selected_district.id)
            schools = School.objects.filter(location_id=selected_district.id)

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
            'districts': Location.objects.filter(parent__isnull=False),
            'selected_district': selected_district,
            'schools': schools,
        }
