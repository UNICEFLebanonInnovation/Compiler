# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from collections import defaultdict
from django.views.generic import DetailView, ListView, UpdateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from django.db.models import F , Q
from django.urls import reverse
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from fuzzywuzzy import fuzz
from django.shortcuts import redirect, render
from django.db import connection
import csv
import codecs
import logging
import traceback
from student_registration.students.utils import generate_one_unique_id
from student_registration.students.models import Nationality

from .filters import (
    MainFilter,
    FullFilter,
    PartnerFilter,
    PDFilter,
    PDPartnerFilter
)
from .tables import (
    RegistrationTable,
    PDTable,
    PDPartnerTable

)
from .models import (
    ProgramDocument,
    SubProgram,
    EnrolledPrograms,
    ProgramDocumentIndicator,
    Donor
)

from .forms import (
    MainForm,
)
from .serializers import (
    MainSerializer
)

from .utils import *

from student_registration.users.templatetags.custom_tags import has_group
from student_registration.locations import views as location_views

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'youth/dashboard.html'


def _indicator_number_sort_key(indicator):
    try:
        return (0, [int(p) for p in indicator.number.split('.')])
    except (AttributeError, ValueError):
        return (1, indicator.number or '')


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
    success_url = '/youth/List/'
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


def main_mark_delete_view(request, pk):
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


class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = RegistrationTable
    model = Registration
    template_name = 'youth/list.html'
    group_required = [u"YOUTH"]

    filterset_class = MainFilter

    def get_queryset(self):
        user = self.request.user
        partner_id = user.partner_id

        qs = (
            Registration.objects.filter(deleted=False)
                .select_related(
                'adolescent',
                'adolescent__disability',
                'adolescent__nationality',
                'adolescent__governorate',
                'adolescent__district',
                'adolescent__cadaster',
                'partner',
                'owner',
                'modified_by',
            )
                .order_by('-id')
        )
        if has_group(user, 'YOUTH_UNICEF'):
            pass
        elif has_group(user, 'YOUTH_PARTNER') and partner_id is not None:
            qs = qs.filter(partner_id=partner_id)
        else:
            return Registration.objects.none()
        return qs.distinct()

    def get_table_class(self):
        return RegistrationTable

    def get_filterset_class(self):
        if has_group(self.request.user, 'YOUTH_UNICEF'):
            return FullFilter
        elif has_group(self.request.user, 'YOUTH_PARTNER'):
            return PartnerFilter
        return PartnerFilter


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
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        birthday_year = body.get('birthday_year')
        birthday_month = body.get('birthday_month')
        birthday_day = body.get('birthday_day')
        first_name = body.get('first_name')
        father_name = body.get('father_name')
        last_name = body.get('last_name')
        mother_fullname = body.get('mother_fullname')
        sex = body.get('sex')
        nationality_id = body.get('nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(birthday_year, birthday_month, birthday_day)
        unicef_id = generate_one_unique_id(
            '0',
            first_name,
            father_name,
            last_name,
            mother_fullname,
            birthdate,
            nationality,
            sex
        )

        if unicef_id:
            qs = Registration.objects.filter(
                adolescent__unicef_id=unicef_id,
                deleted=False
            )
            if registration_id:
                qs = qs.exclude(pk=registration_id)

            latest = qs.order_by('-id').values('id', 'partner__name').first()
            if latest:
                return JsonResponse({
                    'has_duplicate': True,
                    'partner_name': latest['partner__name'],
                    'registration_id': latest['id'],
                })

        return JsonResponse({'has_duplicate': False})


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


@login_required(login_url='/users/login')
def export_data(request, **kwargs):
    try:
        user = request.user
        partner_id = user.partner_id

        partner = request.GET.get('partner', '')
        governorate = request.GET.get('governorate', '')
        district = request.GET.get('district', '')
        cadaster = request.GET.get('cadaster', '')
        adolescent_first_name = request.GET.get('adolescent_first_name', '')
        adolescent_father_name = request.GET.get('adolescent_father_name', '')
        adolescent_last_name = request.GET.get('adolescent_last_name', '')
        adolescent_unicef_id = request.GET.get('adolescent_unicef_id', '')
        adolescent_gender = request.GET.get('adolescent_gender', '')
        adolescent_nationality = request.GET.get('adolescent_nationality', '')
        adolescent_disability = request.GET.get('adolescent_disability', '')
        adolescent_first_phone_number = request.GET.get('adolescent_first_phone_number', '')
        master_program = request.GET.get('master_program', '')
        sub_program = request.GET.get('sub_program', '')
        donor = request.GET.get('donor', '')
        program_document = request.GET.get('program_document', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        registration_qs = Registration.objects.filter(deleted=False)

        def _safe_int(value):
            if value in (None, "", "undefined", "null"):
                return None
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        print("partner: ", partner)
        partner_id_filter = _safe_int(partner)
        if partner_id_filter is not None:
            registration_qs = registration_qs.filter(partner__id=partner_id_filter)

        if governorate:
            registration_qs = registration_qs.filter(adolescent__governorate__id=governorate)

        if district:
            registration_qs = registration_qs.filter(adolescent__district__id=district)

        if cadaster:
            registration_qs = registration_qs.filter(adolescent__cadaster__id=cadaster)

        if adolescent_first_name:
            registration_qs = registration_qs.filter(adolescent__first_name__icontains=adolescent_first_name)

        if adolescent_father_name:
            registration_qs = registration_qs.filter(adolescent__father_name__icontains=adolescent_father_name)

        if adolescent_last_name:
            registration_qs = registration_qs.filter(adolescent__last_name__icontains=adolescent_last_name)

        if adolescent_unicef_id:
            registration_qs = registration_qs.filter(adolescent__unicef_id__icontains=adolescent_unicef_id)

        if adolescent_gender:
            registration_qs = registration_qs.filter(adolescent__gender=adolescent_gender)

        if adolescent_nationality:
            registration_qs = registration_qs.filter(adolescent__nationality_id=adolescent_nationality)

        if adolescent_disability:
            registration_qs = registration_qs.filter(adolescent__disability__id=adolescent_disability)

        if adolescent_first_phone_number:
            registration_qs = registration_qs.filter(adolescent__first_phone_number__icontains=adolescent_first_phone_number)

        # EnrolledPrograms-related filters
        if any([master_program, sub_program, donor, program_document, start_date, end_date]):
            registration_qs = registration_qs.prefetch_related('enrolled_programs')

            if master_program:
                master_program_ids = master_program.split(",")
                registration_qs = registration_qs.filter(enrolled_programs__master_program__id__in=master_program_ids)

            if sub_program:
                sub_program_ids = sub_program.split(",")
                registration_qs = registration_qs.filter(enrolled_programs__sub_program__id__in=sub_program_ids)

            if donor:
                registration_qs = registration_qs.filter(enrolled_programs__donor__id=donor)

            if program_document:
                registration_qs = registration_qs.filter(enrolled_programs__program_document__id=program_document)

            if start_date:
                try:
                    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    registration_qs = registration_qs.filter(enrolled_programs__completion_date__gte=start_date_obj)
                except ValueError:
                    pass

            if end_date:
                try:
                    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    registration_qs = registration_qs.filter(enrolled_programs__completion_date__lte=end_date_obj)
                except ValueError:
                    pass

        registration_ids = list(registration_qs.values_list('id', flat=True).distinct())
        # vw_youth_data query
        cursor = connection.cursor()

        cursor = connection.cursor()
        query_params = []

        vw_youth_data_str = "SELECT * FROM vw_youth_data WHERE deleted = 'false'"

        if registration_ids:
            vw_youth_data_str += " AND id = ANY(%s)"
            query_params.append(registration_ids)
        else:
            vw_youth_data_str += " AND 1 = 0"  # No results

        if has_group(user, 'YOUTH_UNICEF'):
            vw_youth_data_str += " AND id > 0"
        elif has_group(user, 'YOUTH_PARTNER') and partner_id:
            vw_youth_data_str += " AND partner_id = %s"
            query_params.append(partner_id)
        else:
            vw_youth_data_str += " AND id = 0"

        # Log the query to the console before execution
        logger.debug("Executing Query:")
        mogrified_query = cursor.mogrify(vw_youth_data_str, query_params)
        if isinstance(mogrified_query, bytes):
            mogrified_query = mogrified_query.decode('utf-8')
        logger.debug(mogrified_query)
        cursor.execute(vw_youth_data_str, query_params)

        headers = [col[0] for col in cursor.description]

        # Prepare CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="youth_registration_data.csv"'
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)

        for row in cursor.fetchall():
            writer.writerow([
                cell.strftime('%Y-%m-%d') if isinstance(cell, (datetime.date, datetime.datetime)) else cell
                for cell in row
            ])

        return response

    except Exception as e:
        logging.error("Export failed:", exc_info=True)
        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/users/login')
def export_pd_data(request, **kwargs):
    try:
        user = request.user
        partner_id = getattr(user, "partner_id", None)

        partner = request.GET.get('partner', '').strip()
        funded_by = request.GET.get('funded_by', '').strip()
        project_status = request.GET.get('project_status', '').strip()
        project_code = request.GET.get('project_code', '').strip()
        project_name = request.GET.get('project_name', '').strip()
        implementing_partners = request.GET.get('implementing_partners', '').strip()
        focal_point = request.GET.get('focal_point', '').strip()
        start_date = request.GET.get('start_date', '').strip()
        end_date = request.GET.get('end_date', '').strip()
        donor = request.GET.get('donor', '').strip()
        master_program = request.GET.get('master_program', '').strip()

        queryset = ProgramDocument.objects.all()

        if partner.isdigit():
            queryset = queryset.filter(partner__id=int(partner))
        if funded_by.isdigit():
            queryset = queryset.filter(funded_by__id=int(funded_by))
        if project_status.isdigit():
            queryset = queryset.filter(project_status__id=int(project_status))
        if project_code:
            queryset = queryset.filter(project_code__icontains=project_code)
        if project_name:
            queryset = queryset.filter(project__icontains=project_name)
        if implementing_partners:
            queryset = queryset.filter(implementing_partners__icontains=implementing_partners)
        if focal_point.isdigit():
            queryset = queryset.filter(focal_point__id=int(focal_point))
        if start_date:
            try:
                start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(start_date__gte=start_date_obj)
            except ValueError:
                pass
        if end_date:
            try:
                end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(end_date__lte=end_date_obj)
            except ValueError:
                pass
        if donor.isdigit():
            queryset = queryset.filter(donors__id=int(donor))
        if master_program:
            master_program_ids = [int(mp) for mp in master_program.split(",") if mp.isdigit()]
            if master_program_ids:
                queryset = queryset.filter(master_program__id__in=master_program_ids)

        pd_ids = list(queryset.values_list('id', flat=True).distinct())

        sql = "SELECT * FROM vw_youth_pd WHERE id > 0"
        params = []

        if pd_ids:
            placeholders = ",".join(["%s"] * len(pd_ids))
            sql += f" AND id IN ({placeholders})"
            params.extend(pd_ids)
        else:
            sql += " AND 1 = 0"

        # User group filtering
        if has_group(user, 'YOUTH_UNICEF'):
            pass
        elif has_group(user, 'YOUTH_PARTNER') and partner_id:
            sql += " AND partner_id = %s"
            params.append(partner_id)
        else:
            sql += " AND id = 0"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            headers = [col[0] for col in cursor.description]  # now valid
            rows = cursor.fetchall()

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=youth_pd_data.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)

        for row in rows:
            writer.writerow([
                cell.strftime('%Y-%m-%d') if isinstance(cell, (datetime.date, datetime.datetime)) else cell
                for cell in row
            ])

        return response

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)


class PDListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = PDTable
    model = ProgramDocument
    template_name = 'youth/pd_list.html'
    group_required = [u"YOUTH"]

    filterset_class = PDFilter

    def get_queryset(self):
        user = self.request.user
        partner_id = user.partner_id

        qs = (
            ProgramDocument.objects.select_related(
                'partner',
                'funded_by',
                'project_status',
                'focal_point',
                'plan',
                'sectors',
                'project_type',
            )
            .prefetch_related(
                'governorates',
                'population_groups',
                'donors',
                'indicators__master_indicator',
            )
            .order_by('-id')
        )

        if has_group(user, 'YOUTH_UNICEF'):
            pass
        elif has_group(user, 'YOUTH_PARTNER') and partner_id is not None:
            qs = qs.filter(partner_id=partner_id)
        else:
            return ProgramDocument.objects.none()

        return qs.distinct()

    def get_table_class(self):
        if has_group(self.request.user, 'YOUTH_UNICEF'):
            return PDTable
        elif has_group(self.request.user, 'YOUTH_PARTNER'):
            return PDPartnerTable
        return PDPartnerTable

    def get_filterset_class(self):
        if has_group(self.request.user, 'YOUTH_UNICEF'):
            return PDFilter
        elif has_group(self.request.user, 'YOUTH_PARTNER'):
            return PDPartnerFilter
        return PDPartnerFilter


load_districts = location_views.load_districts
load_cadasters = location_views.load_cadasters


def _get_accessible_program_documents(request):
    program_documents = ProgramDocument.objects.all()
    if (
        has_group(request.user, 'YOUTH_PARTNER')
        and request.user.partner_id
    ):
        program_documents = program_documents.filter(partner_id=request.user.partner_id)
    elif not has_group(request.user, 'YOUTH_UNICEF'):
        program_documents = ProgramDocument.objects.none()
    return program_documents


def load_program_document(request):
    program_documents = _get_accessible_program_documents(request).order_by('project_name')
    return render(request, 'youth/program_document_dropdown_list_options.html', {'program_documents': program_documents})


def load_donor(request):
    donors = Donor.objects.none()
    if request.GET.get('id_program_document'):
        id_program_document = request.GET.get('id_program_document')
        program_document = _get_accessible_program_documents(request).filter(id=id_program_document).first()
        if program_document:
            donors = program_document.donors.filter(active=True).order_by('name')
    return render(request, 'youth/donor_dropdown_list_options.html', {'donors': donors})


def load_master_program(request):
    master_programs = []

    # Check if 'id_program_document' is provided in the GET request
    if request.GET.get('id_program_document'):
        id_program_document = request.GET.get('id_program_document')

        # Fetch the ProgramDocument by id
        program_document = _get_accessible_program_documents(request).filter(id=id_program_document).first()

        if program_document:
            master_programs = MasterProgram.objects.filter(
                id__in=program_document.indicators
                    .filter(master_indicator__isnull=False)
                    .values_list('master_indicator_id', flat=True)
                    .distinct()
            )

    return render(request, 'youth/master_program_dropdown_list_options.html', {
        'master_programs': master_programs
    })


def load_sub_program(request):
    sub_programs = []

    master_program_ids = request.GET.getlist('id_master_program[]') or request.GET.getlist('id_master_program')
    if request.GET.get('id_master_program'):
        master_program_ids.append(request.GET.get('id_master_program'))

    master_program_ids = [
        program_id
        for raw_program_id in master_program_ids
        for program_id in str(raw_program_id).split(',')
        if program_id
    ]

    if master_program_ids:
        sub_program_queryset = SubProgram.objects.filter(master_program_id__in=master_program_ids)

        program_document_id = request.GET.get('id_program_document')
        if program_document_id:
            program_document = _get_accessible_program_documents(request).filter(id=program_document_id).first()
            if program_document:
                sub_program_queryset = sub_program_queryset.filter(
                    id__in=program_document.indicators
                        .filter(sub_indicator__isnull=False)
                        .values_list('sub_indicator_id', flat=True)
                        .distinct()
                )
            else:
                sub_program_queryset = SubProgram.objects.none()

        sub_programs = sorted(
            sub_program_queryset,
            key=_indicator_number_sort_key
        )

    selected_sub_program_ids = request.GET.getlist('selected_sub_program[]') or request.GET.getlist('selected_sub_program')
    if request.GET.get('selected_sub_program'):
        selected_sub_program_ids.append(request.GET.get('selected_sub_program'))

    selected_sub_program_ids = [
        sub_program_id
        for raw_sub_program_id in selected_sub_program_ids
        for sub_program_id in str(raw_sub_program_id).split(',')
        if sub_program_id
    ]

    return render(request, 'youth/sub_program_dropdown_list_options.html', {
        'sub_programs': sub_programs,
        'selected_sub_program_ids': selected_sub_program_ids,
    })


def program_document_indicators_view(request, program_document_id):

    masters = list(MasterProgram.objects.filter(active=True)
                   .order_by('number', 'name')
                   .values('id', 'name', 'number')
                   )

    master_indicators = [
        {
            "id": m["id"],
            "name": "{} - {}".format(m.get("number", ""), m["name"]).strip(" -")
        }
        for m in masters
    ]

    subs = SubProgram.objects.filter(
        master_program_id__in=[m["id"] for m in masters]
    ).order_by('number', 'name').values('id', 'name', 'number', 'master_program_id')

    sub_indicator_map = defaultdict(list)
    for sp in subs:
        sub_indicator_map[sp["master_program_id"]].append({
            "id": sp["id"],
            "name": "{} - {}".format(sp.get("number", ""), sp["name"]).strip(" -")
        })

    return render(request, 'youth/program_document_indicator.html', {
        'program_document_id': program_document_id,
        'master_indicators': master_indicators,
        'sub_indicators': json.dumps(sub_indicator_map, ensure_ascii=False),
    })

def program_document_indicator_list_view(request, program_document_id):
    try:
        indicators = ProgramDocumentIndicator.objects.filter(program_document_id=program_document_id)
        data = []
        for ind in indicators:
            data.append({
                'id': ind.id,
                'master_indicator_id': ind.master_indicator.id if ind.master_indicator else None,
                'master_indicator_name': ind.master_indicator.name if ind.master_indicator else '',
                'sub_indicator_id': ind.sub_indicator.id if ind.sub_indicator else None,
                'sub_indicator_name': ind.sub_indicator.name if ind.sub_indicator else '',
                'baseline': ind.baseline,
                'target': ind.target
            })
        return JsonResponse({'indicators': data})
    except Exception as e:
        print("Error in program_document_indicator_list_view:", e)
        # return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def save_indicators(request):
    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))
        indicators = payload.get('indicators', [])
        deleted_ids = payload.get('deleted_ids', [])

        if deleted_ids:
            ProgramDocumentIndicator.objects.filter(id__in=deleted_ids).delete()

        for item in indicators:
            if item['id']:
                try:
                    indicator = ProgramDocumentIndicator.objects.get(id=item['id'])
                except ProgramDocumentIndicator.DoesNotExist:
                    continue
            else:
                indicator = ProgramDocumentIndicator()

            indicator.program_document_id = item.get('program_document_id')
            indicator.master_indicator_id = item.get('master_indicator') or None
            indicator.sub_indicator_id = item.get('sub_indicator') or None
            baseline_value = item.get('baseline')
            indicator.baseline = (
                baseline_value if baseline_value not in (None, '') else None
            )
            indicator.target = item.get('target') or None
            indicator.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid method'}, status=400)
