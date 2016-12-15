# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from student_registration.locations.models import (
    Location,
)
from student_registration.schools.models import (
    School,
)
from student_registration.students.models import (
    Student,
    IDType,
    Nationality,
)

from student_registration.registrations.models import Registration, RegisteringAdult
from student_registration.enrollments.models import Enrollment
from student_registration.alp.models import Outreach
import datetime
from django.db.models import Q


class RegistrationsPilotView(LoginRequiredMixin,
                             SuperuserRequiredMixin,
                             TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Registration
    template_name = 'dashboard/registrations-pilot.html'

    # group_required = [u"editors", u"admins"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        # children by governate || get the governettes and get the number of children for each, and put them in a dictionary
        # Also Adults by governate
        # Also schools by governate
        governates = Location.objects.exclude(parent__isnull=False)

        childrenPerGov = {}
        adultsPerGov = {}
        schoolsPerGov = {}
        for gov in governates:
            # get schools of this governate and its districts
            govdistschools = School.objects.filter(Q(location__parent__id=gov.id) | Q(location=gov.id))
            schoolsPerGov[gov.name] = govdistschools.count()
            # get number of children of each of these schools
            numchildren = 0
            numadults = 0
            for oneschool in govdistschools:
                numchildren = numchildren + Registration.objects.filter(school=oneschool.id).count()
                numadults = numadults + RegisteringAdult.objects.filter(school=oneschool.id).count()

            childrenPerGov[gov.name] = numchildren
            adultsPerGov[gov.name] = numadults

        # some students are not tied to any school, show them also in the charts
        childrenPerGov['N/A'] = Registration.objects.filter(school__isnull=True).count()
        adultsPerGov['N/A'] = RegisteringAdult.objects.filter(school__isnull=True).count()

        # get children by age range
        now = datetime.datetime.now()
        agerange = {}
        agerange['0-5'] = Student.objects.filter(birthday_year__gte= (now.year - 5)).count()
        agerange['6-9'] = Student.objects.filter(birthday_year__lte= (now.year - 6), birthday_year__gte=(now.year - 9)).count()
        agerange['10+'] = Student.objects.filter(birthday_year__lte=(now.year - 10)).count()

        # get HHs by ID Type
        adultsbyidtype = {}
        idtypes = IDType.objects.all()
        for type in idtypes:
            adultsbyidtype[type] = RegisteringAdult.objects.filter(id_type=type).count()

        # get HHs by Nationality
        adultsbynationality = {}
        nationalities = Nationality.objects.all()
        for nationality in nationalities:
            adultsbynationality[nationality] = RegisteringAdult.objects.filter(nationality=nationality).count()

        return {
                'schools': School.objects.count(),
                'students': Student.objects.count(),
                'registrations': Registration.objects.count(),
                'adults': RegisteringAdult.objects.count(),
                'males': Student.objects.filter(sex='Male').count(),
                'females': Student.objects.filter(sex='Female').count(),
                'notenrolledlastyear': Registration.objects.filter(enrolled_last_year_school__isnull = True).count(),
                'childrenPerGov': childrenPerGov,
                'adultsPerGov': adultsPerGov,
                'agerange': agerange,
                'adultsbyidtype': adultsbyidtype,
                'adultsbynationality': adultsbynationality,
                'schoolsPerGov': schoolsPerGov,
        }


class Registrations2ndShiftView(LoginRequiredMixin,
                                GroupRequiredMixin,
                                TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Enrollment
    template_name = 'dashboard/registrations-2ndshift.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        # children by governate || get the governettes and get the number of children for each, and put them in a dictionary
        # Also schools by governate
        governorates = Location.objects.exclude(parent__isnull=False)

        students_per_gov = {}
        schools_per_gov = {}
        students_per_school = {}
        for gov in governorates:
            # get schools of this governate and its districts
            govdistschools = School.objects.filter(Q(location__parent__id=gov.id) | Q(location=gov.id))
            schools_per_gov[gov.name] = govdistschools.count()
            # get number of children of each of these schools
            numchildren = 0
            for oneschool in govdistschools:
                nbr = self.model.objects.filter(school=oneschool.id).count()
                if nbr:
                    students_per_school[oneschool.name] = nbr
                numchildren += nbr

            students_per_gov[gov.name] = numchildren

        # get children by age range
        now = datetime.datetime.now()
        age_range = {}
        age_range['0-6'] = self.model.objects.filter(student__birthday_year__gte=(now.year - 6)).count()
        age_range['7-9'] = self.model.objects.filter(student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range['10-12'] = self.model.objects.filter(student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range['13+'] = self.model.objects.filter(student__birthday_year__lte=(now.year - 13)).count()

        age_range_1 = {}
        age_range_1['0-6'] = self.model.objects.filter(school__location__parent_id=1, student__birthday_year__gte=(now.year - 6)).count()
        age_range_1['7-9'] = self.model.objects.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_1['10-12'] = self.model.objects.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_1['13+'] = self.model.objects.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 13)).count()

        age_range_2 = {}
        age_range_2['0-6'] = self.model.objects.filter(school__location__parent_id=2, student__birthday_year__gte=(now.year - 6)).count()
        age_range_2['7-9'] = self.model.objects.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_2['10-12'] = self.model.objects.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_2['13+'] = self.model.objects.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 13)).count()

        age_range_3 = {}
        age_range_3['0-6'] = self.model.objects.filter(school__location__parent_id=3, student__birthday_year__gte=(now.year - 6)).count()
        age_range_3['7-9'] = self.model.objects.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_3['10-12'] = self.model.objects.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_3['13+'] = self.model.objects.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 13)).count()

        age_range_4 = {}
        age_range_4['0-6'] = self.model.objects.filter(school__location__parent_id=4, student__birthday_year__gte=(now.year - 6)).count()
        age_range_4['7-9'] = self.model.objects.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_4['10-12'] = self.model.objects.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_4['13+'] = self.model.objects.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 13)).count()

        age_range_5 = {}
        age_range_5['0-6'] = self.model.objects.filter(school__location__parent_id=5, student__birthday_year__gte=(now.year - 6)).count()
        age_range_5['7-9'] = self.model.objects.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_5['10-12'] = self.model.objects.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_5['13+'] = self.model.objects.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 13)).count()

        age_range_6 = {}
        age_range_6['0-6'] = self.model.objects.filter(school__location__parent_id=6, student__birthday_year__gte=(now.year - 6)).count()
        age_range_6['7-9'] = self.model.objects.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_6['10-12'] = self.model.objects.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_6['13+'] = self.model.objects.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 13)).count()

        age_range_7 = {}
        age_range_7['0-6'] = self.model.objects.filter(school__location__parent_id=7, student__birthday_year__gte=(now.year - 6)).count()
        age_range_7['7-9'] = self.model.objects.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_7['10-12'] = self.model.objects.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_7['13+'] = self.model.objects.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 13)).count()

        age_range_8 = {}
        age_range_8['0-6'] = self.model.objects.filter(school__location__parent_id=8, student__birthday_year__gte=(now.year - 6)).count()
        age_range_8['7-9'] = self.model.objects.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_8['10-12'] = self.model.objects.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_8['13+'] = self.model.objects.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 13)).count()

        # get HHs by ID Type
        students_by_idtype = {}
        id_types = IDType.objects.all()
        for type in id_types:
            students_by_idtype[type] = self.model.objects.filter(student__id_type=type).count()

        # get HHs by Nationality
        students_by_nationality = {}
        nationalities = Nationality.objects.all()
        for nationality in nationalities:
            students_by_nationality[nationality] = self.model.objects.filter(student__nationality_id=nationality.id).count()

        return {
                'schools': len(students_per_school),
                'registrations': self.model.objects.count(),
                'males': self.model.objects.filter(student__sex='Male').count(),
                'females': self.model.objects.filter(student__sex='Female').count(),
                'students_per_gov': students_per_gov,
                'students_per_school': students_per_school,
                'age_range': age_range,
                'age_range_1': age_range_1,
                'age_range_2': age_range_2,
                'age_range_3': age_range_3,
                'age_range_4': age_range_4,
                'age_range_5': age_range_5,
                'age_range_6': age_range_6,
                'age_range_7': age_range_7,
                'age_range_8': age_range_8,
                'students_by_idtype': students_by_idtype,
                'students_by_nationality': students_by_nationality,
                'schools_per_gov': schools_per_gov,
        }


class RegistrationsALPView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Outreach
    queryset = Outreach.objects.exclude(assigned_to_level__isnull=True)
    template_name = 'dashboard/registrations-alp.html'

    group_required = [u"ALP_MEHE"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        # children by governate || get the governettes and get the number of children for each, and put them in a dictionary
        # Also schools by governate
        governorates = Location.objects.exclude(parent__isnull=False)

        students_per_gov = {}
        schools_per_gov = {}
        students_per_school = {}
        for gov in governorates:
            # get schools of this governate and its districts
            govdistschools = School.objects.filter(Q(location__parent__id=gov.id) | Q(location=gov.id))
            schools_per_gov[gov.name] = govdistschools.count()
            # get number of children of each of these schools
            numchildren = 0
            for oneschool in govdistschools:
                nbr = self.queryset.filter(school=oneschool.id).count()
                if nbr:
                    students_per_school[oneschool.name] = nbr
                numchildren += nbr

            students_per_gov[gov.name] = numchildren

        # get children by age range
        now = datetime.datetime.now()
        age_range = {}
        age_range['0-6'] = self.queryset.filter(student__birthday_year__gte=(now.year - 6)).count()
        age_range['7-9'] = self.queryset.filter(student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range['10-12'] = self.queryset.filter(student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range['13+'] = self.queryset.filter(student__birthday_year__lte=(now.year - 13)).count()

        # get HHs by ID Type
        students_by_idtype = {}
        id_types = IDType.objects.all()
        for type in id_types:
            students_by_idtype[type] = self.queryset.filter(student__id_type=type).count()

        # get HHs by Nationality
        students_by_nationality = {}
        nationalities = Nationality.objects.all()
        for nationality in nationalities:
            students_by_nationality[nationality] = self.queryset.filter(student__nationality_id=nationality.id).count()

        return {
                'schools': len(students_per_school),
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'students_per_gov': students_per_gov,
                'students_per_school': students_per_school,
                'age_range': age_range,
                'students_by_idtype': students_by_idtype,
                'students_by_nationality': students_by_nationality,
                'schools_per_gov': schools_per_gov,
        }


class AttendanceView(LoginRequiredMixin, ListView):

    model = Registration
    template_name = 'dashboard/attendance.html'

    def get_context_data(self, **kwargs):


        return {

        }
