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
        alp_round = ALPRound.objects.get(current_round=True)
        education_year = EducationYear.objects.get(current_year=True)
        qs = self.queryset.filter(
            Q(alp_enrollment__isnull=False,
              alp_enrollment__deleted=False,
              # alp_enrollment__dropout_status=False,
              alp_enrollment__alp_round=alp_round) |
            Q(student_enrollment__isnull=False,
              student_enrollment__deleted=False,
              # student_enrollment__dropout_status=False,
              student_enrollment__education_year=education_year)
        )
        if self.request.GET.get('barcode', None):
            qs = qs.filter(hh_barcode=self.request.GET.get('barcode', None))
        if self.request.GET.get('case_number', None):
            qs = qs.filter(id_number=self.request.GET.get('case_number', None))
        if self.request.GET.get('name', None):
            for term in self.request.GET.get('name', None).split():
                qs = qs.filter(
                    Q(first_name__contains=term) |
                    Q(father_name__contains=term) |
                    Q(last_name__contains=term) |
                    Q(id_number__contains=term)
                ).distinct()
        try:
            if self.request.GET.get('individual_number', None):
                qs = qs.filter(id_number=self.request.GET.get('individual_number', None))
        except Exception as ex:
            print ex.message
            return []

        return qs


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
