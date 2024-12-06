# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from .program_form import *
from .utils import *


class EnrolledProgramsFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'youth/enrolled_programs_form.html'
    form_class = EnrolledProgramsForm
    success_url = ''
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return '/youth/Child-Profile/{}/'.format(str(self.kwargs['registry']))

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


class ProgramDocumentFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'youth/program_document_form.html'
    form_class = ProgramDocumentForm
    success_url = ''
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return '/youth/PD-List/'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ProgramDocumentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return ProgramDocumentForm(self.request.POST, instance=instance,
                                        request=self.request)
        else:
            if instance:
                # Fetch instance data and convert to dictionary format if available
                try:
                    instance_data = ProgramDocument.objects.get(id=instance)
                    data = {
                        'partner': instance_data.partner_id,
                        'funded_by': instance_data.funded_by_id,
                        'project_status': instance_data.project_status_id,
                        'project_code': instance_data.project_code,
                        'project_name': instance_data.project_name,
                        'project_description': instance_data.project_description,
                        'implementing_partners': instance_data.implementing_partners,
                        'focal_point': instance_data.focal_point_id,
                        'start_date': instance_data.start_date,
                        'end_date': instance_data.end_date,
                        'comment': instance_data.comment,
                        'plan': instance_data.plan_id,
                        'sectors': instance_data.sectors_id,
                        'project_type': instance_data.project_type_id,
                        'public_institution_support': instance_data.public_institution_support,
                        'budget': instance_data.budget,
                        'cash_assistance': instance_data.cash_assistance,
                        'number_targeted_syrians': instance_data.number_targeted_syrians,
                        'number_targeted_lebanese': instance_data.number_targeted_lebanese,
                        'number_targeted_prl': instance_data.number_targeted_prl,
                        'number_targeted_prs': instance_data.number_targeted_prs,
                        'governorates': instance_data.governorates.all(),
                        'population_groups': instance_data.population_groups.all(),
                        'master_programs': instance_data.master_programs.all(),
                        'donors': instance_data.donors.all(),
                        'master_program1': instance_data.master_program1_id,
                        'baseline1': instance_data.baseline1,
                        'target1': instance_data.target1,
                        'master_program2': instance_data.master_program2_id,
                        'baseline2': instance_data.baseline2,
                        'target2': instance_data.target2,
                        'master_program3': instance_data.master_program3_id,
                        'baseline3': instance_data.baseline3,
                        'target3': instance_data.target3,
                    }
                except ProgramDocument.DoesNotExist:
                    pass

                return ProgramDocumentForm(data=data, instance=instance, request=self.request)

            return ProgramDocumentForm(instance=instance, request=self.request)


    def form_valid(self, form):
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, instance=instance)
        return super(ProgramDocumentFormView, self).form_valid(form)

