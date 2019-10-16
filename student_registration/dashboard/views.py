# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User
from student_registration.backends.djqscsv import render_to_csv_response
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import render

import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.shortcuts import render
from student_registration.locations.models import (
    Location,
)
from student_registration.schools.models import (
    School,
    EducationYear,
    EducationLevel,
    ClassLevel,
    ClassRoom,
)

from student_registration.alp.models import Outreach, ALPRound
from student_registration.users.models import User
from student_registration.backends.exporter import export_full_data


class ExporterView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):

    template_name = 'dashboard/exporter.html'

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        return {
            'alp_rounds': ALPRound.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'education_years': EducationYear.objects.all()
        }


class RunExporterViewSet(LoginRequiredMixin,
                         GroupRequiredMixin,
                         ListView):

    group_required = [u"MEHE"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get(self, request, *args, **kwargs):
        return export_full_data(self.request.GET)


def fill_data(request, *args):
    from student_registration.enrollments.models import Enrollment
    from student_registration.schools.models import ClassRoom

    T_Enrollment = Enrollment.objects.filter(created__gt='2019-10-9', created__lt='2019-10-11', school_id__isnull=True,
                                             education_year_id__isnull=True)# classroom_id__isnull=True,
    for T_Enr in T_Enrollment:
        try:
            last_enrollment = Enrollment.objects.filter(student_id=T_Enr.student_id, education_year_id=1).order_by('-created')[:1]
            for line in last_enrollment:
                T_Enr.school_id = line.school_id
                T_Enr.education_year_id = 4

                try:
                    last_class = ClassRoom.objects.filter(id__gt=line.classroom_id)[:1]
                    for v_class in last_class:
                        T_Enr.classroom_id = v_class.id
                except ClassRoom.DoesNotExist:
                    False
                T_Enr.owner_id = line.owner_id
                T_Enr.save()
        except Enrollment.DoesNotExist:
            continue
    context = {}
    return render(request, "dashboard/exporter.html", context)


def run_attendance(request):
    from student_registration.attendances.tasks import geo_calculate_attendances_by_student,\
        geo_calculate_last_attendance_date
    from_school = request.GET['txtfromschool']
    to_school = request.GET['txttoschool']
    from_date = request.GET['txtfromdate']
    to_date = request.GET['txttodate']
    if request.GET.get('btn_lastattendance') == 'Generate':
        geo_calculate_attendances_by_student(from_school, to_school, from_date, to_date)
        geo_calculate_last_attendance_date(from_school, to_school)
        messages.add_message(request, messages.INFO, 'Finished !')
        context = {}
        return render(request, "dashboard/exporter.html", context)
    else:
        from student_registration.enrollments.models import Enrollment
        queryset = Enrollment.objects.filter(education_year__current_year=True).order_by('school__number')
        queryset = queryset.filter(school__number__gte=from_school, school__number__lte=to_school)
        headers = {
            'school__number': _('School number'),
            'school__name': _('School'),
            'school__location__name': _('District'),
            'school__location__parent__name': _('Governorate'),
            'student__number': 'student number',
            'student__first_name': _('Student first name'),
            'student__father_name': _('Student father name'),
            'student__last_name': _('Student last name'),
            'student__mother_fullname': _('Mother fullname'),
            'student__sex': _('Sex'),
            'student__birthday_year': _('year'),
            'student__birthday_month': _('month'),
            'student__birthday_day': _('day'),
            'student__place_of_birth': _('Place of birth'),
            'student__phone': _('Phone number'),
            'student__phone_prefix': _('Phone prefix'),
            'student__id_number': _('Student ID Number'),
            'student__nationality__name': _('Student nationality'),
            'section__name': _('Current Section'),
            'classroom__name': _('Current Class'),
            'last_attendance_date': _('Last attendance date'),
            'last_absent_date': _('Last absent date'),
            'dropout_status': _('dropout status'),
            'dropout_date': _('dropout date'),
            'moved': _('moved'),
            'last_moved_date': _('last moved date'),
            }
        queryset = queryset.values(
            'school__number',
            'school__name',
            'school__location__name',
            'school__location__parent__name',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__sex',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__place_of_birth',
            'student__phone',
            'student__phone_prefix',
            'student__id_number',
            'student__nationality__name',
            'section__name',
            'classroom__name',
            'last_attendance_date',
            'last_absent_date',
            'dropout_status',
            'dropout_date',
            'moved',
            'last_moved_date',
            )
        return render_to_csv_response(queryset, field_header_map=headers)


def run_to_excel_per_day(request):
    from student_registration.attendances.tasks import geo_calculate_attendances_per_day
    from student_registration.attendances.models import AttendanceDt
    from student_registration.students.models import Student
    from_school = request.GET['txt_from_school']
    to_school = request.GET['txt_to_school']
    from_date = request.GET['txt_from_date']
    to_date = request.GET['txt_to_date']
    txt_std = request.GET['txt_student']
    if request.GET.get('btntype') == 'Generate':
        geo_calculate_attendances_per_day(from_school, to_school, from_date, to_date, txt_std)
        messages.add_message(request, messages.INFO, 'Finished !')
        context = {}
        return render(request, "dashboard/exporter.html", context)
    else:
        if txt_std:
            std_id = ()
            std = Student.objects.filter(number=txt_std)
            for st in std:
                std_id = st.id,
            qs_attendancedt = AttendanceDt.objects.filter(attendance_date__gte=from_date, attendance_date__lte=to_date,
                                                          school__number__gte=from_school, school__number__lte=to_school,
                                                          student_id__in=std_id).\
                order_by('attendance_date', 'school__number')
        else:
            qs_attendancedt = AttendanceDt.objects.filter(attendance_date__gte=from_date, attendance_date__lte=to_date,
                                                          school__number__gte=from_school, school__number__lte=to_school
                                                          ).order_by('attendance_date', 'school__number')

    headers = {
        'school__number': _('School number'),
        'school__name': _('School'),
        'school__location__name': _('District'),
        'school__location__parent__name': _('Governorate'),
        'student__number': 'student number',
        'student__first_name': _('Student first name'),
        'student__father_name': _('Student father name'),
        'student__last_name': _('Student last name'),
        'student__mother_fullname': _('Mother fullname'),
        'student__sex': _('Sex'),
        'student__birthday_year': _('year'),
        'student__birthday_month': _('month'),
        'student__birthday_day': _('day'),
        'student__place_of_birth': _('Place of birth'),
        'student__phone': _('Phone number'),
        'student__phone_prefix': _('Phone prefix'),

        'student__id_number': _('Student ID Number'),
        'student__nationality__name': _('Student nationality'),

        'section__name': _('Current Section'),
        'levelname': _('Current Class'),

        'attendance_date': _('Attendance date'),
        'is_present': _('Is Present'),

    }
    qs_attendancedt = qs_attendancedt.values(
        'school__number',
        'school__name',
        'school__location__name',
        'school__location__parent__name',
        'student__number',
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
        'student__sex',
        'student__birthday_year',
        'student__birthday_month',
        'student__birthday_day',
        'student__place_of_birth',
        'student__phone',
        'student__phone_prefix',

        'student__id_number',
        'student__nationality__name',

        'section__name',
        'levelname',

        'attendance_date',
        'is_present',

    )

    return render_to_csv_response(qs_attendancedt, field_header_map=headers)


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

        not_schools = User.objects.filter(groups__name__in=['PARTNER', 'TEST_MANAGER', 'CERD'])
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
        not_schools = User.objects.filter(groups__name__in=['PARTNER', 'TEST_MANAGER', 'CERD'])
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
