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
    EducationLevel,
    ClassLevel,
    ClassRoom,
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

        education_levels = ClassRoom.objects.all()

        return {
                'schools': 0,
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'education_levels': education_levels,
                'governorates': governorates,
                'enrollments': self.queryset,
        }


class Registrations2ndShiftOverallView(LoginRequiredMixin,
                                       GroupRequiredMixin,
                                       TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Enrollment
    queryset = Enrollment.objects.all()
    template_name = 'dashboard/2ndshift-overall.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):

        now = datetime.datetime.now()
        governorates = Location.objects.exclude(parent__isnull=False)
        education_levels = ClassRoom.objects.all()
        level_by_age = {}

        return {
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'education_levels': education_levels,
                'governorates': governorates,
                'enrollments': self.queryset,
                'level_by_age': level_by_age
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

        education_levels = EducationLevel.objects.all()

        return {
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'enrollments': self.queryset,
                'governorates': governorates,
                'education_levels': education_levels,
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

        round_id = self.request.GET.get('alp_round', 0)
        if round_id:
            alp_round = ALPRound.objects.get(id=round_id)
            post_test_round = alp_round
        else:
            alp_round = ALPRound.objects.get(current_round=True)
            post_test_round = ALPRound.objects.get(current_post_test=True)

        alp_rounds = ALPRound.objects.all()
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
            refer_to_level_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
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

        new_enrolled_test = self.queryset.filter(
            alp_round=alp_round,
            owner__in=not_schools,
            level__isnull=False,
            assigned_to_level__isnull=False,
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
                'new_enrolled_test': new_enrolled_test.count(),
                'new_enrolled_test_males': new_enrolled_test.filter(student__sex='Male').count(),
                'new_enrolled_test_females': new_enrolled_test.filter(student__sex='Female').count(),
                'alp_round': alp_round,
                'alp_rounds': alp_rounds,
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

        return {
                'schools': 0,
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
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

        return {
                'schools': 0,
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'enrollments': self.queryset,
                'governorates': governorates,
                'education_levels': EducationLevel.objects.all(),
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
            refer_to_level__isnull=False
        )

        return {
                'schools': 0,
                'registrations': self.queryset.count(),
                'males': self.queryset.filter(student__sex='Male').count(),
                'females': self.queryset.filter(student__sex='Female').count(),
                'enrollments': self.queryset,
                'governorates': governorates,
                'education_levels': ClassLevel.objects.all()
        }


class AttendanceView(LoginRequiredMixin, ListView):

    model = Registration
    template_name = 'dashboard/attendance.html'

    def get_context_data(self, **kwargs):


        return {

        }
