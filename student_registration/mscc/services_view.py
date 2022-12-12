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

from .services_form import *


class InclusionAddView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_inclusion.html'
    form_class = InclusionServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Profile/{}/'.format(str(self.request.session.get('registration_id')))

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(InclusionServiceForm, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return InclusionServiceForm(self.request.POST, instance=None, request=self.request)
        else:
            return InclusionServiceForm(None, instance=None, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(InclusionServiceForm, self).form_valid(form)


class InclusionEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'mscc/service_inclusion.html'
    form_class = InclusionServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Profile/{}/'.format(str(self.request.session.get('registration_id')))

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(InclusionEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return InclusionServiceForm(self.request.POST, instance=instance, request=self.request)
        else:
            return InclusionServiceForm(None, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(InclusionEditView, self).form_valid(form)
