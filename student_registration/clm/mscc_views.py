# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func, When
from django.db.models.expressions import RawSQL
from django.core.urlresolvers import reverse
from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.backends.djqscsv import render_to_csv_response
from student_registration.users.utils import force_default_language
from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer
from student_registration.schools.models import CLMRound
from student_registration.locations.models import Location
from student_registration.students.models import Person
from .mscc_filters import (
    MSCCFilter
)
from .mscc_tables import (
    BootstrapTable,
    MSCCTable,
    MSCCYouthTable,
    MSCCCPTable,
    MSCCHealthTable
)
from .models import (
    MSCC,
    Disability,
    Center,
    Outreach,
)
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    CLMRound,
    EducationalLevel,
    PartnerOrganization,
)
from .mscc_forms import (
    MSCCForm,
    MSCCEducationSituationForm,
    DiagnosticAssessmentForm,
    EducationAssessmentForm
)
from .mscc_serializers import (
    MSCCSerializer
)
from .utils import is_allowed_create, is_allowed_edit


class CLMView(LoginRequiredMixin,
              GroupRequiredMixin,
              TemplateView):
    template_name = 'clm/index.html'

    group_required = [u"CLM"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        return {}


def assessment_form(instance_id, stage, enrollment_model, assessment_slug, callback=''):
    try:
        assessment = Assessment.objects.get(slug=assessment_slug)
        return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]={enrollment_model}&returnURL={callback}'.format(
            form=assessment.assessment_form,
            status=stage,
            enrollment_model=enrollment_model,
            enrollment_id=instance_id,
            callback=callback
        )
    except Assessment.DoesNotExist:
        return ''


class MSCCAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'clm/mscc_create_form.html'
    form_class = MSCCForm
    success_url = '/clm/mscc-list/'
    group_required = [u"CLM_MSCC"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/mscc-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/mscc-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='MSCC',
                assessment_slug='mscc_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:mscc_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('MSCC')
        return super(MSCCAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(MSCCAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = MSCC.objects.get(id=self.request.GET.get('enrollment_id'))
            data = MSCCSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data

        if self.request.GET.get('outreach_id'):
            instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
            data = MSCCSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(MSCCAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return MSCCForm(self.request.POST, instance=None, request=self.request)
        else:
            return MSCCForm(None, instance=None, request=self.request, initial=self.get_initial())


class MSCCEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'clm/mscc_edit_form.html'
    form_class = MSCCForm
    success_url = '/clm/mscc-list/'
    group_required = [u"CLM_MSCC"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/mscc-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/mscc-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='MSCC',
                assessment_slug='mscc_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:mscc_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('MSCC')
        return super(MSCCEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = MSCC.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return MSCCForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = MSCCSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            # if 'pre_test' in data:
            #     p_test = data['pre_test']
                # if p_test:
                    # if "BLN_ASSESSMENT/attended_arabic" in p_test:
                    #     data['attended_arabic'] = p_test["BLN_ASSESSMENT/attended_arabic"]
                    #
                    # if "BLN_ASSESSMENT/modality_arabic" in p_test:
                    #     data['modality_arabic'] = p_test["BLN_ASSESSMENT/modality_arabic"]
                    #
                    # if "BLN_ASSESSMENT/arabic" in p_test:
                    #     data['arabic'] = p_test["BLN_ASSESSMENT/arabic"]
                    #
                    # if "BLN_ASSESSMENT/attended_english" in p_test:
                    #     data['attended_english'] = p_test["BLN_ASSESSMENT/attended_english"]
                    #
                    # if "BLN_ASSESSMENT/modality_english" in p_test:
                    #     data['modality_english'] = p_test["BLN_ASSESSMENT/modality_english"]
                    #
                    # if "BLN_ASSESSMENT/english" in p_test:
                    #     data['english'] = p_test["BLN_ASSESSMENT/english"]
                    #
                    # if "BLN_ASSESSMENT/attended_math" in p_test:
                    #     data['attended_math'] = p_test["BLN_ASSESSMENT/attended_math"]
                    #
                    # if "BLN_ASSESSMENT/modality_math" in p_test:
                    #     data['modality_math'] = p_test["BLN_ASSESSMENT/modality_math"]
                    #
                    # if "BLN_ASSESSMENT/math" in p_test:
                    #     data['math'] = p_test["BLN_ASSESSMENT/math"]
                    #
                    # if "BLN_ASSESSMENT/attended_social" in p_test:
                    #     data['attended_social'] = p_test["BLN_ASSESSMENT/attended_social"]
                    #
                    # if "BLN_ASSESSMENT/modality_social" in p_test:
                    #     data['modality_social'] = p_test["BLN_ASSESSMENT/modality_social"]
                    #
                    # if "BLN_ASSESSMENT/social_emotional" in p_test:
                    #     data['social_emotional'] = p_test["BLN_ASSESSMENT/social_emotional"]
                    #
                    # if "BLN_ASSESSMENT/attended_artistic" in p_test:
                    #     data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_artistic"]
                    # elif "BLN_ASSESSMENT/attended_psychomotor" in p_test:
                    #     data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_psychomotor"]
                    #
                    # if "BLN_ASSESSMENT/modality_artistic" in p_test:
                    #     data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_artistic"]
                    # elif "BLN_ASSESSMENT/modality_psychomotor" in p_test:
                    #     data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_psychomotor"]
                    #
                    # if "BLN_ASSESSMENT/modality_artistic" in p_test:
                    #     data['artistic'] = p_test["BLN_ASSESSMENT/artistic"]
                    # elif "BLN_ASSESSMENT/psychomotor" in p_test:
                    #     data['artistic'] = p_test["BLN_ASSESSMENT/psychomotor"]

            return MSCCForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = MSCC.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MSCCEditView, self).form_valid(form)


class MSCCListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = MSCCTable
    model = MSCC
    template_name = 'clm/mscc_list.html'
    table = BootstrapTable(MSCC.objects.all(), order_by='id')
    group_required = [u"CLM_MSCC"]

    filterset_class = MSCCFilter

    def get_queryset(self):
        force_default_language(self.request)

        return MSCC.objects.filter(partner=self.request.user.partner_id,
                                  round__current_year=True).order_by('-id')


class MSCCEducationSituationView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):

    template_name = 'clm/mscc_education_situation.html'
    form_class = MSCCEducationSituationForm
    success_url = '/clm/mscc-list/'
    group_required = [u"CLM_MSCC"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MSCCEducationSituationView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = MSCC.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = MSCC.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(MSCCEducationSituationView, self).form_valid(form)


class DiagnosticAssessmentView(LoginRequiredMixin,
                             GroupRequiredMixin,
                             FormView):
    template_name = 'clm/mscc_diagnostic_assessment.html'
    form_class = DiagnosticAssessmentForm
    success_url = '/clm/mscc-list/'
    group_required = [u"CLM_MSCC"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(DiagnosticAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = MSCC.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = MSCCSerializer(instance).data
            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:
                    print(p_test)
                    if "Diagnostic_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["Diagnostic_ASSESSMENT/attended_arabic"]

                    if "Diagnostic_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["Diagnostic_ASSESSMENT/modality_arabic"]

                    if "Diagnostic_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["Diagnostic_ASSESSMENT/arabic"]

                    if "Diagnostic_ASSESSMENT/attended_foreign_language" in p_test:
                        data['attended_foreign_language'] = p_test["Diagnostic_ASSESSMENT/attended_foreign_language"]

                    if "Diagnostic_ASSESSMENT/modality_foreign_language" in p_test:
                        data['modality_foreign_language'] = p_test["Diagnostic_ASSESSMENT/modality_foreign_language"]

                    if "Diagnostic_ASSESSMENT/foreign_language" in p_test:
                        data['foreign_language'] = p_test["Diagnostic_ASSESSMENT/foreign_language"]

                    if "Diagnostic_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["Diagnostic_ASSESSMENT/attended_math"]

                    if "Diagnostic_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["Diagnostic_ASSESSMENT/modality_math"]

                    if "Diagnostic_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Diagnostic_ASSESSMENT/math"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = MSCC.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(DiagnosticAssessmentView, self).form_valid(form)


class EducationAssessmentView(LoginRequiredMixin,
                             GroupRequiredMixin,
                             FormView):
    template_name = 'clm/mscc_education_assessment.html'
    form_class = EducationAssessmentForm
    success_url = '/clm/mscc-list/'
    group_required = [u"CLM_MSCC"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EducationAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = MSCC.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = MSCCSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "Education_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["Education_ASSESSMENT/attended_arabic"]

                    if "Education_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["Education_ASSESSMENT/modality_arabic"]

                    if "Education_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["Education_ASSESSMENT/arabic"]

                    if "Education_ASSESSMENT/attended_foreign_language" in p_test:
                        data['attended_foreign_language'] = p_test["Education_ASSESSMENT/attended_foreign_language"]

                    if "Education_ASSESSMENT/modality_foreign_language" in p_test:
                        data['modality_foreign_language'] = p_test["Education_ASSESSMENT/modality_foreign_language"]

                    if "Education_ASSESSMENT/foreign_language" in p_test:
                        data['foreign_language'] = p_test["Education_ASSESSMENT/foreign_language"]

                    if "Education_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["Education_ASSESSMENT/attended_math"]

                    if "Education_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["Education_ASSESSMENT/modality_math"]

                    if "Education_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Education_ASSESSMENT/math"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = MSCC.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(EducationAssessmentView, self).form_valid(form)


class MSCCYouthListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = MSCCYouthTable
    model = MSCC
    template_name = 'clm/mscc_youth_list.html'
    table = BootstrapTable(MSCC.objects.all(), order_by='id')
    group_required = [u"MSCC_YOUTH"]

    filterset_class = MSCCFilter

    def get_queryset(self):
        force_default_language(self.request)

        return MSCC.objects.filter(partner=self.request.user.partner_id,
                                  round__current_year=True).order_by('-id')


class MSCCHealthListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = MSCCHealthTable
    model = MSCC
    template_name = 'clm/mscc_health_list.html'
    table = BootstrapTable(MSCC.objects.all(), order_by='id')
    group_required = [u"MSCC_HEALTH"]

    filterset_class = MSCCFilter

    def get_queryset(self):
        force_default_language(self.request)

        return MSCC.objects.filter(partner=self.request.user.partner_id,
                                   round__current_year=True).order_by('-id')


class MSCCCPListView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         FilterView,
                         ExportMixin,
                         SingleTableView,
                         RequestConfig):
    table_class = MSCCCPTable
    model = MSCC
    template_name = 'clm/mscc_CP_list.html'
    table = BootstrapTable(MSCC.objects.all(), order_by='id')
    group_required = [u"MSCC_CP"]

    filterset_class = MSCCFilter

    def get_queryset(self):
        force_default_language(self.request)

        return MSCC.objects.filter(partner=self.request.user.partner_id,
                                   round__current_year=True).order_by('-id')


# ####################### API VIEWS #############################

class MSCCViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    model = MSCC
    queryset = MSCC.objects.all()
    serializer_class = MSCCSerializer
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


def load_districts(request):
    id_governorate = request.GET.get('id_governorate')
    cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    id_district = request.GET.get('id_district')
    cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    id_governorate = request.GET.get('id_governorate')
    schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})


def search_clm_child(request):
    # from django.db.models.functions import Concat
    # from django.db.models import Value

    clm_type = request.GET.get('clm_type', 'MSCC')
    term = request.GET.get('term', 0)
    terms = request.GET.get('term', 0)
    model = MSCC
    if clm_type == 'RS':
        model = RS
    elif clm_type == 'ABLN':
        model = ABLN
    elif clm_type == 'CBECE':
        model = CBECE
    elif clm_type == 'Outreach':
        model = Outreach
    elif clm_type == 'Bridging':
        model = Bridging

    search_model = clm_type

    qs = {}
    qs = clm_child_list(model, term, terms, search_model)

    if clm_type == 'Bridging' and len(qs) == 0:
        model = BLN
        search_model = 'BLN'
        qs = clm_child_list(model, term, terms, search_model)
        if len(list(qs)) == 0:
            model = ABLN
            search_model = 'ABLN'
            qs = clm_child_list(model, term, terms, search_model)
            if len(qs) == 0:
                model = CBECE
                search_model = 'CBECE'
                qs = clm_child_list(model, term, terms, search_model)

    return JsonResponse({'result': json.dumps(list(qs))})


def clm_child_list(model, term, terms, search_model):
    from django.db.models.functions import Concat
    from django.db.models import Value
    from django.db.models import CharField
    qs = {}
    if terms:
        if len(terms.split()) > 1:

            # .filter(partner=request.user.partner_id) \

            qs = model.objects.annotate(fullname=Concat('student__first_name', Value(' '),
                                                        'student__father_name', Value(' '),
                                                        'student__last_name')) \
                .filter(fullname__icontains=terms) \
                .values('id', 'student__first_name', 'student__father_name',
                        'student__last_name', 'student__mother_fullname',
                        'student__sex', 'student__birthday_day', 'student__birthday_month',
                        'student__birthday_year', 'round__name', 'internal_number').distinct().annotate(
                search_model=Value(search_model, output_field=CharField()))

        else:
            # for term in terms:
            # .filter(partner=request.user.partner_id)
            qs = model.objects \
                .filter(
                Q(student__first_name__contains=term) |
                Q(student__father_name__contains=term) |
                Q(student__last_name__contains=term) |
                Q(student__id_number__startswith=term) |
                Q(student__number__startswith=term) |
                Q(internal_number__startswith=term)
            ).values('id', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct().annotate(
                search_model=Value(search_model, output_field=CharField()))

    return qs


def search_clm_duplicate_registration(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    search_by = body['search_by']
    round_id = body['round_id']
    clm_type = body['clm_type']
    student_id = body['student_id']
    student_first_name = body['student_first_name']
    student_father_name = body['student_father_name']
    student_last_name = body['student_last_name']
    student_mother_fullname = body['student_mother_fullname']
    phone_number = body['phone_number']
    id_type = body['id_type']
    case_number = body['case_number']
    recorded_number = body['recorded_number']
    parent_syrian_national_number = body['parent_syrian_national_number']
    parent_sop_national_number = body['parent_sop_national_number']
    parent_national_number = body['parent_national_number']
    parent_other_number = body['parent_other_number']

    model = BLN
    if clm_type == 'BLN':
        model = BLN
    if clm_type == 'RS':
        model = RS
    elif clm_type == 'ABLN':
        model = ABLN
    elif clm_type == 'CBECE':
        model = CBECE
    elif clm_type == 'Outreach':
        model = Outreach
    elif clm_type == 'Bridging':
        model = Bridging

    str_partner_name = search_student(model, search_by, round_id, id_type, student_id, student_first_name,
                                      student_father_name, student_last_name, student_mother_fullname
                                      , phone_number, case_number, recorded_number,
                                      parent_syrian_national_number, parent_sop_national_number, parent_national_number,
                                      parent_other_number)

    if str_partner_name != '':
        return JsonResponse({'result': str_partner_name})
    elif clm_type == 'BLN':
        model = ABLN
        str_partner_name = search_student(model, search_by, round_id, id_type, student_id, student_first_name,
                                          student_father_name, student_last_name, student_mother_fullname,
                                          phone_number, case_number, recorded_number,
                                          parent_syrian_national_number, parent_sop_national_number,
                                          parent_national_number,
                                          parent_other_number)

        if str_partner_name != '':
            return JsonResponse({'result': str_partner_name})
    elif clm_type == 'ABLN':
        model = BLN
        str_partner_name = search_student(model, search_by, round_id, id_type, student_id, student_first_name,
                                          student_father_name, student_last_name, student_mother_fullname,
                                          phone_number, case_number, recorded_number,
                                          parent_syrian_national_number, parent_sop_national_number,
                                          parent_national_number,
                                          parent_other_number)

        if str_partner_name != '':
            return JsonResponse({'result': str_partner_name})

    return JsonResponse({'result': ''})


def search_student(model, search_by, round_id, id_type, student_id, student_first_name, student_father_name,
                   student_last_name, student_mother_fullname,
                   phone_number, case_number, recorded_number, parent_syrian_national_number,
                   parent_sop_national_number, parent_national_number, parent_other_number):
    from django.db.models.functions import Concat
    from django.db.models import Value

    model = model
    qs = {}
    if search_by == 'student id':
        qs = search_duplicate_student_id(model, round_id, student_id)
    elif search_by == 'student name':
        qs = search_duplicate_student_name(model, round_id, student_first_name, student_father_name, student_last_name,
                                           student_mother_fullname)
    elif search_by == 'phone':
        qs = search_duplicate_phone(model, round_id, student_first_name, phone_number)
    elif search_by == 'id':
        qs = search_duplicate_case(model, round_id, id_type, student_first_name, case_number, recorded_number,
                                   parent_syrian_national_number, parent_sop_national_number, parent_national_number,
                                   parent_other_number)
    str_partner_name = ''

    if qs:
        qsjson = json.dumps(list(qs))
        student = json.loads(qsjson)[0]
        partner_name = (student["partner__name"])
        str_partner_name = str(partner_name)

    return str_partner_name


def search_duplicate_student_id(model, round_id, student_id):
    model = model

    qs = {}
    if round_id:
        qs = model.objects.filter(
            round=round_id, student=student_id
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()
    else:
        qs = model.objects.filter(
            student=student_id
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()
    return qs


def search_duplicate_student_name(model, round_id, student_first_name, student_father_name, student_last_name,
                                  student_mother_fullname):
    model = model

    qs = {}
    if round_id:
        qs = model.objects.filter(
            round=round_id,
            student__first_name=student_first_name,
            student__father_name=student_father_name,
            student__last_name=student_last_name,
            student__mother_fullname=student_mother_fullname,
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()
    else:
        qs = model.objects.filter(
            student__first_name=student_first_name,
            student__father_name=student_father_name,
            student__last_name=student_last_name,
            student__mother_fullname=student_mother_fullname,
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()

    return qs


def search_duplicate_phone(model, round_id, student_first_name, phone_number):
    model = model
    qs = {}
    if round_id:
        qs = model.objects.filter(
            round=round_id,
            student__first_name=student_first_name,
            phone_number=phone_number
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()
    else:
        qs = model.objects.filter(
            student__first_name=student_first_name,
            phone_number=phone_number
        ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                 'student__last_name', 'student__mother_fullname',
                 'student__sex', 'student__birthday_day', 'student__birthday_month',
                 'student__birthday_year', 'round__name', 'internal_number').distinct()
    return qs


def search_duplicate_case(model, round_id, id_type, student_first_name, case_number, recorded_number,
                          parent_syrian_national_number, parent_sop_national_number, parent_national_number,
                          parent_other_number):
    model = model
    qs = {}
    if round_id:
        if id_type == 'UNHCR Registered':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                case_number=case_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'UNHCR Recorded':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                recorded_number=recorded_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Syrian national ID':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                parent_syrian_national_number=parent_syrian_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Palestinian national ID':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                parent_sop_national_number=parent_sop_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Lebanese national ID':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                parent_national_number=parent_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Other nationality':
            qs = model.objects.filter(
                round=round_id,
                student__first_name=student_first_name,
                parent_other_number=parent_other_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
    else:
        if id_type == 'UNHCR Registered':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                case_number=case_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'UNHCR Recorded':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                recorded_number=recorded_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Syrian national ID':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                parent_syrian_national_number=parent_syrian_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Palestinian national ID':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                parent_sop_national_number=parent_sop_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Lebanese national ID':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                parent_national_number=parent_national_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
        elif id_type == 'Other nationality':
            qs = model.objects.filter(
                student__first_name=student_first_name,
                parent_other_number=parent_other_number
            ).values('id', 'partner__name', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()
    return qs


