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


from .models import EducationAssessment, Registration
from .education_form import *
from .utils import *


class EducationAssessmentFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_assessment_form.html'
    form_class = EducationAssessmentForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EducationAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationAssessmentForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(EducationAssessmentForm.Meta.fields, EducationAssessment.objects.get(id=instance))
            return EducationAssessmentForm(data, registry=registry, instance=instance, request=self.request)
    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationAssessmentFormView, self).form_valid(form)


class EducationServiceFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_service_form.html'
    form_class = EducationServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EducationServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationServiceForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(EducationServiceForm.Meta.fields, EducationService.objects.get(id=instance))
            return EducationServiceForm(data, registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationServiceFormView, self).form_valid(form)



class EducationRSServiceFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_rs_service_form.html'
    form_class = EducationRSServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EducationRSServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationRSServiceForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(EducationRSServiceForm.Meta.fields, EducationRSService.objects.get(id=instance))
            return EducationRSServiceForm(data, registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationRSServiceFormView, self).form_valid(form)
