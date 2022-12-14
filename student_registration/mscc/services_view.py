# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.users.utils import force_default_language
from .models import Registration
from .utils import *
from .services_form import *


class InclusionFormView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FormView):
    template_name = 'mscc/service_inclusion_form.html'
    form_class = InclusionServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(InclusionFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return InclusionServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(InclusionServiceForm.Meta.fields, InclusionService.objects.get(id=instance))
            return InclusionServiceForm(data, registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(InclusionFormView, self).form_valid(form)
