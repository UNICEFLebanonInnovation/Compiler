# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import calendar
import json
from collections import OrderedDict
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import EducationService, Round
from student_registration.locations.models import Center
from student_registration.schools.models import PartnerOrganization

from .utils import load_child_attendance, create_attendance
from student_registration.users.templatetags.custom_tags import has_group


def _aggregate_attendance(queryset, *group_fields):
    """Aggregate attendance counts for the provided ``group_fields``.

    This mirrors the logic used by the heatmap view to ensure the API is
    using the exact same calculations as the user-facing dashboard.
    """

    return (
        queryset
        .values(*group_fields)
        .annotate(
            total=Count('id'),
            absent=Count('id', filter=Q(attended='No'))
        )
        .order_by(*group_fields)
    )


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
    """Persist attendance for MSCC children.

    Similar to the CLM view, this now validates the request body and ensures an
    ``HttpResponse`` is always returned even when errors occur.
    """

    body_unicode = request.body.decode("utf-8")

    if not body_unicode.strip():
        return HttpResponseBadRequest("Empty request body")

    try:
        data = json.loads(body_unicode)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        result = create_attendance(data, request.GET.get("center_id"))
    except Exception:  # pragma: no cover - safety net
        return HttpResponseBadRequest("Failed to save attendance")

    return JsonResponse({"result": result})


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
            return {'instances': [], 'new_instances': []}

        try:
            # Parse the attendance_date_str into a datetime object
            attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            if attendance_date <= current_date and center_id:
                data = load_child_attendance(
                    center_id,
                    round_id,
                    attendance_date_str,
                    education_program,
                    class_section,
                )
            else:
                data = {'instances': [], 'new_instances': []}
        except ValueError:
            data = {'instances': [], 'new_instances': []}

        return data


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

        if not has_group(self.request.user, 'MSCC_UNICEF'):
            if self.request.user.center_id:
                center = Center.objects.filter(id=self.request.user.center_id).last()
                if center:
                    context['center'] = [center]
                    context['partner'] = PartnerOrganization.objects.filter(id=center.partner_id).all()
        else:
            context['center'] = Center.objects.all()
            context['partner'] = PartnerOrganization.objects.all()

        return context


class AttendanceHeatmap(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/attendance_heatmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))

        base_qs = MSCCAttendanceChild.objects.filter(
            attendance_day__attendance_date__year=year
        )

        queryset = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date',
        )

        programme_qs = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date',
            'registration__education_service__education_program',
        )

        programme_data = {}
        for row in programme_qs:
            programme = row['registration__education_service__education_program'] or 'Unknown'
            programme_data.setdefault(programme, []).append({
                'attendance_day__attendance_date': row['attendance_day__attendance_date'],
                'total': row['total'],
                'absent': row['absent'],
            })

        years = MSCCAttendanceChild.objects.dates(
            'attendance_day__attendance_date', 'year'
        )

        context['attendance_json'] = json.dumps(list(queryset), default=str)
        context['program_attendance_json'] = json.dumps(programme_data, default=str)
        context['year'] = year
        context['years'] = [d.year for d in years]
        return context


class AttendanceHeatmapAPI(LoginRequiredMixin, View):
    """Provide attendance percentages per month and per programme."""

    def get(self, request, *args, **kwargs):
        year = int(self.request.GET.get('year', timezone.now().year))

        base_qs = MSCCAttendanceChild.objects.filter(
            attendance_day__attendance_date__year=year
        )

        monthly_rows = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date__month',
        )

        monthly = []
        for row in monthly_rows:
            month = row['attendance_day__attendance_date__month']
            total = row['total'] or 0
            absent = row['absent'] or 0
            present = total - absent
            percentage = round((present * 100.0) / total, 2) if total else 0.0
            monthly.append({
                'month': month,
                'month_name': calendar.month_name[month],
                'attendance_percentage': percentage,
                'present': present,
                'absent': absent,
                'total': total,
            })

        programme_rows = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date__month',
            'registration__education_service__education_program',
        )

        programme_choices = dict(EducationService.EDUCATION_PROGRAM)
        programme_monthly = OrderedDict()

        for row in programme_rows:
            programme = row['registration__education_service__education_program'] or 'Unknown'
            label = programme_choices.get(programme, programme)
            month = row['attendance_day__attendance_date__month']
            total = row['total'] or 0
            absent = row['absent'] or 0
            present = total - absent
            percentage = round((present * 100.0) / total, 2) if total else 0.0

            if label not in programme_monthly:
                programme_monthly[label] = []

            programme_monthly[label].append({
                'month': month,
                'month_name': calendar.month_name[month],
                'attendance_percentage': percentage,
                'present': present,
                'absent': absent,
                'total': total,
            })

        for values in programme_monthly.values():
            values.sort(key=lambda item: item['month'])

        years = MSCCAttendanceChild.objects.dates(
            'attendance_day__attendance_date', 'year'
        )

        data = {
            'year': year,
            'available_years': [d.year for d in years],
            'monthly': sorted(monthly, key=lambda item: item['month']),
            'programme_monthly': programme_monthly,
        }

        return JsonResponse(data)
