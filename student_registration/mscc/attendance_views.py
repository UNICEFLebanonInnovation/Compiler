# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.template.loader import render_to_string




from .models import Registration
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild

import json

from .utils import *


class AttendanceView(LoginRequiredMixin,
                     TemplateView):
    template_name = 'mscc/attendance.html'

    def get_context_data(self, **kwargs):

        return {
        }

    # def post(self, request, *args, **kwargs):
    #
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     attendance_child_formset = self.get_child_formset(self.request.POST)
    #     child_count = len(attendance_child_formset)
    #     if self.request.POST['day_off'] == 'yes' and child_count > 0:
    #         form.add_error('day_off', 'Day is off')
    #
    #     if form.is_valid() and attendance_child_formset.is_valid():
    #         return self.form_valid(form, attendance_child_formset)
    #     else:
    #         return self.form_invalid(form, attendance_child_formset)



def save_attendance_children(request):
    data = json.loads(request.body)
    result = create_attendance(data, request.GET.get('center_id'))
    return JsonResponse({'result': result})


def LoadAttendanceChildren(request):
    from datetime import datetime
    template_name = 'mscc/attendance_children.html'
    data = json.loads(request.body)
    center_id = request.GET.get('center_id')
    attendance_date = data["attendance_date"]

    attendance = MSCCAttendance.objects.filter(center_id=center_id,
                                               attendance_date=datetime.strptime(attendance_date, '%m/%d/%Y')).values(
        'id',
        'day_off',
        'close_reason'
    ).last()
    if not attendance:
        instances = load_child_registration_information(center_id)
        attendance_id= 0,
        attendance_day_off = ''
        attendance_close_reason = ''
    else:
        attendance_id = attendance['id']
        instances = load_child_attendance_information(attendance_id)
        attendance_id = attendance_id
        attendance_day_off = attendance['day_off']
        attendance_close_reason =  attendance['close_reason']

    templateData = {
        'instances': instances,
    }

    html = render_to_string(template_name, templateData)

    return JsonResponse({'ChildrenView': html, 'attendance_id': attendance_id, 'attendance_day_off': attendance_day_off, 'attendance_close_reason': attendance_close_reason})

