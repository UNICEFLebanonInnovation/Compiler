# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from student_registration.attendances.models import MSCCAttendance
from .utils import load_child_attendance, create_attendance


class AttendanceView(LoginRequiredMixin,
                     TemplateView):
    template_name = 'mscc/attendance.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime
        center_id = self.request.user.center_id
        attendance_date = datetime.now().strftime('%m/%d/%Y')
        day_off = 'No'
        close_reason = ''

        instance = MSCCAttendance.objects.filter(center_id=center_id,
                                                 attendance_date=datetime.now()).last()

        if instance:
            day_off = instance.day_off
            close_reason = instance.close_reason

        return {
            'instance': instance,
            'attendance_date': attendance_date,
            'day_off': day_off,
            'close_reason': close_reason
        }


def save_attendance_children(request):
    data = json.loads(request.body)
    result = create_attendance(data, request.GET.get('center_id'))
    return JsonResponse({'result': result})


class LoadAttendanceChildren(LoginRequiredMixin,
                             TemplateView):

    template_name = 'mscc/attendance_children.html'

    def get_context_data(self, **kwargs):

        center_id = self.request.GET.get("center_id")
        attendance_date = self.request.GET.get("attendance_date")

        instances = load_child_attendance(center_id, attendance_date)

        return {
            'instances': instances
        }
