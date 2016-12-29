# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from dal import autocomplete
from django.db.models import Q
from .models import (
    Student,
)

from .serializers import (
    StudentSerializer,
)

from django.views.generic.edit import FormView

import json

class StudentViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    model = Student
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return []


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
