# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden


from .models import Registration
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild


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


class LoadAttendanceChildren(LoginRequiredMixin,
                             TemplateView):

    template_name = 'mscc/attendance_children.html'

    def get_context_data(self, **kwargs):
        center_id = self.request.GET.get('center_id')

        instances = Registration.objects.filter(center_id=center_id)

        return {
            'instances': instances,
        }


def save_attendance_children(request):

    return JsonResponse({})
