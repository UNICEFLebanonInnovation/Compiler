# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from openpyxl import Workbook

from rest_framework import status
from django.db.models import F, Q
from django.core.urlresolvers import reverse
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from fuzzywuzzy import fuzz

from .filters import (
    MainFilter
)
from .tables import (
    BootstrapTable,
    MainTable,
    YouthMainTable,
)
from .models import (
    Registration,
    Referral,
    EducationHistory
)

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
            'total_woosc': instances.filter(type='Walk-in-OOSC').count(),
            'total_wshl': instances.filter(type='Walk-in-In-School').count(),
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
        # return Registration.objects.all().order_by('-id')
        return Registration.objects.filter(center=self.request.user.center_id).order_by('-id')

    def get_table_class(self):

        """
        Return the class to use for the table.
        """
        if not has_group(self.request.user, 'MSCC_FULL'):
            return YouthMainTable
        return self.table_class


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
        if fuzzy_match > 85:
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
    group_required = [u"MSCC"]

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
        child__birthday_day=birthday_day
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
        if fuzzy_match > 90:
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
        qs = Registration.objects.filter(center=request.user.center_id)
        if len(terms.split()) > 1:
            qs = qs.annotate(fullname=Concat('child__first_name', Value(' '), 'child__father_name',
                                             Value(' '), 'child__last_name')) \
                .filter(child__fullname__icontains=terms) \
                .values('id', 'child__first_name', 'child__last_name',
                        'child__father_name', 'child__mother_fullname').distinct()
        else:
            # for term in terms:
            qs = qs.filter(
                Q(child__first_name__icontains=term) |
                Q(child__last_name__icontains=term))\
                .values('id', 'child__first_name', 'child__last_name',
                        'child__father_name', 'child__mother_fullname').distinct()

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


class ChildProfilePreview(LoginRequiredMixin,
                          TemplateView):

    template_name = 'mscc/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        registry_id = self.request.GET.get('registry_id')

        instance = Registration.objects.get(id=registry_id)

        return {
            'instance': instance,
        }


def export_data(request):
    from django.db import connection
    cursor = connection.cursor()

    center = request.user.center_id
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    father_name = request.GET.get('father_name', '')
    mother_fullname = request.GET.get('mother_fullname', '')
    nationality = request.GET.get('nationality', '')

    vw_str = 'SELECT * FROM vw_mscc_data where center_id = ' + str(center)
    if first_name != '':
        vw_str += " and child_first_name LIKE '" + first_name + "%'"
    if last_name != '':
        vw_str += " and child_father_name LIKE '" + last_name + "%'"
    if father_name != '':
        vw_str += " and child_last_name LIKE '" + father_name + "%'"
    if mother_fullname != '':
        vw_str += " and mother_fullname LIKE '" + mother_fullname + "%'"
    if nationality != '':
        vw_str += " and student_nationality_id = " + nationality

    cursor.execute(vw_str)
    data = cursor.fetchall()

    headers = [col[0] for col in cursor.description]

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(headers)

    for row in data:
        encoded_row = [value.encode('utf-8') if isinstance(value, str) else value for value in row]
        worksheet.append(encoded_row)

    # Set the appropriate response headers for Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response
