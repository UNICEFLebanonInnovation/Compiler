# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import datetime
import json

from django.views import View
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render

from braces.views import GroupRequiredMixin
from rest_framework import viewsets, mixins, permissions
from rest_framework.generics import ListAPIView
from rest_framework import status

from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    EducationLevel
)
from student_registration.enrollments.models import (
    Enrollment,
    EducationYear,
)
from student_registration.alp.models import Outreach
from student_registration.backends.tasks import export_attendance
from student_registration.users.utils import force_default_language
from .utils import find_attendances, calculate_absentees
from .models import Attendance, Absentee
from .serializers import AttendanceSerializer, AbsenteeSerializer


class AttendanceViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):

    model = Attendance
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_superuser:
            if self.request.user.school:
                return self.queryset.filter(school_id=self.request.user.school.id)
            else:
                return []

        return self.queryset

    def list(self, request, *args, **kwargs):
        if self.request.GET.get('from_date', None) and self.request.GET.get('to_date', None):
            data = find_attendances(governorate=self.request.GET.get('governorate', None),
                                    student_id=self.request.GET.get('student', None),
                                    from_date=self.request.GET.get('from_date', None),
                                    to_date=self.request.GET.get('to_date', None),
                                    filter_by_status=request.GET.get('status', False)
                                    )
            return JsonResponse(json.dumps(data), safe=False)

        return JsonResponse({'status': status.HTTP_200_OK})

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        try:
            instance = Attendance.objects.get(school=int(request.POST.get('school')),
                                              attendance_date=request.POST.get('attendance_date'),
                                              school_type=request.POST.get('school_type'))
            return JsonResponse({'status': status.HTTP_200_OK, 'data': instance.id})
        except Attendance.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.instance = serializer.save()
            return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.instance.id})

    def update(self, request, *args, **kwargs):
        if 'pk' not in kwargs:
            return super(AttendanceViewSet, self).update(request)
        instance = self.model.objects.get(id=kwargs['pk'])
        data = {}
        level_section = ''
        if request.data.keys():
            data = json.loads(request.data.keys()[0], "utf-8")
            level_section = data.keys()[0]
        if not instance.students:
            instance.students = data
        elif level_section:
            instance.students[level_section] = data[level_section]
        instance.save()
        # calculate_absentees(instance, data[level_section]['students'])
        return JsonResponse({'status': status.HTTP_200_OK, 'data': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        return super(AttendanceViewSet, self).partial_update(request)


class AbsenteeViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    model = Absentee
    queryset = Absentee.objects.all()
    serializer_class = AbsenteeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.GET.get('days', None):
            return self.queryset.filter(absent_days__lte=self.request.GET.get('days', None))
        return []

    # def list(self, request, *args, **kwargs):
    #     if self.request.GET.get('days', None):
    #         return self.queryset.filter(absent_days=self.request.GET.get('days', None))
    #     return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     ListView):

    model = Attendance
    template_name = 'attendances/school_day.html'
    group_required = [u"ATTENDANCE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        level = 0
        section = 0
        school = 0
        levels_by_sections = []
        attendance_students = []
        attendance_status = {}
        students = []
        date_format = '%Y-%m-%d'
        date_format_display = '%A %d/%m/%Y'

        if self.request.user.school:
            school = self.request.user.school

        if not school.academic_year_start:
            messages.warning(self.request, _('Please go to the school profile and enter the academic start date '
                                             'in order to take attendance.'))
            self.template_name = 'error.html'
            return {
            }

        current_date = datetime.datetime.now().strftime(date_format)
        selected_date = self.request.GET.get('date', current_date)
        selected_date_obj = datetime.datetime.strptime(selected_date, date_format).date()
        selected_date_view = datetime.datetime.strptime(selected_date, date_format).strftime(date_format_display)

        try:
            attendance = Attendance.objects.get(
                school_id=school.id,
                attendance_date=selected_date,
                school_type='2nd-shift'
            )
        except Attendance.DoesNotExist:
            attendance = ''

        if self.request.GET.get('level', 0):
            level = ClassRoom.objects.get(id=int(self.request.GET.get('level', 0)))
            self.template_name = 'attendances/level_section.html'
        if self.request.GET.get('section', 0):
            section = Section.objects.get(id=int(self.request.GET.get('section', 0)))

        education_year = EducationYear.objects.get(current_year=True)
        queryset = Enrollment.objects.exclude(last_moved_date__lt=selected_date,
                                              moved=True).filter(school_id=school, education_year=education_year)
        # queryset = Enrollment.objects.exclude(moved=True).filter(school_id=school, education_year=education_year)
        registrations = queryset.filter(
            classroom__isnull=False,
            section__isnull=False
        ).distinct().values(
            'classroom__name',
            'classroom_id',
            'section__name',
            'section_id'
        ).order_by('classroom_id')

        current_level_section = ''
        disable_attendance = False
        for registry in registrations:
            exam_day = False
            not_attending = False
            school_closed = attendance.close_reason if attendance else False
            validation_date = attendance.validation_date if attendance else ''
            total_attended = 0
            total_absences = 0
            attendance_taken = False
            level_section = '{}-{}'.format(registry['classroom_id'], registry['section_id'])
            attendances = attendance.students[
                level_section] if attendance and attendance.students and level_section in attendance.students else ''
            total = queryset.filter(classroom_id=registry['classroom_id'],
                                    section_id=registry['section_id'],
                                    registration_date__lte=selected_date).count()
            if total == 0:
                continue

            if attendances:
                attendance_taken = True
                total = attendances['total_enrolled']
                total_attended = attendances['total_attended']
                total_absences = attendances['total_absences']
                exam_day = attendances['exam_day'] if 'exam_day' in attendances else False
                not_attending = attendances['not_attending'] if 'not_attending' in attendances else False
                for value in attendances['students']:
                    attendance_status[value['student_id']] = value

            level_by_section = {
                'level_name': registry['classroom__name'],
                'level': registry['classroom_id'],
                'section_name': registry['section__name'],
                'section': registry['section_id'],
                'total': total,
                'total_attended': total_attended,
                'total_absences': total_absences,
                'exam_day': exam_day,
                'not_attending': not_attending,
                'validation_date': validation_date,
                'disable_attendance': disable_attendance,
                'attendance_taken': attendance_taken,
                'school_closed': school_closed
            }

            if level and section and level.id == registry['classroom_id'] \
                     and section.id == registry['section_id']:
                current_level_section = level_by_section
                if exam_day or not_attending or (attendance and attendance.validation_date) or school_closed:
                    disable_attendance = True

            levels_by_sections.append(level_by_section)

        if attendance and (attendance.validation_date or attendance.close_reason):
            disable_attendance = True

        if level and section:
            students = queryset.filter(classroom_id=level.id,
                                       section_id=section.id,
                                       registration_date__lte=selected_date,
                                       ).order_by('student__first_name', 'student__father_name', 'student__last_name')
            for line in students:
                student = line.student
                if str(student.id) in attendance_status:
                    student_status = attendance_status[str(student.id)]
                    line.attendance_status = student_status['status'] if 'status' in student_status else True
                    line.absence_reason = student_status['absence_reason'] if 'absence_reason' in student_status else ''
                    attendance_students.append(line)

        base = datetime.datetime.now()
        dates = []
        if school.attendance_from_beginning:
            start_date = school.academic_year_start
            end_date = datetime.date(base.year, base.month, base.day)
            delta = end_date - start_date
            day_range = delta.days + 1
        else:
            day_range = school.attendance_range if school.attendance_range else Attendance.DEFAULT_ATTENDANCE_RANGE

        for x in range(0, day_range):
            d = base - datetime.timedelta(days=x)
            dates.append({
                'value': d.strftime(date_format),
                'label': d.strftime(date_format_display)
            })

        return {
            'school_type': '2nd-shift',
            'attendance': attendance,
            'disable_attendance': disable_attendance,
            'current_level_section': current_level_section,
            'total': queryset.count(),
            'total_students': students.count() if students else 0,
            'students': students,
            'school': school,
            'level': level,
            'section': section,
            'dates': dates,
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'levels_by_sections': levels_by_sections,
            'selected_date': selected_date,
            'selected_date_view': selected_date_view,
        }


class AbsenteeView(ListAPIView):
    """
    API endpoint for validated absentees
    """
    queryset = Absentee.objects.filter(
        school__location=True
    )
    serializer_class = AbsenteeSerializer
    permission_classes = (permissions.IsAdminUser,)


class AttendanceALPView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        ListView):

    model = Attendance
    template_name = 'attendances/school_day.html'
    group_required = [u"ATTENDANCE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        level = 0
        section = 0
        school = 0
        levels_by_sections = []
        attendance_students = []
        attendance_status = {}
        students = []
        date_format = '%Y-%m-%d'
        date_format_display = '%A %d/%m/%Y'

        if self.request.user.school:
            school = self.request.user.school

        if not school.academic_year_start:
            messages.warning(self.request, _('Please go to the school profile and enter the academic start date in order to take attendance.'))
            self.template_name = 'error.html'
            return {
            }

        current_date = datetime.datetime.now().strftime(date_format)
        selected_date = self.request.GET.get('date', current_date)
        selected_date_view = datetime.datetime.strptime(selected_date, date_format).strftime(date_format_display)

        try:
            attendance = Attendance.objects.get(
                school_id=school.id,
                attendance_date=selected_date,
                school_type='ALP'
            )
        except Attendance.DoesNotExist:
            attendance = ''

        if self.request.GET.get('level', 0):
            level = EducationLevel.objects.get(id=int(self.request.GET.get('level', 0)))
            self.template_name = 'attendances/level_section.html'
        if self.request.GET.get('section', 0):
            section = Section.objects.get(id=int(self.request.GET.get('section', 0)))

        queryset = Outreach.objects.filter(school_id=school, alp_round__current_round=True)
        registrations = queryset.filter(
            registered_in_level__isnull=False,
            section__isnull=False
        ).distinct().values(
            'registered_in_level__name',
            'registered_in_level_id',
            'section__name',
            'section_id'
        ).order_by('registered_in_level_id')

        current_level_section = ''
        disable_attendance = False
        for registry in registrations:
            exam_day = False
            not_attending = False
            school_closed = attendance.close_reason if attendance else False
            validation_date = attendance.validation_date if attendance else ''
            total_attended = 0
            total_absences = 0
            attendance_taken = False
            level_section = '{}-{}'.format(registry['registered_in_level_id'], registry['section_id'])
            attendances = attendance.students[level_section] if attendance \
                                                             and attendance.students \
                                                             and level_section in attendance.students else ''
            total = queryset.filter(registered_in_level_id=registry['registered_in_level_id'],
                                    section_id=registry['section_id']).count()

            if attendances:
                attendance_taken = True
                total = attendances['total_enrolled']
                total_attended = attendances['total_attended']
                total_absences = attendances['total_absences']
                exam_day = attendances['exam_day'] if 'exam_day' in attendances else False
                not_attending = attendances['not_attending'] if 'not_attending' in attendances else False
                for value in attendances['students']:
                    attendance_status[value['student_id']] = value

            level_by_section = {
                'level_name': registry['registered_in_level__name'],
                'level': registry['registered_in_level_id'],
                'section_name': registry['section__name'],
                'section': registry['section_id'],
                'total': total,
                'total_attended': total_attended,
                'total_absences': total_absences,
                'exam_day': exam_day,
                'not_attending': not_attending,
                'validation_date': validation_date,
                'disable_attendance': disable_attendance,
                'attendance_taken': attendance_taken,
                'school_closed': school_closed
            }

            if level and section and level.id == registry['registered_in_level_id'] and section.id == registry['section_id']:
                current_level_section = level_by_section
                if exam_day or not_attending or (attendance and attendance.validation_date) or school_closed:
                    disable_attendance = True

            levels_by_sections.append(level_by_section)

        if attendance and (attendance.validation_date or attendance.close_reason):
            disable_attendance = True

        if level and section:
            students = queryset.filter(registered_in_level_id=level.id, section_id=section.id,
                                       ).order_by('student__first_name', 'student__father_name', 'student__last_name')
            for line in students:
                student = line.student
                if str(student.id) in attendance_status:
                    student_status = attendance_status[str(student.id)]
                    line.attendance_status = student_status['status'] if 'status' in student_status else True
                    line.absence_reason = student_status['absence_reason'] if 'absence_reason' in student_status else ''
                    attendance_students.append(line)

        base = datetime.datetime.now()
        dates = []
        if school.attendance_from_beginning:
            start_date = school.academic_year_start
            end_date = datetime.date(base.year, base.month, base.day)
            delta = end_date - start_date
            day_range = delta.days + 1
        else:
            day_range = school.attendance_range if school.attendance_range else Attendance.DEFAULT_ATTENDANCE_RANGE

        for x in range(0, day_range):
            d = base - datetime.timedelta(days=x)
            dates.append({
                'value': d.strftime(date_format),
                'label': d.strftime(date_format_display)
            })

        return {
            'school_type': 'ALP',
            'attendance': attendance,
            'disable_attendance': disable_attendance,
            'current_level_section': current_level_section,
            'total': queryset.count(),
            'total_students': students.count() if students else 0,
            'students': students,
            'school': school,
            'level': level,
            'section': section,
            'dates': dates,
            'classrooms': EducationLevel.objects.all(),
            'sections': Section.objects.all(),
            'levels_by_sections': levels_by_sections,
            'selected_date': selected_date,
            'selected_date_view': selected_date_view,
        }


class ExportView(LoginRequiredMixin, ListView):

    model = Attendance
    queryset = Attendance.objects.all()

    def get(self, request, *args, **kwargs):

        date_format = '%Y-%m-%d'
        current_date = datetime.datetime.now().strftime(date_format)
        selected_date = self.request.GET.get('date', current_date)
        school_type = self.request.GET.get('school_type', '2nd-shift')

        school = self.request.user.school_id
        # data = export_attendance({'date': selected_date, 'school': school, 'school_type': school_type}, return_data=True)
        data = export_attendance({'school_type': school_type}, return_data=True)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=attendance_'+selected_date+'.xlsx'
        return response
