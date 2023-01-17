# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from .utils import *
from .services_form import *
from .models import *


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
            kwargs['registry'] = self.kwargs['registry']
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
            return InclusionServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(InclusionFormView, self).form_valid(form)


class DigitalFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_digital_form.html'
    form_class = DigitalServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(DigitalFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return DigitalServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(DigitalServiceForm.Meta.fields, DigitalService.objects.get(id=instance))
                return DigitalServiceForm(data, registry=registry, instance=instance, request=self.request)
            return DigitalServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(DigitalFormView, self).form_valid(form)


class HealthNutritionFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_health_nutrition_form.html'
    form_class = HealthNutritionServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(HealthNutritionFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        age = self.kwargs['age']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return HealthNutritionServiceForm(self.request.POST, instance=instance, registry=registry,age=age, request=self.request)
        else:
            if instance:
                data = to_array(HealthNutritionServiceForm.Meta.fields, HealthNutritionService.objects.get(id=instance))
                return HealthNutritionServiceForm(data, registry=registry, age=age, instance=instance, request=self.request)
            return HealthNutritionServiceForm(registry=registry, age=age, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(HealthNutritionFormView, self).form_valid(form)


class PSSFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_pss_form.html'
    form_class = PSSServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(PSSFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return PSSServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(PSSServiceForm.Meta.fields, PSSService.objects.get(id=instance))
                return PSSServiceForm(data, registry=registry, instance=instance, request=self.request)
            return PSSServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(PSSFormView, self).form_valid(form)


class YouthKitServiceFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_youth_kit_form.html'
    form_class = YouthKitServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(YouthKitServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthKitServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(YouthKitServiceForm.Meta.fields, YouthKitService.objects.get(id=instance))
                return YouthKitServiceForm(data, registry=registry, instance=instance, request=self.request)
            return YouthKitServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthKitServiceFormView, self).form_valid(form)


class FollowUpFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_follow_up_form.html'
    form_class = FollowUpServiceForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(FollowUpFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return FollowUpServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(FollowUpServiceForm.Meta.fields, FollowUpService.objects.get(id=instance))
                return FollowUpServiceForm(data, registry=registry, instance=instance, request=self.request)
            return FollowUpServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(FollowUpFormView, self).form_valid(form)


class YouthAssessmentFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_youth_assessment_form.html'
    form_class = YouthAssessmentForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(YouthAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthAssessmentForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(YouthAssessmentForm.Meta.fields, YouthAssessment.objects.get(id=instance))
                return YouthAssessmentForm(data, registry=registry, instance=instance, request=self.request)
            return YouthAssessmentForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthAssessmentFormView, self).form_valid(form)


