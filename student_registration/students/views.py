# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import detail_route, list_route
from dal import autocomplete
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from django.core import serializers

from .models import (
    Student,
)

from .serializers import (
    StudentSerializer,
)
from student_registration.alp.models import ALPRound
from student_registration.schools.models import EducationYear


class StudentViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     # mixins.CreateModelMixin,
                     # mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    model = Student
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return []

    def get_basic_queryset(self):
        alp_round = ALPRound.objects.get(current_round=True)
        education_year = EducationYear.objects.get(current_year=True)
        qs = Student.objects.filter(
            Q(alp_enrollment__isnull=False,
              alp_enrollment__deleted=False,
              # alp_enrollment__dropout_status=False,
              alp_enrollment__alp_round=alp_round) |
            Q(student_enrollment__isnull=False,
              student_enrollment__deleted=False,
              # student_enrollment__dropout_status=False,
              student_enrollment__education_year=education_year)
        )
        return qs

    @list_route(url_path='by_barcode/(?P<barcode>.+)')
    def by_barcode(self, request, *args, **kwargs):
        qs = self.get_basic_queryset()
        qs = qs.filter(hh_barcode=kwargs['barcode'])
        serializer = StudentSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route(url_path='by_case_number/(?P<id_number>.+)')
    def by_case_number(self, request, *args, **kwargs):
        qs = self.get_basic_queryset()
        qs = qs.filter(id_number=kwargs['id_number'])
        serializer = StudentSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route(url_path='by_individual_number/(?P<id_number>.+)')
    def by_individual_number(self, request, *args, **kwargs):
        qs = self.get_basic_queryset()
        try:
            qs = qs.get(id_number=kwargs['id_number'])
            serializer = StudentSerializer(qs)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response()

    @list_route(url_path='attendances_per_gov/(?P<start_date>.+)/(?P<end_date>.+)/(?P<gov>.+)')
    def attendances_per_gov(self, request, *args, **kwargs):
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        gov_id = kwargs['gov']

        qs = self.get_basic_queryset()
        serializer = StudentSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route(url_path='date_interval/(?P<start_date>.+)/(?P<end_date>.+)/(?P<id>.+)')
    def date_interval(self, request, *args, **kwargs):
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        student_id = kwargs['id']

        qs = self.get_basic_queryset()
        serializer = StudentSerializer(qs, many=True)
        return Response(serializer.data)


class StudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Student.objects.none()

        qs = Student.objects.all()

        if self.q:
            qs = Student.objects.filter(
                Q(first_name__istartswith=self.q) | Q(father_name__istartswith=self.q) |
                Q(last_name__istartswith=self.q) | Q(id_number__istartswith=self.q)
            )

        return qs
