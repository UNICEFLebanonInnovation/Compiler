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
from student_registration.alp.models import Outreach, ALPRound
from student_registration.users.models import User
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
    queryset = Enrollment.objects.all()
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

        age_range_1 = {}
        age_range_1['0-6'] = self.queryset.filter(school__location__parent_id=1, student__birthday_year__gte=(now.year - 6)).count()
        age_range_1['7-9'] = self.queryset.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_1['10-12'] = self.queryset.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_1['13+'] = self.queryset.filter(school__location__parent_id=1, student__birthday_year__lte=(now.year - 13)).count()

        age_range_2 = {}
        age_range_2['0-6'] = self.queryset.filter(school__location__parent_id=2, student__birthday_year__gte=(now.year - 6)).count()
        age_range_2['7-9'] = self.queryset.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_2['10-12'] = self.queryset.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_2['13+'] = self.queryset.filter(school__location__parent_id=2, student__birthday_year__lte=(now.year - 13)).count()

        age_range_3 = {}
        age_range_3['0-6'] = self.queryset.filter(school__location__parent_id=3, student__birthday_year__gte=(now.year - 6)).count()
        age_range_3['7-9'] = self.queryset.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_3['10-12'] = self.queryset.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_3['13+'] = self.queryset.filter(school__location__parent_id=3, student__birthday_year__lte=(now.year - 13)).count()

        age_range_4 = {}
        age_range_4['0-6'] = self.queryset.filter(school__location__parent_id=4, student__birthday_year__gte=(now.year - 6)).count()
        age_range_4['7-9'] = self.queryset.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_4['10-12'] = self.queryset.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_4['13+'] = self.queryset.filter(school__location__parent_id=4, student__birthday_year__lte=(now.year - 13)).count()

        age_range_5 = {}
        age_range_5['0-6'] = self.queryset.filter(school__location__parent_id=5, student__birthday_year__gte=(now.year - 6)).count()
        age_range_5['7-9'] = self.queryset.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_5['10-12'] = self.queryset.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_5['13+'] = self.queryset.filter(school__location__parent_id=5, student__birthday_year__lte=(now.year - 13)).count()

        age_range_6 = {}
        age_range_6['0-6'] = self.queryset.filter(school__location__parent_id=6, student__birthday_year__gte=(now.year - 6)).count()
        age_range_6['7-9'] = self.queryset.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_6['10-12'] = self.queryset.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_6['13+'] = self.queryset.filter(school__location__parent_id=6, student__birthday_year__lte=(now.year - 13)).count()

        age_range_7 = {}
        age_range_7['0-6'] = self.queryset.filter(school__location__parent_id=7, student__birthday_year__gte=(now.year - 6)).count()
        age_range_7['7-9'] = self.queryset.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_7['10-12'] = self.queryset.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_7['13+'] = self.queryset.filter(school__location__parent_id=7, student__birthday_year__lte=(now.year - 13)).count()

        age_range_8 = {}
        age_range_8['0-6'] = self.queryset.filter(school__location__parent_id=8, student__birthday_year__gte=(now.year - 6)).count()
        age_range_8['7-9'] = self.queryset.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 7), student__birthday_year__gte=(now.year - 9)).count()
        age_range_8['10-12'] = self.queryset.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 10), student__birthday_year__gte=(now.year - 12)).count()
        age_range_8['13+'] = self.queryset.filter(school__location__parent_id=8, student__birthday_year__lte=(now.year - 13)).count()

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
    queryset = Outreach.objects.all()
    queryset = queryset.filter(registered_in_level__isnull=False)
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
        alp_round = ALPRound.objects.get(current_round=True)
        self.queryset = self.queryset.filter(alp_round=alp_round)

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


class RegistrationsALPOverallView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Outreach
    queryset = Outreach.objects.all()
    template_name = 'dashboard/alp-overall.html'

    group_required = [u"ALP_MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        alp_round = ALPRound.objects.get(current_round=True)
        post_test_round = ALPRound.objects.get(current_post_test=True)
        enrolled = self.queryset.filter(registered_in_level__isnull=False, alp_round=alp_round)

        partners = User.objects.filter(groups__name__in=['PARTNER'])
        outreached = self.model.objects.filter(alp_round=alp_round, owner__in=partners)

        not_schools = User.objects.filter(groups__name__in=['PARTNER', 'CERD'])
        pretested = self.model.objects.filter(
            alp_round=alp_round,
            owner__in=not_schools,
            level__isnull=False,
            assigned_to_level__isnull=False,
        )

        posttested = self.queryset.filter(
            alp_round=post_test_round,
            registered_in_level__isnull=False,
            refer_to_level__isnull=False
        )

        referred_to_formal = self.queryset.filter(
            alp_round=post_test_round,
            registered_in_level__isnull=False,
            refer_to_level_id__in=[1, 10, 11, 12, 13, 14, 15, 16, 17]
        )

        referred_to_following = self.queryset.filter(
            alp_round=post_test_round,
            registered_in_level__isnull=False,
            refer_to_level_id__in=[2, 3, 4, 5, 6, 7, 8, 9]
        )

        repeated_level = self.queryset.filter(
            alp_round=post_test_round,
            registered_in_level__isnull=False,
            refer_to_level_id__in=[18, 19, 20, 21, 22, 23, 24, 25, 26]
        )

        passed_level = self.queryset.filter(
            alp_round=post_test_round,
            registered_in_level__isnull=False,
            refer_to_level_id__in=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        )

        old_enrolled = self.queryset.filter(
            alp_round=alp_round,
            registered_in_level__isnull=False,
        ).extra(where={
                'alp_outreach.student_id IN (Select distinct s.id from students_student s, alp_outreach e where s.id=e.student_id group by s.id having count(*) > 1)'
            }).distinct()

        new_enrolled = self.queryset.filter(
            alp_round=alp_round,
            registered_in_level__isnull=False,
        ).extra(where={
                'alp_outreach.student_id IN (Select distinct s.id from students_student s, alp_outreach e where s.id=e.student_id group by s.id having count(*) = 1)'
        }).distinct()

        return {
                'enrolled': enrolled.count(),
                'enrolled_males': enrolled.filter(student__sex='Male').count(),
                'enrolled_females': enrolled.filter(student__sex='Female').count(),
                'outreached': outreached.count(),
                'outreached_males': outreached.filter(student__sex='Male').count(),
                'outreached_females': outreached.filter(student__sex='Female').count(),
                'pretested': pretested.count(),
                'pretested_males': pretested.filter(student__sex='Male').count(),
                'pretested_females': pretested.filter(student__sex='Female').count(),
                'posttested': posttested.count(),
                'posttested_males': posttested.filter(student__sex='Male').count(),
                'posttested_females': posttested.filter(student__sex='Female').count(),
                'referred_to_formal': referred_to_formal.count(),
                'referred_to_formal_males': referred_to_formal.filter(student__sex='Male').count(),
                'referred_to_formal_females': referred_to_formal.filter(student__sex='Female').count(),
                'referred_to_following': referred_to_following.count(),
                'referred_to_following_males': referred_to_following.filter(student__sex='Male').count(),
                'referred_to_following_females': referred_to_following.filter(student__sex='Female').count(),
                'repeated_level': repeated_level.count(),
                'repeated_level_males': repeated_level.filter(student__sex='Male').count(),
                'repeated_level_females': repeated_level.filter(student__sex='Female').count(),
                'passed_level': passed_level.count(),
                'passed_level_males': passed_level.filter(student__sex='Male').count(),
                'passed_level_females': passed_level.filter(student__sex='Female').count(),
                'old_enrolled': old_enrolled.count(),
                'old_enrolled_males': old_enrolled.filter(student__sex='Male').count(),
                'old_enrolled_females': old_enrolled.filter(student__sex='Female').count(),
                'new_enrolled': new_enrolled.count(),
                'new_enrolled_males': new_enrolled.filter(student__sex='Male').count(),
                'new_enrolled_females': new_enrolled.filter(student__sex='Female').count(),
                'alp_round': alp_round,
        }


class RegistrationsALPOutreachView(LoginRequiredMixin,
                                   GroupRequiredMixin,
                                   TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Outreach
    queryset = Outreach.objects.all()
    template_name = 'dashboard/registrations-alp-outreach.html'

    group_required = [u"ALP_MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        governorates = Location.objects.exclude(parent__isnull=False)

        alp_round = ALPRound.objects.filter(current_pre_test=True)
        users = User.objects.filter(groups__name__in=['PARTNER'])
        self.queryset = self.queryset.filter(alp_round=alp_round, owner__in=users)

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


class RegistrationsALPPreTestView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Outreach
    queryset = Outreach.objects.all()
    template_name = 'dashboard/registrations-alp-pre-test.html'

    group_required = [u"ALP_MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        governorates = Location.objects.exclude(parent__isnull=False)

        alp_round = ALPRound.objects.get(current_pre_test=True)
        not_schools = User.objects.filter(groups__name__in=['PARTNER', 'CERD'])
        self.queryset = self.queryset.filter(
            alp_round=alp_round,
            owner__in=not_schools,
            level__isnull=False,
            assigned_to_level__isnull=False,
        )

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


class RegistrationsALPPostTestView(LoginRequiredMixin,
                                   GroupRequiredMixin,
                                   TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Outreach
    queryset = Outreach.objects.all()
    template_name = 'dashboard/registrations-alp-post-test.html'

    group_required = [u"ALP_MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        governorates = Location.objects.exclude(parent__isnull=False)

        alp_round = ALPRound.objects.get(current_post_test=True)
        self.queryset = self.queryset.filter(
            alp_round=alp_round,
            registered_in_level__isnull=False,
            section__isnull=False,
            refer_to_level__isnull=False
        )

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
