# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView
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
from django.shortcuts import redirect, render

from .filters import (
    MainFilter,
    FullFilter,
    PDFilter
)
from .tables import (
    BootstrapTable,
    RegistrationTable,
    PDTable

)
from .models import (
    Registration,
    ProgramDocument,
    MasterProgram,
    SubProgram,
    Donor
)
from student_registration.locations.models import Location

from .forms import (
    MainForm,
)
from .serializers import (
    MainSerializer
)

from .utils import *

from student_registration.users.templatetags.custom_tags import has_group


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'youth/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        current_tab = self.request.GET.get('current_tab', 'info')

        return {
            'instance': instance,
            'current_tab': current_tab
        }


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'youth/main_form.html'
    form_class = MainForm
    success_url = '/youth/List/'
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return reverse('youth:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

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
    template_name = 'youth/main_form.html'
    form_class = MainForm
    success_url = '/YOUTH/List/'
    group_required = [u"YOUTH"]

    def get_success_url(self):
        return reverse('youth:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

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
            data['adolescent_nationality'] = data['adolescent_nationality_id'] if 'adolescent_nationality_id' in data else ''
            data['adolescent_governorate'] = data['adolescent_governorate_id'] if 'adolescent_governorate_id' in data else ''
            data['adolescent_district'] = data['adolescent_district_id'] if 'adolescent_district_id' in data else ''
            data['adolescent_cadaster'] = data['adolescent_cadaster_id'] if 'adolescent_cadaster_id' in data else ''
            data['adolescent_disability'] = data['adolescent_disability_id'] if 'adolescent_disability_id' in data else ''
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']if 'main_caregiver_nationality_id' in data else ''
            data['father_educational_level'] = data['father_educational_level_id']if 'father_educational_level_id' in data else ''
            data['mother_educational_level'] = data['mother_educational_level_id']if 'mother_educational_level_id' in data else ''
            data['id_type'] = data['id_type_id']if 'id_type_id' in data else ''
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)



class NewRoundRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):

        registry = self.request.GET.get('registry')
        if self.request.GET.get('new_round_confirmation', None) == 'confirmed':
            import copy
            registration = Registration.objects.get(id=registry)
            new_registration = copy.copy(registration)
            new_registration.pk = None
            new_registration.save()
            return reverse('youth:service_enrolled_programs_add', kwargs={'registry': new_registration.id})

        return reverse('youth:new_round', kwargs={'registry': registry})


def MainMarkDeleteView(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            result = {"isSuccessful": True}
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


from django.db.models import F, Max
class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = RegistrationTable
    model = Registration
    template_name = 'youth/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u"YOUTH"]

    filterset_class = MainFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.youth_partner_id

        return Registration.objects.filter(deleted=False
                                           ).order_by('-id')
        # elif has_group(user, 'YOUTH_PARTNER') and partner_id:
        #     return Registration.objects.filter(partner=partner_id, deleted=False, round__current_year=True).order_by('-id')
        # elif has_group(user, 'YOUTH_CENTER') and center_id:
        #     return Registration.objects.filter(center=center_id, deleted=False, round__current_year=True).order_by('-id')

        # return Registration.objects.none()

    def get_table_class(self):
        return RegistrationTable

    def get_filterset_class(self):
        return FullFilter


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
            return redirect('/YOUTH/List/')
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
            # result['programmes'] = education_history_programmes(result['id'])
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



class ChildProfilePreview(LoginRequiredMixin,
                          TemplateView):

    template_name = 'youth/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        registry_id = self.request.GET.get('registry_id')

        instance = Registration.objects.get(id=registry_id)

        return {
            'instance': instance,
        }


def export_data(request):
    from django.db import connection
    cursor = connection.cursor()
    user = request.user
    center_id = user.center_id
    partner_id = user.youth_partner_id

    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    father_name = request.GET.get('father_name', '')
    mother_fullname = request.GET.get('mother_fullname', '')
    nationality = request.GET.get('nationality', '')

    vw_youth_data_str = "SELECT * FROM vw_youth_data WHERE deleted='false'  "

    # if has_group(user, 'MSCC_UNICEF'):
    #     vw_mscc_data_str += " AND id>0 "
    # elif has_group(user, 'MSCC_PARTNER') and partner_id:
    #     vw_mscc_data_str += " AND partner_id = " + str(partner_id)
    # elif has_group(user, 'MSCC_CENTER') and center_id:
    #     vw_mscc_data_str += " AND center_id = " + str(center_id)
    # else:
    #     # return empty
    #     vw_mscc_data_str += " AND id=0 "
    #
    # if first_name != '':
    #     vw_mscc_data_str += " AND child_first_name LIKE '%" + first_name + "%'"
    # if father_name != '':
    #     vw_mscc_data_str += " AND child_father_name LIKE '%" + father_name + "%'"
    # if last_name != '':
    #     vw_mscc_data_str += " AND child_last_name LIKE '%" + last_name + "%'"
    # if mother_fullname != '':
    #     vw_mscc_data_str += " AND child_mother_fullname LIKE '%" + mother_fullname + "%'"
    # if nationality != '':
    #     vw_mscc_data_str += " AND child_nationality_id = " + nationality


    cursor.execute(vw_youth_data_str)
    data = cursor.fetchall()

    headers = [col[0] for col in cursor.description]

    workbook = Workbook()
    worksheet_all_data = workbook.create_sheet("All Data")
    worksheet_all_data.append(headers)

    for row in data:
        worksheet_all_data.append(row)


    default_sheet = workbook.get_sheet_by_name('Sheet')
    workbook.remove(default_sheet)

    # Set the appropriate response headers for the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response


class PDListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = PDTable
    model = ProgramDocument
    template_name = 'youth/pd_list.html'
    table = BootstrapTable(ProgramDocument.objects.all(), order_by='id')
    group_required = [u"YOUTH"]

    filterset_class = PDFilter

    def get_queryset(self):
        return ProgramDocument.objects.all()

    def get_table_class(self):
        return PDTable

    def get_filterset_class(self):
        return PDFilter


def load_districts(request):
    cities = []
    if request.GET.get('id_adolescent_governorate'):
        id_adolescent_governorate = request.GET.get('id_adolescent_governorate')
        print(id_adolescent_governorate)
        cities = Location.objects.filter(parent_id=id_adolescent_governorate).order_by('name')
        print(cities)
    return render(request, 'youth/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    cities = []
    if request.GET.get('id_adolescent_district'):
        id_adolescent_district = request.GET.get('id_adolescent_district')
        cities = Location.objects.filter(parent_id=id_adolescent_district).order_by('name')
    return render(request, 'youth/cadaster_dropdown_list_options.html', {'cities': cities})


def load_program_document(request):
    program_documents = []
    if request.GET.get('id_donor'):
        id_donor = request.GET.get('id_donor')
        program_documents = ProgramDocument.objects.filter(partner_id=id_donor).order_by('project_name')
    return render(request, 'youth/program_document_dropdown_list_options.html', {'program_documents': program_documents})


def load_master_program(request):
    master_programs = []
    if request.GET.get('id_program_document'):
        id_program_document = request.GET.get('id_program_document')
        master_programs = MasterProgram.objects.filter(
            programdocument__id=id_program_document
        )
    return render(request, 'youth/master_program_dropdown_list_options.html', {'master_programs': master_programs})


def load_sub_program(request):
    sub_programs = []
    if request.GET.get('id_master_program'):
        id_master_program = request.GET.get('id_master_program')
        sub_programs = SubProgram.objects.filter(master_program_id=id_master_program).order_by('name')
    return render(request, 'youth/sub_program_dropdown_list_options.html', {'sub_programs': sub_programs})
