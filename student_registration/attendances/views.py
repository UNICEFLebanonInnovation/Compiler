# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from datetime import datetime
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.students.models import (
    Location,
    Grade,
    School,
    Section,
)
from student_registration.alp.models import Registration
from .models import Attendance
from .serializers import AttendanceSerializer


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


class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendances/index.html'

    def get_context_data(self, **kwargs):
        selected_school = 0
        school = 0

        if self.request.user.is_superuser:
            self.template_name = 'attendances/list.html'
        if self.request.user.school:
            selected_school = self.request.user.school.id
            school = self.request.user.school

        return {
            'school': school,
            'selected_school': selected_school,
            'locations': Location.objects.all(),
            'schools': School.objects.all(),
            'grades': Grade.objects.all(),
            'sections': Section.objects.all()
        }
