# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.users.utils import force_default_language

from .models import EducationAssessment, Registration
from .education_form import *


class EducationAssessmentAddView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 FormView):
    template_name = 'mscc/education_assessment_form.html'
    form_class = EducationAssessmentForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        reg_id = self.kwargs['reg_id']
        return reverse('mscc:edit_child', kwargs={'pk': reg_id})

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        context = super(EducationAssessmentAddView, self).get_context_data(**kwargs)
        context['reg_id'] = self.kwargs['reg_id']
        return context

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return EducationAssessmentForm(self.request.POST, instance=None, request=self.request,
                                           reg_id=self.kwargs['reg_id'])
        else:
            return EducationAssessmentForm(None, instance=None, request=self.request, reg_id=self.kwargs['reg_id'])

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(EducationAssessmentAddView, self).get_form_kwargs(*args, **kwargs)
        kwargs['reg_id'] = self.kwargs['reg_id']
        return kwargs

    def form_valid(self, form):
        form.instance.Registration = Registration.objects.get(pk=self.kwargs['reg_id'])
        form.save(self.request)
        return super(EducationAssessmentAddView, self).form_valid(form)


class EducationAssessmentEditView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/education_assessment_form.html'
    form_class = EducationAssessmentForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        reg_id = 5
        return reverse('mscc:edit_child', kwargs={'pk': reg_id})

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EducationAssessmentEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = EducationAssessment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return EducationAssessmentForm(self.request.POST, instance=instance, request=self.request)
        else:
            return EducationAssessmentForm(None, instance=instance, request=self.request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(EducationAssessmentEditView, self).form_valid(form)


class EducationAssessmentRedirectView(RedirectView):

    def get_redirect_url(*args, **kwargs):
        registration_id = kwargs['pk']
        if EducationAssessment.objects.filter(registration__id=registration_id).exists():
            education_assessment_id = EducationAssessment.objects.filter(registration__id=registration_id).first().id
            return reverse('mscc:edit_education_assessment', kwargs={'pk': education_assessment_id})
        else:
            return reverse('mscc:add_education_assessment', kwargs={'reg_id': registration_id})
