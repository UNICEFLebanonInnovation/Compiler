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
                                SuperuserRequiredMixin,
                                TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Registration
    template_name = 'dashboard/registrations-2ndshift.html'

    # group_required = [u"editors", u"admins"]

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
        for gov in governorates:
            # get schools of this governate and its districts
            govdistschools = School.objects.filter(Q(location__parent__id=gov.id) | Q(location=gov.id))
            schools_per_gov[gov.name] = govdistschools.count()
            # get number of children of each of these schools
            numchildren = 0
            for oneschool in govdistschools:
                numchildren = numchildren + Enrollment.objects.filter(school=oneschool.id).count()

            students_per_gov[gov.name] = numchildren

        # get children by age range
        now = datetime.datetime.now()
        age_range = {}
        age_range['0-5'] = Student.objects.filter(birthday_year__gte= (now.year - 5)).count()
        age_range['6-9'] = Student.objects.filter(birthday_year__lte= (now.year - 6), birthday_year__gte=(now.year - 9)).count()
        age_range['10+'] = Student.objects.filter(birthday_year__lte=(now.year - 10)).count()

        # get HHs by ID Type
        students_by_idtype = {}
        id_types = IDType.objects.all()
        for type in id_types:
            students_by_idtype[type] = Enrollment.objects.filter(student__id_type=type).count()

        # get HHs by Nationality
        students_by_nationality = {}
        nationalities = Nationality.objects.all()
        for nationality in nationalities:
            students_by_nationality[nationality] = Enrollment.objects.filter(student__nationality_id=nationality.id).count()

        return {
                'schools': School.objects.count(),
                'students': Student.objects.count(),
                'registrations': Enrollment.objects.count(),
                'males': Student.objects.filter(sex='Male').count(),
                'females': Student.objects.filter(sex='Female').count(),
                'students_per_gov': students_per_gov,
                'students_per_school': students_per_gov,
                'age_range': age_range,
                'students_by_idtype': students_by_idtype,
                'students_by_nationality': students_by_nationality,
                'schools_per_gov': schools_per_gov,
        }


class RegistrationsALPView(LoginRequiredMixin,
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


class AttendanceView(LoginRequiredMixin, ListView):

    model = Registration
    template_name = 'dashboard/attendance.html'

    def get_context_data(self, **kwargs):


        return {

        }
