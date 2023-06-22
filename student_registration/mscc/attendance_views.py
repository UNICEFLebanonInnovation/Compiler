# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import EducationService
from .utils import load_child_attendance, create_attendance


class AttendanceView(LoginRequiredMixin, TemplateView):

    template_name = 'mscc/attendance.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime
        from collections import OrderedDict

        center_id = self.request.user.center_id
        attendance_date = datetime.now().strftime('%m/%d/%Y')
        day_off = 'No'
        close_reason = ''

        education_programs = EducationService.EDUCATION_PROGRAM
        sorted_education_programs = sorted(education_programs, key=lambda x: x[1])
        education_program_dict = OrderedDict(sorted_education_programs)

        class_sections = EducationService.CLASS_SECTION
        sorted_class_sections = sorted(class_sections, key=lambda x: x[1])
        class_section_dict = OrderedDict(sorted_class_sections)


        instance = MSCCAttendance.objects.filter(center_id=center_id,
                                                 attendance_date=datetime.now()).last()

        if instance:
            day_off = instance.day_off
            close_reason = instance.close_reason

        return {
            'instance': instance,
            'attendance_date': attendance_date,
            'day_off': day_off,
            'close_reason': close_reason,
            'education_program': education_program_dict,
            'class_section': class_section_dict
        }



def save_attendance_children(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    result = create_attendance(data, request.GET.get('center_id'))
    return JsonResponse({'result': result})


class LoadAttendanceChildren(LoginRequiredMixin,
                             TemplateView):

    template_name = 'mscc/attendance_children.html'

    def get_context_data(self, **kwargs):

        center_id = self.request.GET.get("center_id")
        attendance_date = self.request.GET.get("attendance_date")
        education_program = self.request.GET.get("education_program")
        class_section = self.request.GET.get("class_section")

        instances = load_child_attendance(center_id, attendance_date, education_program, class_section)

        return {
            'instances': instances
        }


class LoadAttendanceChild(LoginRequiredMixin,
                          TemplateView):

    template_name = 'mscc/child_attendance_month.html'

    def get_context_data(self, **kwargs):
        import calendar

        child_id = kwargs["child"]
        month = int(self.request.GET.get("month"))

        instances = MSCCAttendanceChild.objects.filter(child_id=child_id,
                                                       attendance_day__attendance_date__month=month)\
            .order_by('attendance_day__attendance_date')

        return {
            'instances': instances,
            'nbr_attended': instances.filter(attended='Yes').count(),
            'nbr_absent': instances.filter(attended='No').count(),
            'attendance_month': calendar.month_name[month]
        }
