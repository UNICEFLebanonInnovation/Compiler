# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import calendar
import json
from collections import OrderedDict

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from openpyxl import Workbook

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Count, Q, Sum, Avg, F, Func, When
from django.db.models.expressions import RawSQL
from django.urls import reverse
from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action

from .models import (
    Bridging
)
from student_registration.students.models import Teacher
from student_registration.students.serializers import TeacherSerializer
from student_registration.schools.models import (
    CLMRound,
    School,
    PartnerOrganization,
)
from student_registration.schools.serializers import SchoolSerializer
from .serializers import (
    BridgingSerializer
)
from student_registration.attendances.models import CLMAttendance, CLMAttendanceStudent
from student_registration.attendances.serializers import CLMAttendanceStudentSerializer
from student_registration.users.templatetags.custom_tags import has_group


def _aggregate_attendance_percentage(queryset, *group_fields):
    return (
        queryset
        .values(*group_fields)
        .annotate(
            total=Count('id'),
            absent=Count('id', filter=Q(attended='no')),
        )
        .order_by(*group_fields)
    )


def _build_attendance_percentage_payload(base_qs, available_years, year):
    monthly_rows = _aggregate_attendance_percentage(
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

    level_rows = _aggregate_attendance_percentage(
        base_qs,
        'attendance_day__attendance_date__month',
        'attendance_day__registration_level',
    )

    level_choices = dict(CLMAttendance.REGISTRATION_LEVEL)
    level_monthly_totals = {}

    for row in level_rows:
        level = row['attendance_day__registration_level'] or 'Unknown'
        label = level_choices.get(level, level) or 'Unknown'
        month = row['attendance_day__attendance_date__month']
        key = (label, month)
        totals = level_monthly_totals.setdefault(key, {'total': 0, 'absent': 0})
        totals['total'] += row['total'] or 0
        totals['absent'] += row['absent'] or 0

    level_monthly = OrderedDict()

    for (level, month), data in sorted(level_monthly_totals.items(), key=lambda item: (item[0][0], item[0][1])):
        total = data['total'] or 0
        absent = data['absent'] or 0
        present = total - absent
        percentage = round((present * 100.0) / total, 2) if total else 0.0

        if level not in level_monthly:
            level_monthly[level] = []

        level_monthly[level].append({
            'month': month,
            'month_name': calendar.month_name[month],
            'attendance_percentage': percentage,
            'present': present,
            'absent': absent,
            'total': total,
        })

    available_years_str = ','.join(str(item) for item in available_years)
    flat_rows = []

    for entry in sorted(monthly, key=lambda item: item['month']):
        flat_rows.append({
            'record_type': 'monthly',
            'year': year,
            'available_years': available_years_str,
            'registration_level': '',
            'programme': '',
            **entry,
        })

    for level, values in level_monthly.items():
        for entry in values:
            flat_rows.append({
                'record_type': 'level_monthly',
                'year': year,
                'available_years': available_years_str,
                'registration_level': level,
                'programme': level,
                **entry,
            })

    return flat_rows


class BridgingListViewSet(viewsets.ModelViewSet):

    queryset = Bridging.objects.all()
    serializer_class = BridgingSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = Bridging.objects.none()
        if self.request.user.partner:
            qs = Bridging.objects.filter(partner_id=self.request.user.partner_id)
            if self.request.user.school:
                qs = qs.filter(school_id=self.request.user.school_id)

        return qs


class SchoolListViewSet(viewsets.ModelViewSet):

    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = School.objects.all()
        if self.request.user.partner:
            qs = School.objects.filter(is_closed=False,
                                       id__in=PartnerOrganization
                                       .objects
                                       .filter(id=self.request.user.partner_id)
                                       .values_list('schools', flat=True))
        else:
            qs = qs.none()

        return qs


class TeacherListViewSet(viewsets.ModelViewSet):

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = Teacher.objects.all()
        if self.request.user.partner:
            qs = Teacher.objects.filter(school_id__in=PartnerOrganization
                                        .objects
                                        .filter(id=self.request.user.partner_id)
                                        .values_list('schools', flat=True))
        else:
            qs = qs.none()

        return qs


class AttendanceListViewSet(viewsets.ModelViewSet):
    queryset = CLMAttendanceStudent.objects.all()
    serializer_class = CLMAttendanceStudentSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_queryset(self):
        qs = CLMAttendanceStudent.objects.none()
        if self.request.user.partner:
            qs = CLMAttendanceStudent.objects.filter(attendance_day__school_id__in=PartnerOrganization.objects
                                                     .filter(id=self.request.user.partner_id)
                                                     .values_list('schools', flat=True))

        return qs

    @action(detail=False, methods=['get'], url_path='percentage')
    def percentage(self, request, *args, **kwargs):
        year = int(request.GET.get('year', timezone.now().year))
        base_qs = self.get_queryset().filter(attendance_day__attendance_date__year=year)

        school_id = request.GET.get('school_id')
        if school_id:
            base_qs = base_qs.filter(attendance_day__school_id=school_id)

        round_id = request.GET.get('round_id')
        if round_id:
            base_qs = base_qs.filter(attendance_day__round_id=round_id)

        registration_level = request.GET.get('registration_level')
        if registration_level:
            base_qs = base_qs.filter(attendance_day__registration_level=registration_level)

        available_years = [
            item.year
            for item in self.get_queryset().dates('attendance_day__attendance_date', 'year')
        ]

        payload = _build_attendance_percentage_payload(base_qs, available_years, year)
        return JsonResponse(payload, safe=False)
