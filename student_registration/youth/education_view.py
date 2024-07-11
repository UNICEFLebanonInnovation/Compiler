# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from .education_form import *
from .utils import *


class EnrolledProgramsFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'youth/service_education_assessment_form.html'
    form_class = EnrolledProgramsForm
    success_url = ''
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return '/youth/Child-Profile/{}/?current_tab=services'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(EnrolledProgramsFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EnrolledProgramsForm(self.request.POST, instance=instance, registry=registry,
                                        request=self.request)
        else:
            if instance:
                data = to_array(EnrolledProgramsForm.Meta.fields, EnrolledPrograms.objects.get(id=instance))
                return EnrolledProgramsForm(data, registry=registry,  instance=instance, request=self.request)
            return EnrolledProgramsForm(registry=registry,  instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EnrolledProgramsFormView, self).form_valid(form)

