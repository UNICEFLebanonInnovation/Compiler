# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from rest_framework.generics import ListAPIView
from rest_framework.decorators import detail_route, list_route
from datetime import datetime
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.schools.models import (
    School,
    Section
)
from student_registration.locations.models import Location
from .models import Attendance, Absentee
from .serializers import AttendanceSerializer, AbsenteeSerializer
from student_registration.attendances.tasks import set_app_attendances


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

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})

    @list_route(methods=['get'], url_path='push-by-school/(?P<school>\d+)')
    def push_by_school(self, request, *args, **kwargs):
        school = School.objects.get(id=kwargs.get('school', False))
        set_app_attendances.delay(school_number=school.number)
        return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceReportViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):

    model = Attendance
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        school = request.GET.get("school", 0)

        queryset = self.queryset.filter(school_id=school)
        data = tablib.Dataset()
        data.headers = [
            _('Student number'), _('Student fullname'), _('Mother fullname'),
        ]

        content = []
        for line in queryset:
            content = [
                line.student.number,
                line.student.__unicode__(),
                line.student.mother_fullname,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        # response = HttpResponse(
        #     file_format.export_data(data),
        #     content_type='application/vnd.ms-excel',
        # )
        # response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendances/index.html'

    def get_context_data(self, **kwargs):
        selected_school = 0
        school = 0
        queryset = []
        data = []

        if self.request.user.is_superuser:
            self.template_name = 'attendances/list.html'
            queryset = self.model.objects.order_by('attendance_date')\
                                    .values_list('attendance_date', 'classroom_id', 'validation_status')\
                                    .distinct('attendance_date', 'classroom_id', 'validation_status')
        if self.request.user.school:
            selected_school = self.request.user.school.id
            school = self.request.user.school

        for item in queryset:
            data.append({
                "attendance_date": item[0].strftime('%Y-%m-%d'),
                "classroom": item[1],
                "validated": item[2],
            })

        return {
            'days': json.dumps(data),
            'school': school,
            'selected_school': selected_school,
            'locations': Location.objects.all(),
            'schools': School.objects.all(),
            'sections': Section.objects.all()
        }


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Attendance

    def get(self, request, *args, **kwargs):

        school = request.GET.get("school")

        queryset = self.queryset
        data = tablib.Dataset()
        data.headers = [
            _('Student number'), _('Student fullname'), _('Mother fullname'),
        ]

        content = []
        for line in queryset:
            content = [
                line.student.number,
                line.student.__unicode__(),
                line.student.mother_fullname,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return response


class AbsenteeView(ListAPIView):
    """
    API endpoint for validated absentees
    """
    queryset = Absentee.objects.all()
    serializer_class = AbsenteeSerializer
    permission_classes = (permissions.IsAdminUser,)
