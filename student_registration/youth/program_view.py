# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.http import JsonResponse, HttpResponseNotAllowed

from .program_form import *
from .utils import *
from student_registration.youth.models import EnrolledPrograms, Registration


class EnrolledProgramsFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'youth/enrolled_programs_form.html'
    form_class = EnrolledProgramsForm
    success_url = ''
    group_required = [u"YOUTH"]

    def get_success_url(self):
        registry = self.kwargs.get('registry')
        if registry:
            return '/youth/child-profile/{}/'.format(str(registry))
        return '/youth/list/'

    def get_selected_registration_ids(self):
        selected_registration_ids = self.request.POST.get('selected_registration_ids')
        if selected_registration_ids:
            return [registration_id for registration_id in selected_registration_ids.split(',') if registration_id]
        return self.request.GET.getlist('registrations')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs.get('registry')
        kwargs['selected_registration_ids'] = self.get_selected_registration_ids()
        return super(EnrolledProgramsFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs.get('registry')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        selected_registration_ids = self.get_selected_registration_ids()
        if self.request.method == "POST":
            return EnrolledProgramsForm(self.request.POST, instance=instance, registry=registry,
                                        selected_registration_ids=selected_registration_ids,
                                        request=self.request)
        if instance:
            data = to_array(EnrolledProgramsForm.Meta.fields, EnrolledPrograms.objects.get(id=instance))
            return EnrolledProgramsForm(initial=data, registry=registry, instance=instance, request=self.request)
        return EnrolledProgramsForm(registry=registry, instance=instance,
                                    selected_registration_ids=selected_registration_ids,
                                    request=self.request)

    def form_valid(self, form):
        registry = self.kwargs.get('registry')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        if registry or instance:
            form.save(request=self.request, registry=registry, instance=instance)
        else:
            form.save_bulk(request=self.request)
        return super(EnrolledProgramsFormView, self).form_valid(form)


class EnrolledProgramsDeleteView(View):

    def post(self, request, pk):
        try:
            program = EnrolledPrograms.objects.get(pk=pk)
            program.delete()
            return JsonResponse({'status': 'deleted'})
        except EnrolledPrograms.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    def get(self, request, pk):
        return HttpResponseNotAllowed(['POST'])


class ProgramDocumentFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'youth/program_document_form.html'
    form_class = ProgramDocumentForm
    success_url = ''
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return '/youth/pd-list/'

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
                        'year': instance_data.year_id,
                        'budget': instance_data.budget,
                        'cash_assistance': instance_data.cash_assistance,
                        'number_targeted_syrians': instance_data.number_targeted_syrians,
                        'number_targeted_lebanese': instance_data.number_targeted_lebanese,
                        'number_targeted_prl': instance_data.number_targeted_prl,
                        'number_targeted_prs': instance_data.number_targeted_prs,
                        'governorates': instance_data.governorates.all(),
                        'population_groups': instance_data.population_groups.all(),
                        'donors': instance_data.donors.all(),
                    }
                except ProgramDocument.DoesNotExist:
                    pass

                return ProgramDocumentForm(data=data, instance=instance, request=self.request)

            return ProgramDocumentForm(instance=instance, request=self.request)


    def form_valid(self, form):
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, instance=instance)
        return super(ProgramDocumentFormView, self).form_valid(form)

