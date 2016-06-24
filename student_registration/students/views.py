# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse

from .models import Student, School


class SchoolDetailJson(LoginRequiredMixin, DetailView):
    model = School

    def get(self, request, *args, **kwargs):
        instance = School.objects.get(id=request.GET.get('id'))
        return JsonResponse({'result': 'OK', 'number': instance.number})
