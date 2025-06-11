# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.utils.encoding import smart_str
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from openpyxl import Workbook
from django.db import connection
import csv
import io
import zipfile
import codecs
from django.utils.encoding import smart_str
import logging
import traceback

from rest_framework import status
from django.db.models import F, Q
from django.urls import reverse
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from fuzzywuzzy import fuzz
from django.shortcuts import redirect, render
from django.conf import settings
import os
from django.http import FileResponse
import uuid
from storages.backends.azure_storage import AzureStorage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
from django.contrib.auth.decorators import login_required

from .filters import (
    MainFilter,
    FullFilter
)
from .tables import (
    BootstrapTable,
    MainTable,
    YouthMainTable,
    FullTable,
    PartnerTable,
)
from .models import (
    Registration,
    Referral,
    EducationHistory
)
from student_registration.backends.models import ExportHistory

from .forms import (
    MainForm,
    ReferralForm
)
from .serializers import (
    MainSerializer
)

from .utils import *

from student_registration.mscc.templatetags.simple_tags import education_history_model, education_history_programmes
from student_registration.users.templatetags.custom_tags import has_group


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'mscc/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        generate_services(instance.child.age, instance)
        current_tab = self.request.GET.get('current_tab', 'info')

        return {
            'instance': instance,
            'current_tab': current_tab
        }


class DashboardView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'mscc/dashboard.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization

        instances = Registration.objects.all()
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()

        return {
            'total': instances.count(),
            'total_corepackage': instances.filter(type='Core-Package').count(),
            'total_walkin': instances.filter(type='Walk-in').count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners
        }


class DashboardYouthView(LoginRequiredMixin,
                         TemplateView):
    template_name = 'mscc/dashboard_youth.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization

        instances = Registration.objects.all()
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()

        return {
            'total': instances.count(),
            'total_corepackage': instances.filter(type='Core-Package').count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners
        }


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = '/MSCC/List/'
    group_required = [u"MSCC", u"MSCC_CENTER"]

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
    group_required = [u"MSCC", u"MSCC_CENTER"]

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
            data['child_nationality'] = data['child_nationality_id'] if 'child_nationality_id' in data else ''
            data['child_disability'] = data['child_disability_id'] if 'child_disability_id' in data else ''
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']if 'main_caregiver_nationality_id' in data else ''
            data['father_educational_level'] = data['father_educational_level_id']if 'father_educational_level_id' in data else ''
            data['mother_educational_level'] = data['mother_educational_level_id']if 'mother_educational_level_id' in data else ''
            data['id_type'] = data['id_type_id']if 'id_type_id' in data else ''
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)


class NewRoundView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):

    group_required = [u"MSCC", u"MSCC_CENTER"]
    template_name = 'mscc/new_round.html'

    def get_context_data(self, **kwargs):
        registry = kwargs.get('pk')
        return {
            'registry': registry
        }


class NewRoundRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):

        registry = self.request.GET.get('registry')
        type = self.request.GET.get('registrationType')

        if self.request.GET.get('new_round_confirmation', None) == 'confirmed':
            import copy
            registration = Registration.objects.get(id=registry)
            new_registration = copy.copy(registration)
            new_registration.pk = None
            new_registration.round = None
            new_registration.owner = self.request.user
            new_registration.modified_by = self.request.user
            new_registration.type = type
            if self.request.user.center:
                new_registration.center = self.request.user.center
            if self.request.user.partner:
                new_registration.partner = self.request.user.partner
            new_registration.save()

            generate_services(new_registration.child.age, new_registration, self.request.user)
            return reverse('mscc:service_education_add', kwargs={'registry': new_registration.id, 'package_type': type})

        return reverse('mscc:new_round', kwargs={'registry': registry})


def MainMarkDeleteView(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.deleted_by = request.user
            registration.save()
            result = {"isSuccessful": True}
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


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
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id

        if has_group(user, 'MSCC_UNICEF'):
            return Registration.objects.filter(
                Q(round__isnull=True) | Q(round__current_year=True)
            ).order_by('-id')

        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            return Registration.objects.filter(
                Q(round__isnull=True) | Q(round__current_year=True),
                deleted=False, partner=partner_id
            ).order_by('-id')
        elif has_group(user, 'MSCC_CENTER') and center_id:
            return Registration.objects.filter(
                Q(round__isnull=True) | Q(round__current_year=True),
                deleted=False, center=center_id
            ).order_by('-id')
        return Registration.objects.none()

    def get_table_class(self):

        """
        Return the class to use for the table.
        """
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullTable
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return PartnerTable
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.table_class

        if not has_group(self.request.user, 'MSCC_FULL'):
            return YouthMainTable
        return self.table_class

    def get_filterset_class(self):
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullFilter
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return self.filterset_class
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.filterset_class

        return self.filterset_class


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


def MainRegistrationCancelView(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            return redirect('/MSCC/List/')
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)

def outreach_child_search(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

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
        result_str = '{} {} {}'.format(result['first_name'], result['outreach_caregiver__father_name'],
                                       result['outreach_caregiver__last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 80:
            result['score'] = fuzzy_match
            result_match.append(result)

    if filtered_results != '':
        return JsonResponse({'result': result_match})

    return JsonResponse({'result': []})


def outreach_child(request):

    outreach_id = request.GET.get('outreach_id')
    result = get_outreach_child(outreach_id)
    return JsonResponse(result)


class ReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/referral_form.html'
    form_class = ReferralForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return '/MSCC/Child-Profile/{}/?current_tab=services'.format(str(self.kwargs['registry']))

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(ReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return ReferralForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = Referral.objects.get(id=pk)

                return ReferralForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return ReferralForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(ReferralFormView, self).form_valid(form)


def old_child_search(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    form_str = '{} {} {}'.format(first_name, father_name, last_name)

    # filtered_results = Student.objects.filter(
    #     birthday_year=birthday_year
    # )
    # if filtered_results.count() > 1000 and not birthday_month and not birthday_day:
    #     return JsonResponse({'result': {'error': 'Too many records. Please select the Birthday '
    #                                              'month to get more accurate result'}})
    #
    # if birthday_month:
    #     filtered_results = filtered_results.filter(
    #         birthday_month=birthday_month
    #     )
    #
    # if filtered_results.count() > 1000 and not birthday_day:
    #     return JsonResponse({'result': {'error': 'Too many records. Please select the Birthday '
    #                                              'day to get more accurate result'}})
    #
    # if birthday_day:
    #     filtered_results = filtered_results.filter(
    #         birthday_day=birthday_day
    #     )
    #
    # filtered_results = filtered_results.values(
    #     'id',
    #     'first_name',
    #     'father_name',
    #     'last_name',
    #     'mother_fullname',
    #     'sex',
    #     'nationality__name',
    #     'birthday_year',
    #     'birthday_month',
    #     'birthday_day',
    # ).distinct()
    #
    # result_match = []
    # for result in filtered_results:
    #     result_str = '{} {} {}'.format(result['first_name'], result['father_name'],
    #                                    result['last_name'])
    #     fuzzy_match = fuzz.ratio(form_str, result_str)
    #     if fuzzy_match > 70:
    #         result['score'] = fuzzy_match
    #         result['programmes'] = education_history_programmes(result['id'])
    #         result_match.append(result)
    #
    # return JsonResponse({'result': result_match})

    filtered_results = Student.objects.filter(
        birthday_year=birthday_year
    )

    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )

    filtered_results = filtered_results.filter(
        Q(first_name__contains=first_name, last_name__contains=last_name) |
        Q(first_name__contains=first_name, father_name__contains=last_name)
    ).values(
        'id',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'sex',
        'nationality__name',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['father_name'],
                                       result['last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 70:
            result['score'] = fuzzy_match
            result['programmes'] = education_history_programmes(result['id'])
            result_match.append(result)

    return JsonResponse({'result': result_match})


def old_child_data(request):

    student_id = request.GET.get('student_id')
    result = get_old_child(student_id)
    return JsonResponse(result)


def child_duplication_check(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    form_str = '{} {} {}'.format(first_name, father_name, last_name)
    filtered_results = Registration.objects.filter(
        child__birthday_year=birthday_year,
        child__birthday_month=birthday_month,
        child__birthday_day=birthday_day,
        deleted=False
    )

    filtered_results = filtered_results.values(
        'id',
        'child__first_name',
        'child__father_name',
        'child__last_name',
        'center__name'
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['child__first_name'], result['child__father_name'],
                                       result['child__last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 95:
            result['score'] = fuzzy_match
            result_match.append(result)

    return JsonResponse({'result': result_match})


def quick_search(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    term = request.GET.get('term', 0).strip()
    terms = request.GET.get('term', 0).strip()
    qs = {}

    if terms:
        user = request.user
        if user.is_authenticated:
            center_id = user.center_id
            partner_id = user.partner_id

            if has_group(user, 'MSCC_UNICEF'):
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False
                ).order_by('-id')
            elif has_group(user, 'MSCC_PARTNER') and partner_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, partner=partner_id
                ).order_by('-id')
            elif has_group(user, 'MSCC_CENTER') and center_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, center=center_id
                ).order_by('-id')
            else:
                qs = Registration.objects.none()

            if len(terms.split()) > 1:
                qs = qs.annotate(fullname=Concat('child__first_name', Value(' '), 'child__father_name',
                                                 Value(' '), 'child__last_name')) \
                    .filter(fullname__icontains=terms) \
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()

            else:
                # for term in terms:
                qs = qs.filter(
                    Q(child__first_name__icontains=term) |
                    Q(child__last_name__icontains=term))\
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'result': json.dumps(list(qs))})


class ProgrammeDetails(LoginRequiredMixin,
                       TemplateView):

    template_name = 'mscc/programme_details.html'

    def get_context_data(self, **kwargs):

        programme_id = self.request.GET.get('programme_id')
        programme_type = self.request.GET.get('programme_type')

        instance = education_history_model(programme_id, programme_type)

        return {
            'instance': instance,
            'programme_type': programme_type
        }


class ChildProfilePreview(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ChildProfilePreview, self).get_context_data(**kwargs)

        registry_id = self.request.GET.get('registry_id')

        if not registry_id:
            context['error'] = 'No id provided.'
            return context

        try:
            instance = Registration.objects.get(id=registry_id)
        except Registration.DoesNotExist:
            context['error'] = 'Registration with id' + str(registry_id) + ' not found.'
            return context
        except ValueError:
            context['error'] = 'Invalid registry_id ' + str(registry_id)
            return context

        context['instance'] = instance
        return context


@login_required(login_url='/users/login')
def export_list_background(request):
    try:
        cursor = connection.cursor()
        user = request.user
        center_id = user.center_id

        partner_id = 0
        partner_name = ''
        if user.partner_id:
            partner_id = user.partner_id
            partner_name = user.partner.name

        round = request.GET.get('round', '')
        if not round:
            return JsonResponse({'error': 'Round is not selected. Please select a round before exporting data.'},
                                status=400)

        query_params = []

        if round == 'no_round':
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data_no_round WHERE id > 0 "
        else:
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE round_id = %s"
            query_params = [round]

        if has_group(user, 'MSCC_UNICEF'):
            vw_mscc_data_str += " AND id > 0 "
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_mscc_data_str += " AND partner_id = %s"
            query_params.append(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_mscc_data_str += " AND center_id = %s"
            query_params.append(center_id)
        else:
            vw_mscc_data_str += " AND id = 0 "

        cursor.execute(vw_mscc_data_str, query_params)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for vw_mscc_data
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)

            # Add BOM to handle Arabic text correctly
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)  # Write headers

            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)

            # Add CSV to ZIP
            zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

            # Process followup_service_data
            registration_ids = [row[0] for row in mscc_data]
            if registration_ids:
                followup_service_data_str = "SELECT * FROM mscc_followupservice WHERE registration_id IN ({})".format(
                    ','.join(['%s'] * len(registration_ids)))
                cursor.execute(followup_service_data_str, registration_ids)
                followup_service_data = cursor.fetchall()
                followup_headers = [col[0] for col in cursor.description]

                # Create CSV for followup_service_data
                csv_followup_output = io.StringIO()
                csv_writer = csv.writer(csv_followup_output)

                # Add BOM to handle Arabic text correctly
                csv_followup_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(followup_headers)  # Write headers

                for row in followup_service_data:
                    encoded_row = [smart_str(cell) for cell in row]
                    csv_writer.writerow(encoded_row)

                # Add CSV to ZIP
                zf.writestr('followup_data.csv', csv_followup_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = "out_file_{}.zip".format(unique_id)
        file_path = os.path.join('export', file_name)

        default_storage.save(file_path, ContentFile(zip_output.getvalue()))
        ExportHistory.objects.create(
            export_type='Makani List',
            created_by=user,
            partner_name=partner_name
        )

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


def export_child_list_background(request):
    try:
        cursor = connection.cursor()

        vw_mscc_data_str = "SELECT * FROM vw_mscc_child "
        cursor.execute(vw_mscc_data_str)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for vw_mscc_data
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)

            # Add BOM to handle Arabic text correctly
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)  # Write headers

            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)

            # Add CSV to ZIP
            zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = "out_file_{}.zip".format(unique_id)
        file_path = os.path.join('export', file_name)

        default_storage.save(file_path, ContentFile(zip_output.getvalue()))

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


class MyAzureStorage(AzureStorage):
    location = "export"


@login_required(login_url='/users/login')
def get_file(request, file_name):

    response = None

    if is_valid_filename(file_name):
        storage = MyAzureStorage()

        file_path = os.path.join('export', file_name)
        returned_file_name = 'output_file.zip'

        try:
            with storage.open(file_path, 'rb') as f:
                file_stream = io.BytesIO(f.read())
                file_stream.seek(0)
                response = FileResponse(file_stream)
                response['Content-Disposition'] = 'attachment; filename="' + returned_file_name + '"'
        except Exception as e:
            response = HttpResponse("Error reading file: {}".format(e))

        default_storage.delete(file_path)
    else:
        response = HttpResponse("Invalid file.")
    return response


def is_valid_filename(filename):
    pattern = r'^[a-zA-Z0-9-_]+.zip$'

    return re.match(pattern, filename) is not None


@login_required(login_url='/users/login')
def get_file_csv(request, file_name):
    response = None

    if is_valid_filename_csv(file_name):
        storage = MyAzureStorage()
        file_path = os.path.join('export', file_name)
        returned_file_name = "exported_data.csv"

        try:
            with storage.open(file_path, 'rb') as f:
                file_stream = io.BytesIO(f.read())
                file_stream.seek(0)
                response = FileResponse(file_stream, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="' + returned_file_name + '"'
        except Exception as e:
            response = HttpResponse("Error reading file: {}".format(e))

        # Optionally delete after serving
        default_storage.delete(file_path)
    else:
        response = HttpResponse("Invalid file.", status=400)

    return response


def is_valid_filename_csv(filename):
    """Ensure the filename is a valid CSV file with expected format."""
    pattern = r'^[a-zA-Z0-9-_]+\.csv$'
    return re.match(pattern, filename) is not None
