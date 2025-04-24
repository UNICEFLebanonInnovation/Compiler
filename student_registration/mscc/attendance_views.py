# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import EducationService, Round
from student_registration.locations.models import Center
from student_registration.schools.models import PartnerOrganization

from .utils import load_child_attendance, create_attendance


class AttendanceView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     TemplateView):

    group_required = [u"MSCC",u"MSCC_UNICEF", u"MSCC_CENTER", "MSCC_PARTNER"]
    template_name = 'mscc/attendance.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime
        from collections import OrderedDict

        center_id = self.request.user.center_id
        attendance_date = datetime.now().strftime('%m/%d/%Y')
        day_off = 'No'
        close_reason = ''
        round = Round.objects.filter(current_year=True)

        education_programs = EducationService.EDUCATION_PROGRAM
        sorted_education_programs = sorted(education_programs, key=lambda x: x[1])
        education_program_dict = OrderedDict(sorted_education_programs)

        class_sections = EducationService.CLASS_SECTION
        sorted_class_sections = sorted(class_sections, key=lambda x: x[1])
        class_section_dict = OrderedDict(sorted_class_sections)

        instance = None

        if center_id:
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
            'class_section': class_section_dict,
            'round': round
        }


def save_attendance_children(request):
    body_unicode = request.body.decode('utf-8')

    if body_unicode.strip():
        try:
            data = json.loads(body_unicode)
            result = create_attendance(data, request.GET.get('center_id'))
            return JsonResponse({'result': result})

        except Exception as e:
            pass


class LoadAttendanceChildren(LoginRequiredMixin,
                             TemplateView):

    template_name = 'mscc/attendance_children.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime

        current_date = datetime.today().date()
        attendance_date_str = self.request.GET.get("attendance_date")
        center_id = self.request.GET.get("center_id")
        education_program = self.request.GET.get("education_program")
        class_section = self.request.GET.get("class_section")
        round_id = self.request.GET.get("round_id")

        if attendance_date_str is None:
            return {'instances': []}

        try:
            # Parse the attendance_date_str into a datetime object
            attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            if attendance_date <= current_date and center_id:
                instances = load_child_attendance(center_id, round_id, attendance_date_str, education_program, class_section)
            else:
                instances = []
        except ValueError:
            instances = []

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


class AttendanceReport(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/attendance_report.html'

    def get_context_data(self, **kwargs):
        from collections import OrderedDict

        context = super(AttendanceReport, self).get_context_data(**kwargs)

        context['rounds'] = Round.objects.filter(current_year=True).all()

        education_programs = EducationService.EDUCATION_PROGRAM
        sorted_education_programs = sorted(education_programs, key=lambda x: x[1])
        education_program_dict = OrderedDict(sorted_education_programs)
        context['education_program'] = education_program_dict

        class_sections = EducationService.CLASS_SECTION
        sorted_class_sections = sorted(class_sections, key=lambda x: x[1])
        class_section_dict = OrderedDict(sorted_class_sections)
        context['class_section'] = class_section_dict

        context['center'] = []
        context['partner'] = []

        if not self.request.user.groups.filter(name='MSCC_UNICEF').exists():
            if self.request.user.center_id:
                center = Center.objects.filter(id=self.request.user.center_id).last()
                if center:
                    context['center'] = [center]
                    context['partner'] = PartnerOrganization.objects.filter(id=center.partner_id).all()
        else:
            context['center'] = Center.objects.all()
            context['partner'] = PartnerOrganization.objects.all()

        return context
