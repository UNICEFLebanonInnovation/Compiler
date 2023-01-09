# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from django.core.urlresolvers import reverse
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from student_registration.users.utils import force_default_language
from student_registration.outreach.models import OutreachChild
from student_registration.child.models import Child
from student_registration.outreach.serializers import ChildSerializer
from .filters import (
    MainFilter
)
from .tables import (
    BootstrapTable,
    MainTable,
)
from .models import (
    Registration,
    Referral
)

from .forms import (
    MainForm,
    ReferralForm
)
from .serializers import (
    MainSerializer
)

from .utils import *


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'mscc/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])

        return {
            'instance': instance,
        }


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = '/MSCC/List/'
    group_required = [u"MSCC"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(MainAddView, self).get_initial()
        data = {
            'type': self.request.GET.get('type', ''),
        }
        if self.request.GET.get('registration_id'):
            instance = Registration.objects.get(id=self.request.GET.get('registration_id'))
            data = MainSerializer(instance).data
            data['child_nationality'] = data['child_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data

        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(MainAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=None, request=self.request)
        else:
            return MainForm(None, instance=None, request=self.request, initial=self.get_initial())


class MainEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = '/MSCC/List/'
    group_required = [u"MSCC"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = MainSerializer(instance).data
            data['child_nationality'] = data['child_nationality_id']
            data['child_disability'] = data['child_disability_id']
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']
            data['father_educational_level'] = data['father_educational_level_id']
            data['mother_educational_level'] = data['mother_educational_level_id']
            data['id_type'] = data['id_type_id']
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)


class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = MainTable
    model = Registration
    template_name = 'mscc/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u"MSCC"]

    filterset_class = MainFilter

    def get_queryset(self):
        return Registration.objects.all().order_by('-id')
        # return Registration.objects.filter(partner=self.request.user.partner_id).order_by('-id')


class MainViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    model = Registration
    queryset = Registration.objects.all()
    serializer_class = MainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')

        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


def mscc_child_search(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    birthday_year = body['birthday_year']
    birthday_month = body['birthday_month']
    birthday_day = body['birthday_day']
    first_name = body['first_name']
    father_name = body['father_name']
    last_name = body['last_name']

    form_str = '{} {} {}'.format(first_name, father_name, last_name)
    filtered_results = OutreachChild.objects.filter(
        birthday_year=birthday_year
    )
    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )
    if birthday_day:
        filtered_results = filtered_results.filter(
            birthday_day=birthday_day
        )
    filtered_results = filtered_results.values(
        'id',
        'first_name',
        'outreach_caregiver__father_name',
        'outreach_caregiver__last_name',
        'outreach_caregiver__mother_full_name',
        'gender',
        'nationality',
        'date_of_birth',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['outreach_caregiver__father_name'], result['outreach_caregiver__last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 85:
            result['score'] = fuzzy_match
            result_match.append(result)

    if filtered_results != '':
        return JsonResponse({'result': result_match})

    return JsonResponse({'result': []})


def mscc_outreach_child(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    id = body['id']
    result = OutreachChild.objects.filter(
        id= id
    ).values('id',
             'first_name',
             'outreach_caregiver__father_name',
             'outreach_caregiver__last_name',
             'outreach_caregiver__mother_full_name',
             'gender',
             'nationality',
             'date_of_birth',
             'birthday_year',
             'birthday_month',
             'birthday_day',
             'nationality_other',
             'outreach_caregiver__address',
             'disability',
             'disability_other',
             'family_status',
             'outreach_caregiver__caregiver_nationality',
             'outreach_caregiver__caregiver_nationality_other',
             'working_status',
             'work_type',
             'work_type_other',
             'outreach_caregiver__primary_phone',
             'outreach_caregiver__primary_phone',
             'outreach_caregiver__secondary_phone',
             'outreach_caregiver__secondary_phone',
             'outreach_caregiver__main_caregiver',
             'outreach_caregiver__caregiver_first_name',
             'outreach_caregiver__father_name',
             'outreach_caregiver__last_name',
             'outreach_caregiver__caregiver_mother_name',
             'outreach_caregiver__id_type',
             'outreach_caregiver__unhcr_case_number',
             'outreach_caregiver__caregiver_unhcr_id',
             'child_unhcr_number',
             'outreach_caregiver__unhcr_barcode',
             'outreach_caregiver__caregiver_personal_id',
             'child_personal_id'
             ).first()

    if result != '':
        return JsonResponse({'result': result})

    return JsonResponse({'result': []})


class ReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/referral_form.html'
    form_class = ReferralForm
    success_url = ''
    group_required = [u"MSCC"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['registry'] = self.kwargs['registry']
        return super(ReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return ReferralForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(ReferralForm.Meta.fields, Referral.objects.get(id=instance))
                return ReferralForm(data, registry=registry, instance=instance, request=self.request)
            return ReferralForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(ReferralFormView, self).form_valid(form)
