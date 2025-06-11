# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
import io
import csv
import logging
logging.basicConfig(level=logging.ERROR)
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import connection
import codecs
import logging
import traceback
from django.utils.encoding import force_str
import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func, When
from django.db.models.expressions import RawSQL
from django.urls import reverse
from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.users.utils import force_default_language
from student_registration.outreach.models import Child, OutreachChild
from student_registration.outreach.serializers import ChildSerializer
from student_registration.locations.models import Location
from .filters import (
    BLNFilter,
    ABLNFilter,
    RSFilter,
    CBECEFilter,
    GeneralQuestionnaireFilter,
    OutreachFilter,
    BridgingFilter
)
from .tables import (
    BLNTable,
    ABLNTable,
    RSTable,
    CBECETable,
    GeneralQuestionnaireTable,
    OutreachTable,
    BridgingTable
)
from .models import (
    BLN,
    ABLN,
    RS,
    CBECE,
    SelfPerceptionGrades,
    Disability,
    Assessment,
    ABLN_FC,
    BLN_FC,
    CBECE_FC,
    RS_FC,
    GeneralQuestionnaire,
    Outreach,
    Bridging,
    Inclusion
)
from student_registration.schools.models import (
    School,
    CLMRound,
)
from student_registration.backends.models import ExportHistory
from .forms import (
    BLNForm,
    ABLNForm,
    RSForm,
    RSAssessmentForm,
    CBECEForm,
    BLNReferralForm,
    BLNFollowupForm,
    ABLNReferralForm,
    ABLNFollowupForm,
    BLNAssessmentForm,
    ABLNAssessmentForm,
    CBECEAssessmentForm,
    BridgingAssessmentForm,
    BridgingMidAssessmentForm,
    BridgingFollowupForm,
    BridgingServiceForm,
    CBECEMidAssessmentForm,
    CBECEFollowupForm,
    CBECEReferralForm,
    CBECEMonitoringQuestionerForm,
    BLNMonitoringQuestionerForm,
    ABLNMonitoringQuestionerForm,
    ABLNFCForm,
    BLNFCForm,
    RSFCForm,
    CBECEFCForm,
    GeneralQuestionnaireForm,
    OutreachForm,
    BridgingForm
)
from .serializers import (
    BLNSerializer,
    ABLNSerializer,
    RSSerializer,
    CBECESerializer,
    SelfPerceptionGradesSerializer,
    ABLN_FCSerializer,
    BLN_FCSerializer,
    CBECE_FCSerializer,
    RS_FCSerializer,
    GeneralQuestionnaireSerializer,
    OutreachSerializer,
    BridgingSerializer
)
from .utils import is_allowed_create, is_allowed_edit, bln_build_xls_extraction, abln_build_xls_extraction, \
    cbece_build_xls_extraction, rs_build_xls_extraction, outreach_build_xls_extraction
from student_registration.users.templatetags.custom_tags import has_group


class CLMView(LoginRequiredMixin,
              GroupRequiredMixin,
              TemplateView):
    template_name = 'pages/home.old.html'

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


class BLNAddView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):
    template_name = 'clm/bln_create_form.html'
    form_class = BLNForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bln-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bln-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='BLN',
                assessment_slug='bln_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bln_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('BLN')
        return super(BLNAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(BLNAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = BLN.objects.get(id=self.request.GET.get('enrollment_id'))
            data = BLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data

        if self.request.GET.get('outreach_id'):
            instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
            data = BLNSerializer(instance).data
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
        return super(BLNAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return BLNForm(self.request.POST, instance=None, request=self.request)
        else:
            return BLNForm(None, instance=None, request=self.request, initial=self.get_initial())


class BLNEditView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'clm/bln_edit_form.html'
    form_class = BLNForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bln-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bln-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='BLN',
                assessment_slug='bln_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bln_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('BLN')
        return super(BLNEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = BLN.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return BLNForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = BLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:
                    if "BLN_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["BLN_ASSESSMENT/attended_arabic"]

                    if "BLN_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["BLN_ASSESSMENT/modality_arabic"]

                    if "BLN_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["BLN_ASSESSMENT/arabic"]

                    if "BLN_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["BLN_ASSESSMENT/attended_english"]

                    if "BLN_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["BLN_ASSESSMENT/modality_english"]

                    if "BLN_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["BLN_ASSESSMENT/english"]

                    if "BLN_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["BLN_ASSESSMENT/attended_math"]

                    if "BLN_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["BLN_ASSESSMENT/modality_math"]

                    if "BLN_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["BLN_ASSESSMENT/math"]

                    if "BLN_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["BLN_ASSESSMENT/attended_social"]

                    if "BLN_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["BLN_ASSESSMENT/modality_social"]

                    if "BLN_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["BLN_ASSESSMENT/social_emotional"]

                    if "BLN_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_artistic"]
                    elif "BLN_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_psychomotor"]

                    if "BLN_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_artistic"]
                    elif "BLN_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_psychomotor"]

                    if "BLN_ASSESSMENT/modality_artistic" in p_test:
                        data['artistic'] = p_test["BLN_ASSESSMENT/artistic"]
                    elif "BLN_ASSESSMENT/psychomotor" in p_test:
                        data['artistic'] = p_test["BLN_ASSESSMENT/psychomotor"]

            return BLNForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BLNEditView, self).form_valid(form)


class BLNMonitoringQuestionerView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'clm/bln_monitoring_questioner.html'
    form_class = BLNMonitoringQuestionerForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNMonitoringQuestionerView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(BLNMonitoringQuestionerView, self).form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class AssessmentSubmission(SingleObjectMixin, View):
    model = RS
    slug_url_kwarg = 'status'

    def post(self, request, *args, **kwargs):

        if 'status' not in request.body and \
            'enrollment_id' not in request.body and \
            'enrollment_model' not in request.body:
            return HttpResponseBadRequest()

        payload = json.loads(request.body.decode('utf-8'))
        status = payload['status']
        enrollment_id = payload['enrollment_id']
        model = payload['enrollment_model']
        static_model_value = payload['static_model_value'] if 'static_model_value' in payload else ''

        if model == 'BLN' or 'BLN_ASSESSMENT/arabic' in payload:
            enrollment = BLN.objects.get(id=int(enrollment_id))
        elif model == 'ABLN' or 'ABLN_ASSESSMENT/arabic' in payload:
            enrollment = ABLN.objects.get(id=int(enrollment_id))
        elif model == 'CBECE':
            enrollment = CBECE.objects.get(id=int(enrollment_id))
        # elif model == 'RS':
        #     enrollment = RS.objects.get(id=int(enrollment_id))
        else:
            enrollment = CBECE.objects.get(id=int(enrollment_id))

        enrollment.status = status
        setattr(enrollment, status, payload)
        enrollment.calculate_score(status)
        enrollment.save()

        return HttpResponse()


class BLNListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):
    table_class = BLNTable
    model = BLN
    template_name = 'clm/bln_list.html'
    table = BLNTable(BLN.objects.all(), order_by='id')
    group_required = [u"CLM_BLN"]

    filterset_class = BLNFilter

    def get_queryset(self):
        force_default_language(self.request)

        return BLN.objects.filter(partner=self.request.user.partner_id,
                                  round__current_year=True).order_by('-id')
        # return BLN.objects.filter(partner=self.request.user.partner_id,
        #                             round__end_date_bln__year=Person.CURRENT_YEAR).order_by('-id')
        # return BLN.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by('-id')


class BLNReferralView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'clm/bln_referral.html'
    form_class = BLNReferralForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNReferralView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(BLNReferralView, self).form_valid(form)


class BLNFollowupView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'clm/bln_followup.html'
    form_class = BLNFollowupForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNFollowupView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(BLNFollowupView, self).form_valid(form)


class BLNDashboardView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       TemplateView):
    template_name = 'clm/bln_dashboard.html'
    model = BLN
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)

        per_gov = []
        clm_round = self.request.user.partner.bln_round
        clm_rounds = CLMRound.objects.all()
        governorates = Location.objects.filter(parent__isnull=True)

        # queryset = BLN.objects.filter(round=clm_round)
        queryset = self.model.objects.all()
        total_male = queryset.filter(student__sex='Male')
        total_female = queryset.filter(student__sex='Female')

        completion = queryset.exclude(learning_result='repeat_level')
        completion_male = completion.filter(student__sex='Male')
        completion_female = completion.filter(student__sex='Female')

        attendance = queryset.filter(participation__isnull=False)
        attendances_male = attendance.filter(student__sex='Male')
        attendances_female = attendance.filter(student__sex='Female')

        repeat_class = queryset.filter(learning_result='repeat_level')
        repeat_class_male = repeat_class.filter(student__sex='Male')
        repeat_class_female = repeat_class.filter(student__sex='Female')

        for gov in governorates:
            total_gov = queryset.filter(governorate=gov).count()
            total_male_gov = total_male.filter(governorate=gov).count()
            total_female_gov = total_female.filter(governorate=gov).count()

            completion_gov = completion.filter(governorate=gov).count()
            completion_male_gov = completion_male.filter(governorate=gov).count()
            completion_female_gov = completion_female.filter(governorate=gov).count()

            attendance_gov = attendance.filter(governorate=gov).count()
            attendances_male_gov = attendances_male.filter(governorate=gov)
            attendances_female_gov = attendances_female.filter(governorate=gov)

            repeat_class_male_gov = repeat_class_male.filter(governorate=gov).count()
            repeat_class_female_gov = repeat_class_female.filter(governorate=gov).count()

            per_gov.append({
                'governorate': gov.name,
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov),
                                         2) if total_male_gov else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov),
                                           2) if total_female_gov else 0.0,

                'attendance_male_1': round((float(attendances_male_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_1': round((float(attendances_female_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_2': round((float(attendances_male_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_2': round((float(attendances_female_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_3': round((float(attendances_male_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_3': round((float(attendances_female_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_4': round((float(attendances_male_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_4': round((float(attendances_female_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0,
                                         2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0,
                                           2) if total_gov else 0.0,
            })

        return {
            'clm_round': clm_round,
            'clm_rounds': clm_rounds,
            'per_gov': per_gov
        }


class ABLNAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'clm/abln_create_form.html'
    form_class = ABLNForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/abln-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/abln-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='ABLN',
                assessment_slug='abln_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:abln_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('ABLN')
        return super(ABLNAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(ABLNAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = ABLN.objects.get(id=self.request.GET.get('enrollment_id'))
            data = ABLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('outreach_id'):
            instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
            data = BLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(ABLNAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return ABLNForm(self.request.POST, instance=None, request=self.request)
        else:
            return ABLNForm(None, instance=None, request=self.request, initial=self.get_initial())


class ABLNEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'clm/abln_edit_form.html'
    form_class = ABLNForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/abln-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/abln-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='ABLN',
                assessment_slug='abln_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:abln_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('ABLN')
        return super(ABLNEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = ABLN.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return ABLNForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = ABLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:
                    if "ABLN_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["ABLN_ASSESSMENT/attended_arabic"]

                    if "ABLN_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["ABLN_ASSESSMENT/modality_arabic"]

                    if "ABLN_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["ABLN_ASSESSMENT/arabic"]

                    if "ABLN_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["ABLN_ASSESSMENT/attended_english"]

                    if "ABLN_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["ABLN_ASSESSMENT/modality_english"]

                    if "ABLN_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["ABLN_ASSESSMENT/english"]

                    if "ABLN_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["ABLN_ASSESSMENT/attended_math"]

                    if "ABLN_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["ABLN_ASSESSMENT/modality_math"]

                    if "ABLN_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["ABLN_ASSESSMENT/math"]

                    if "ABLN_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["ABLN_ASSESSMENT/attended_social"]

                    if "ABLN_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["ABLN_ASSESSMENT/modality_social"]

                    if "ABLN_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["ABLN_ASSESSMENT/social_emotional"]

                    if "ABLN_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["ABLN_ASSESSMENT/attended_artistic"]

                    if "ABLN_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["ABLN_ASSESSMENT/modality_artistic"]

                    if "ABLN_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["ABLN_ASSESSMENT/artistic"]

            return ABLNForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(ABLNEditView, self).form_valid(form)


class ABLNMonitoringQuestionerView(LoginRequiredMixin,
                                   GroupRequiredMixin,
                                   FormView):
    template_name = 'clm/abln_monitoring_questioner.html'
    form_class = ABLNMonitoringQuestionerForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ABLNMonitoringQuestionerView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(ABLNMonitoringQuestionerView, self).form_valid(form)


class ABLNListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = ABLNTable
    model = ABLN
    template_name = 'clm/abln_list.html'
    table = ABLNTable(ABLN.objects.all(), order_by='id')
    group_required = [u"CLM_ABLN"]

    filterset_class = ABLNFilter

    def get_queryset(self):
        force_default_language(self.request)

        return ABLN.objects.filter(partner=self.request.user.partner_id,
                                   round__current_year=True).order_by('-id')

        # return ABLN.objects.filter(partner=self.request.user.partner_id,
        #                             round__end_date_abln__year=Person.CURRENT_YEAR).order_by('-id')
        # return ABLN.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by(
        #     '-id')


class ABLNReferralView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'clm/abln_referral.html'
    form_class = ABLNReferralForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ABLNReferralView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(ABLNReferralView, self).form_valid(form)


class ABLNPostAssessmentView(LoginRequiredMixin,
                             GroupRequiredMixin,
                             FormView):
    template_name = 'clm/abln_post_assessment.html'
    form_class = ABLNAssessmentForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ABLNPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = ABLN.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = ABLNSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "ABLN_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["ABLN_ASSESSMENT/attended_arabic"]

                    if "ABLN_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["ABLN_ASSESSMENT/modality_arabic"]

                    if "ABLN_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["ABLN_ASSESSMENT/arabic"]

                    if "ABLN_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["ABLN_ASSESSMENT/attended_english"]

                    if "ABLN_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["ABLN_ASSESSMENT/modality_english"]

                    if "ABLN_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["ABLN_ASSESSMENT/english"]

                    if "ABLN_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["ABLN_ASSESSMENT/attended_math"]

                    if "ABLN_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["ABLN_ASSESSMENT/modality_math"]

                    if "ABLN_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["ABLN_ASSESSMENT/math"]

                    if "ABLN_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["ABLN_ASSESSMENT/attended_social"]

                    if "ABLN_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["ABLN_ASSESSMENT/modality_social"]

                    if "ABLN_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["ABLN_ASSESSMENT/social_emotional"]

                    if "ABLN_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["ABLN_ASSESSMENT/attended_artistic"]

                    if "ABLN_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["ABLN_ASSESSMENT/modality_artistic"]

                    if "ABLN_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["ABLN_ASSESSMENT/artistic"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(ABLNPostAssessmentView, self).form_valid(form)


class ABLNFCAddView(LoginRequiredMixin,
                    GroupRequiredMixin,
                    FormView):
    template_name = 'clm/abln_fc_form.html'
    form_class = ABLNFCForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ABLNFCAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(ABLNFCAddView, self).get_initial()
        data = {
            'enrollment_id': self.kwargs['enrollment_id'],
            'fc_type': self.kwargs['fc_type']
        }

        data['enrollment_id'] = self.kwargs['enrollment_id']
        data['fc_type'] = self.kwargs['fc_type']
        initial = data

        return initial

    def get_form(self, form_class=None):

        instance = ABLN_FC.objects.filter(enrollment_id=self.kwargs['enrollment_id'],
                                          fc_type=self.kwargs['fc_type']).first()

        if self.request.method == "POST":
            data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}

            return ABLNFCForm(self.request.POST, initial=data, instance=instance, request=self.request)
        else:
            if instance:
                data = ABLN_FCSerializer(instance).data

                return ABLNFCForm(data, initial=data, instance=instance, request=self.request)

            else:
                data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}
                fc_type = self.kwargs['fc_type'].split('-')
                if len(fc_type) >= 1:
                    data['subject_taught'] = fc_type[0]
                return ABLNFCForm(initial=data, request=self.request)

    def form_valid(self, form):
        instance = ABLN_FC.objects.filter(enrollment_id=int(self.kwargs['enrollment_id']),
                                          fc_type=self.kwargs['fc_type']).first()

        if instance:
            form.save(request=self.request, instance=instance)
        else:
            form.save(self.request)

        return super(ABLNFCAddView, self).form_valid(form)


class BLNFCAddView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'clm/bln_fc_form.html'
    form_class = BLNFCForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNFCAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(BLNFCAddView, self).get_initial()
        data = {
            'enrollment_id': self.kwargs['enrollment_id'],
            'fc_type': self.kwargs['fc_type']
        }

        data['enrollment_id'] = self.kwargs['enrollment_id']
        data['fc_type'] = self.kwargs['fc_type']
        initial = data

        return initial

    def get_form(self, form_class=None):

        instance = BLN_FC.objects.filter(enrollment_id=self.kwargs['enrollment_id'],
                                         fc_type=self.kwargs['fc_type']).first()

        if self.request.method == "POST":
            data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}
            return BLNFCForm(self.request.POST, initial=data, instance=instance, request=self.request)
        else:
            if instance:
                data = BLN_FCSerializer(instance).data
                return BLNFCForm(data, initial=data, instance=instance, request=self.request)

            else:
                data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}
                splittedFCType = self.kwargs['fc_type'].split('-')
                if len(splittedFCType) >= 1:
                    data['subject_taught'] = splittedFCType[0]
                return BLNFCForm(initial=data, request=self.request)

    def form_valid(self, form):
        instance = BLN_FC.objects.filter(enrollment_id=int(self.kwargs['enrollment_id']),
                                         fc_type=self.kwargs['fc_type']).first()

        if instance:
            form.save(request=self.request, instance=instance)
        else:
            form.save(self.request)

        return super(BLNFCAddView, self).form_valid(form)


class RSFCAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'clm/rs_fc_form.html'
    form_class = RSFCForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(RSFCAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(RSFCAddView, self).get_initial()
        data = {
            'enrollment_id': self.kwargs['enrollment_id'],
            'fc_type': self.kwargs['fc_type']
        }

        data['enrollment_id'] = self.kwargs['enrollment_id']
        data['fc_type'] = self.kwargs['fc_type']
        initial = data

        return initial

    def get_form(self, form_class=None):

        instance = RS_FC.objects.filter(enrollment_id=self.kwargs['enrollment_id'],
                                        fc_type=self.kwargs['fc_type']).first()

        if self.request.method == "POST":
            data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}

            return RSFCForm(self.request.POST, initial=data, instance=instance, request=self.request)
        else:
            if instance:
                data = RS_FCSerializer(instance).data

                return RSFCForm(data, initial=data, instance=instance, request=self.request)

            else:
                data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}
                splittedFCType = self.kwargs['fc_type'].split('-')
                if len(splittedFCType) >= 1:
                    data['subject_taught'] = splittedFCType[0]
                return RSFCForm(initial=data, request=self.request)

    def form_valid(self, form):
        instance = RS_FC.objects.filter(enrollment_id=int(self.kwargs['enrollment_id']),
                                        fc_type=self.kwargs['fc_type']).first()

        if instance:
            form.save(request=self.request, instance=instance)
        else:
            form.save(self.request)

        return super(RSFCAddView, self).form_valid(form)


class CBECEFCAddView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     FormView):
    template_name = 'clm/cbece_fc_form.html'
    form_class = CBECEFCForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEFCAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(CBECEFCAddView, self).get_initial()
        data = {
            'enrollment_id': self.kwargs['enrollment_id'],
            'fc_type': self.kwargs['fc_type']
        }

        data['enrollment_id'] = self.kwargs['enrollment_id']
        data['fc_type'] = self.kwargs['fc_type']
        initial = data

        return initial

    def get_form(self, form_class=None):

        instance = CBECE_FC.objects.filter(enrollment_id=self.kwargs['enrollment_id'],
                                           fc_type=self.kwargs['fc_type']).first()

        if self.request.method == "POST":
            data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}

            return CBECEFCForm(self.request.POST, initial=data, instance=instance, request=self.request)
        else:
            if instance:
                data = CBECE_FCSerializer(instance).data

                return CBECEFCForm(data, initial=data, instance=instance, request=self.request)

            else:
                data = {'enrollment_id': self.kwargs['enrollment_id'], 'fc_type': self.kwargs['fc_type']}
                splittedFCType = self.kwargs['fc_type'].split('-')
                if len(splittedFCType) >= 1:
                    data['subject_taught'] = splittedFCType[0]
                return CBECEFCForm(initial=data, request=self.request)

    def form_valid(self, form):
        instance = CBECE_FC.objects.filter(enrollment_id=int(self.kwargs['enrollment_id']),
                                           fc_type=self.kwargs['fc_type']).first()

        if instance:
            form.save(request=self.request, instance=instance)
        else:
            form.save(self.request)

        return super(CBECEFCAddView, self).form_valid(form)


class BLNPostAssessmentView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bln_post_assessment.html'
    form_class = BLNAssessmentForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = BLN.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BLNSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "BLN_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["BLN_ASSESSMENT/attended_arabic"]

                    if "BLN_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["BLN_ASSESSMENT/modality_arabic"]

                    if "BLN_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["BLN_ASSESSMENT/arabic"]

                    if "BLN_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["BLN_ASSESSMENT/attended_english"]

                    if "BLN_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["BLN_ASSESSMENT/modality_english"]

                    if "BLN_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["BLN_ASSESSMENT/english"]

                    if "BLN_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["BLN_ASSESSMENT/attended_math"]

                    if "BLN_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["BLN_ASSESSMENT/modality_math"]

                    if "BLN_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["BLN_ASSESSMENT/math"]

                    if "BLN_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["BLN_ASSESSMENT/attended_social"]

                    if "BLN_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["BLN_ASSESSMENT/modality_social"]

                    if "BLN_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["BLN_ASSESSMENT/social_emotional"]

                    if "BLN_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_artistic"]
                    elif "BLN_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_artistic'] = p_test["BLN_ASSESSMENT/attended_psychomotor"]

                    if "BLN_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_artistic"]
                    elif "BLN_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_psychomotor"]

                    if "BLN_ASSESSMENT/modality_artistic" in p_test:
                        data['artistic'] = p_test["BLN_ASSESSMENT/artistic"]
                    elif "BLN_ASSESSMENT/psychomotor" in p_test:
                        data['artistic'] = p_test["BLN_ASSESSMENT/psychomotor"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(BLNPostAssessmentView, self).form_valid(form)


class BridgingPostAssessmentView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_post_assessment.html'
    form_class = BridgingAssessmentForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                        data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                        data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                    if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                        data['arabic_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/arabic_reading_comprehension"]

                    if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                        data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                        data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                    if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                        data['english_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/english_reading_comprehension"]

                    if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                        data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                        data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                    if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                        data['french_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/french_reading_comprehension"]

                    if "Bridging_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Bridging_ASSESSMENT/math"]
                    # if "Bridging_ASSESSMENT/artistic" in p_test:
                    #     data['artistic'] = p_test["Bridging_ASSESSMENT/artistic"]
                    # if "Bridging_ASSESSMENT/social_emotional" in p_test:
                    #     data['social_emotional'] = p_test["Bridging_ASSESSMENT/social_emotional"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingPostAssessmentView, self).form_valid(form)



class BridgingMidAssessmentView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_mid_assessment.html'
    form_class = BridgingMidAssessmentForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['number'] = self.kwargs['number'] if 'number' in self.kwargs else None
        return super(BridgingMidAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        number = int(self.kwargs.get('number', 1))

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance,number=number, request=self.request)
        else:
            data = BridgingSerializer(instance).data
            p_test = ''
            if number == 1 and 'mid_test1' in data:
                p_test = data['mid_test1']
            elif number == 2 and 'mid_test2' in data:
                p_test = data['mid_test2']

            if p_test:
                if "Bridging_ASSESSMENT/mid_test_done" in p_test:
                    data['mid_test_done'] = p_test["Bridging_ASSESSMENT/mid_test_done"]

                if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                    data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                    data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                    data['arabic_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/arabic_reading_comprehension"]

                if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                    data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                    data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                    data['english_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/english_reading_comprehension"]

                if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                    data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                    data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                    data['french_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/french_reading_comprehension"]

                if "Bridging_ASSESSMENT/math" in p_test:
                    data['math'] = p_test["Bridging_ASSESSMENT/math"]

            return form_class(data, instance=instance, number=number, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        number = self.kwargs['number'] if 'number' in self.kwargs else None
        form.save(request=self.request, number=number, instance=instance)
        return super(BridgingMidAssessmentView, self).form_valid(form)


class BridgingFollowupView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_followup.html'
    form_class = BridgingFollowupForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingFollowupView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingFollowupView, self).form_valid(form)


class BridgingServiceView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_service.html'
    form_class = BridgingServiceForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingServiceView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingServiceView, self).form_valid(form)


class CBECEPostAssessmentView(LoginRequiredMixin,
                              GroupRequiredMixin,
                              FormView):
    template_name = 'clm/cbece_post_assessment.html'
    form_class = CBECEAssessmentForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = CBECE.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = CBECESerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "CBECE_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["CBECE_ASSESSMENT/attended_arabic"]

                    if "CBECE_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["CBECE_ASSESSMENT/modality_arabic"]

                    if "CBECE_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["CBECE_ASSESSMENT/arabic"]

                    if "CBECE_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["CBECE_ASSESSMENT/attended_english"]

                    if "CBECE_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["CBECE_ASSESSMENT/modality_english"]

                    if "CBECE_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["CBECE_ASSESSMENT/english"]

                    if "CBECE_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["CBECE_ASSESSMENT/attended_math"]

                    if "CBECE_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["CBECE_ASSESSMENT/modality_math"]

                    if "CBECE_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["CBECE_ASSESSMENT/math"]

                    if "CBECE_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["CBECE_ASSESSMENT/attended_social"]

                    if "CBECE_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["CBECE_ASSESSMENT/modality_social"]

                    if "CBECE_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["CBECE_ASSESSMENT/social_emotional"]

                    if "CBECE_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_psychomotor'] = p_test["CBECE_ASSESSMENT/attended_psychomotor"]

                    if "CBECE_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_psychomotor'] = p_test["CBECE_ASSESSMENT/modality_psychomotor"]

                    if "CBECE_ASSESSMENT/psychomotor" in p_test:
                        data['psychomotor'] = p_test["CBECE_ASSESSMENT/psychomotor"]

                    if "CBECE_ASSESSMENT/attended_science" in p_test:
                        data['attended_science'] = p_test["CBECE_ASSESSMENT/attended_science"]

                    if "CBECE_ASSESSMENT/modality_science" in p_test:
                        data['modality_science'] = p_test["CBECE_ASSESSMENT/modality_science"]

                    if "CBECE_ASSESSMENT/science" in p_test:
                        data['science'] = p_test["CBECE_ASSESSMENT/science"]

                    if "CBECE_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["CBECE_ASSESSMENT/attended_artistic"]

                    if "CBECE_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["CBECE_ASSESSMENT/modality_artistic"]

                    if "CBECE_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["CBECE_ASSESSMENT/artistic"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(CBECEPostAssessmentView, self).form_valid(form)


class CBECEMidAssessmentView(LoginRequiredMixin,
                             GroupRequiredMixin,
                             FormView):
    template_name = 'clm/cbece_mid_assessment.html'
    form_class = CBECEMidAssessmentForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEMidAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = CBECE.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = CBECESerializer(instance).data
            if 'mid_test' in data:
                p_test = data['mid_test']

                if p_test:
                    if "CBECE_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["CBECE_ASSESSMENT/attended_arabic"]

                    if "CBECE_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["CBECE_ASSESSMENT/modality_arabic"]

                    if "CBECE_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["CBECE_ASSESSMENT/arabic"]

                    if "CBECE_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["CBECE_ASSESSMENT/attended_english"]

                    if "CBECE_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["CBECE_ASSESSMENT/modality_english"]

                    if "CBECE_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["CBECE_ASSESSMENT/english"]

                    if "CBECE_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["CBECE_ASSESSMENT/attended_math"]

                    if "CBECE_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["CBECE_ASSESSMENT/modality_math"]

                    if "CBECE_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["CBECE_ASSESSMENT/math"]

                    if "CBECE_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["CBECE_ASSESSMENT/attended_social"]

                    if "CBECE_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["CBECE_ASSESSMENT/modality_social"]

                    if "CBECE_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["CBECE_ASSESSMENT/social_emotional"]

                    if "CBECE_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_psychomotor'] = p_test["CBECE_ASSESSMENT/attended_psychomotor"]

                    if "CBECE_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_psychomotor'] = p_test["CBECE_ASSESSMENT/modality_psychomotor"]

                    if "CBECE_ASSESSMENT/psychomotor" in p_test:
                        data['psychomotor'] = p_test["CBECE_ASSESSMENT/psychomotor"]

                    if "CBECE_ASSESSMENT/attended_science" in p_test:
                        data['attended_science'] = p_test["CBECE_ASSESSMENT/attended_science"]

                    if "CBECE_ASSESSMENT/modality_science" in p_test:
                        data['modality_science'] = p_test["CBECE_ASSESSMENT/modality_science"]

                    if "CBECE_ASSESSMENT/science" in p_test:
                        data['science'] = p_test["CBECE_ASSESSMENT/science"]

                    if "CBECE_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["CBECE_ASSESSMENT/attended_artistic"]

                    if "CBECE_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["CBECE_ASSESSMENT/modality_artistic"]

                    if "CBECE_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["CBECE_ASSESSMENT/artistic"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(CBECEMidAssessmentView, self).form_valid(form)


class RSPostAssessmentView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           FormView):
    template_name = 'clm/rs_post_assessment.html'
    form_class = RSAssessmentForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(RSPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = RS.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = RSSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:

                    if "RS_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["RS_ASSESSMENT/attended_arabic"]

                    if "RS_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["RS_ASSESSMENT/modality_arabic"]

                    if "RS_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["RS_ASSESSMENT/arabic"]

                    if "RS_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["RS_ASSESSMENT/attended_english"]

                    if "RS_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["RS_ASSESSMENT/modality_english"]

                    if "RS_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["RS_ASSESSMENT/english"]

                    if "RS_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["RS_ASSESSMENT/attended_math"]

                    if "RS_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["RS_ASSESSMENT/modality_math"]

                    if "RS_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["RS_ASSESSMENT/math"]

                    if "RS_ASSESSMENT/attended_science" in p_test:
                        data['attended_science'] = p_test["RS_ASSESSMENT/attended_science"]

                    if "RS_ASSESSMENT/modality_science" in p_test:
                        data['modality_science'] = p_test["RS_ASSESSMENT/modality_science"]

                    if "RS_ASSESSMENT/science" in p_test:
                        data['science'] = p_test["RS_ASSESSMENT/science"]

                    if "RS_ASSESSMENT/attended_biology" in p_test:
                        data['attended_biology'] = p_test["RS_ASSESSMENT/attended_biology"]

                    if "RS_ASSESSMENT/modality_biology" in p_test:
                        data['modality_biology'] = p_test["RS_ASSESSMENT/modality_biology"]

                    if "RS_ASSESSMENT/biology" in p_test:
                        data['biology'] = p_test["RS_ASSESSMENT/biology"]

                    if "RS_ASSESSMENT/attended_chemistry" in p_test:
                        data['attended_chemistry'] = p_test["RS_ASSESSMENT/attended_chemistry"]

                    if "RS_ASSESSMENT/modality_chemistry" in p_test:
                        data['modality_chemistry'] = p_test["RS_ASSESSMENT/modality_chemistry"]

                    if "RS_ASSESSMENT/chemistry" in p_test:
                        data['chemistry'] = p_test["RS_ASSESSMENT/chemistry"]

                    if "RS_ASSESSMENT/attended_physics" in p_test:
                        data['attended_physics'] = p_test["RS_ASSESSMENT/attended_physics"]

                    if "RS_ASSESSMENT/modality_physics" in p_test:
                        data['modality_physics'] = p_test["RS_ASSESSMENT/modality_physics"]

                    if "RS_ASSESSMENT/physics" in p_test:
                        data['physics'] = p_test["RS_ASSESSMENT/physics"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = RS.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(RSPostAssessmentView, self).form_valid(form)


class ABLNFollowupView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'clm/abln_followup.html'
    form_class = ABLNFollowupForm
    success_url = '/clm/abln-list/'
    group_required = [u"CLM_ABLN"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(ABLNFollowupView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(ABLNFollowupView, self).form_valid(form)


class RSDashboardView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      TemplateView):
    template_name = 'clm/rs_dashboard.html'
    model = RS
    group_required = [u"CLM_RS"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)

        per_gov = []
        clm_round = self.request.user.partner.rs_round
        clm_rounds = CLMRound.objects.all()
        governorates = Location.objects.filter(parent__isnull=True)
        disability = Disability.objects.filter(active=True)

        # queryset = self.model.objects.filter(round=clm_round)
        queryset = self.model.objects.all()
        total_male = queryset.filter(student__sex='Male')
        total_female = queryset.filter(student__sex='Female')

        completion = queryset.exclude(learning_result='repeat_level')
        completion_male = completion.filter(student__sex='Male')
        completion_female = completion.filter(student__sex='Female')

        attendance = queryset.filter(participation__isnull=False)
        attendances_male = attendance.filter(student__sex='Male')
        attendances_female = attendance.filter(student__sex='Female')

        repeat_class = queryset.filter(learning_result='repeat_level')
        repeat_class_male = repeat_class.filter(student__sex='Male')
        repeat_class_female = repeat_class.filter(student__sex='Female')

        student_male = queryset.filter(student__sex='Male')
        student_female = queryset.filter(student__sex='Female')

        dis_gov = []

        for gov in governorates:

            total_gov = queryset.filter(governorate=gov).count()
            total_male_gov = total_male.filter(governorate=gov).count()
            total_female_gov = total_female.filter(governorate=gov).count()

            completion_gov = completion.filter(governorate=gov).count()
            completion_male_gov = completion_male.filter(governorate=gov).count()
            completion_female_gov = completion_female.filter(governorate=gov).count()

            attendance_gov = attendance.filter(governorate=gov).count()
            attendances_male_gov = attendances_male.filter(governorate=gov)
            attendances_female_gov = attendances_female.filter(governorate=gov)

            repeat_class_male_gov = repeat_class_male.filter(governorate=gov).count()
            repeat_class_female_gov = repeat_class_female.filter(governorate=gov).count()

            per_gov.append({
                'governorate': gov.name,
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov),
                                         2) if total_male_gov else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov),
                                           2) if total_female_gov else 0.0,

                'attendance_male_1': round((float(attendances_male_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_1': round((float(attendances_female_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_2': round((float(attendances_male_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_2': round((float(attendances_female_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_3': round((float(attendances_male_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_3': round((float(attendances_female_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_4': round((float(attendances_male_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_4': round((float(attendances_female_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0,
                                         2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0,
                                           2) if total_gov else 0.0,

                'repetition_male1': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0,
                                          2) if total_gov else 0.0,
                'repetition_female1': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0,
                                            2) if total_gov else 0.0,
            })

            dis_count = []
            for dis in disability:
                dis_count.append({
                    'student_male_dis': student_male.filter(governorate=gov, disability=dis).count(),
                    'student_female_dis': student_female.filter(governorate=gov, disability=dis).count(),
                })
            dis_gov.append({
                'governorate': gov.name,
                'dis': dis_count
            })
        return {
            'clm_round': clm_round,
            'clm_rounds': clm_rounds,
            'per_gov': per_gov,
            'disability': disability,
            'dis_gov': dis_gov
        }


class CBECEDashboardView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         TemplateView):
    template_name = 'clm/cbece_dashboard.html'
    model = CBECE
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)

        per_gov = []
        domain_gov = []
        clm_round = self.request.user.partner.cbece_round
        clm_rounds = CLMRound.objects.all()
        governorates = Location.objects.filter(parent__isnull=True)

        # queryset = self.model.objects.filter(round=clm_round)
        queryset = self.model.objects.all()
        total_male = queryset.filter(student__sex='Male')
        total_female = queryset.filter(student__sex='Female')

        completion = queryset.exclude(learning_result='repeat_level')
        completion_male = completion.filter(student__sex='Male')
        completion_female = completion.filter(student__sex='Female')

        attendance = queryset.filter(participation__isnull=False)
        attendances_male = attendance.filter(student__sex='Male')
        attendances_female = attendance.filter(student__sex='Female')

        repeat_class = queryset.filter(learning_result='repeat_level')
        repeat_class_male = repeat_class.filter(student__sex='Male')
        repeat_class_female = repeat_class.filter(student__sex='Female')

        for gov in governorates:
            total_gov = queryset.filter(governorate=gov).count()
            total_male_gov = total_male.filter(governorate=gov)
            total_female_gov = total_female.filter(governorate=gov)

            completion_gov = completion.filter(governorate=gov).count()
            completion_male_gov = completion_male.filter(governorate=gov).count()
            completion_female_gov = completion_female.filter(governorate=gov).count()

            attendance_gov = attendance.filter(governorate=gov).count()
            attendances_male_gov = attendances_male.filter(governorate=gov)
            attendances_female_gov = attendances_female.filter(governorate=gov)

            repeat_class_male_gov = repeat_class_male.filter(governorate=gov).count()
            repeat_class_female_gov = repeat_class_female.filter(governorate=gov).count()

            per_gov.append({
                'governorate': gov.name,
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov.count()),
                                         2) if total_male_gov.count() else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov.count()),
                                           2) if total_female_gov.count() else 0.0,

                'attendance_male_1': round((float(attendances_male_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_1': round((float(attendances_female_gov.filter(
                    participation='less_than_5days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_2': round((float(attendances_male_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_2': round((float(attendances_female_gov.filter(
                    participation='5_10_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_3': round((float(attendances_male_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_3': round((float(attendances_female_gov.filter(
                    participation='10_15_days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'attendance_male_4': round((float(attendances_male_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                           2) if attendance_gov else 0.0,
                'attendance_female_4': round((float(attendances_female_gov.filter(
                    participation='more_than_15days').count()) / float(attendance_gov)) * 100.0,
                                             2) if attendance_gov else 0.0,

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0,
                                         2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0,
                                           2) if total_gov else 0.0,
            })

            d1_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_LanguageArtDomain')::float)", params=[]),
                                              post=RawSQL("((scores->>'post_LanguageArtDomain')::float)",
                                                          params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d1_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_LanguageArtDomain')::float)", params=[]),
                                                  post=RawSQL("((scores->>'post_LanguageArtDomain')::float)",
                                                              params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d3_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_CognitiveDomain')::float)", params=[]),
                                              post=RawSQL("((scores->>'post_CognitiveDomain')::float)",
                                                          params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d3_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_CognitiveDomain')::float)", params=[]),
                                                  post=RawSQL("((scores->>'post_CognitiveDomain')::float)",
                                                              params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d4_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_SocialEmotionalDomain')::float)", params=[]),
                                              post=RawSQL("((scores->>'post_SocialEmotionalDomain')::float)",
                                                          params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d4_female = total_female_gov.annotate(
                pre=RawSQL("((scores->>'pre_SocialEmotionalDomain')::float)", params=[]),
                post=RawSQL("((scores->>'post_SocialEmotionalDomain')::float)", params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d5_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_PsychomotorDomain')::float)", params=[]),
                                              post=RawSQL("((scores->>'post_PsychomotorDomain')::float)",
                                                          params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d5_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_PsychomotorDomain')::float)", params=[]),
                                                  post=RawSQL("((scores->>'post_PsychomotorDomain')::float)",
                                                              params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d6_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_ArtisticDomain')::float)", params=[]),
                                              post=RawSQL("((scores->>'post_ArtisticDomain')::float)",
                                                          params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d6_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_ArtisticDomain')::float)", params=[]),
                                                  post=RawSQL("((scores->>'post_ArtisticDomain')::float)",
                                                              params=[])).aggregate(
                total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            domain_gov.append({
                'governorate': gov.name,

                'art_improvement_male': d1_male['total'] if d1_male['total'] != None else 0.0,
                'art_improvement_female': d1_female['total'] if d1_female['total'] != None else 0.0,

                'cognitive_improvement_male': d3_male['total'] if d3_male['total'] != None else 0.0,
                'cognitive_improvement_female': d3_female['total'] if d3_female['total'] != None else 0.0,

                'social_improvement_male': d4_male['total'] if d4_male['total'] != None else 0.0,
                'social_improvement_female': d4_female['total'] if d4_female['total'] != None else 0.0,

                'psycho_improvement_male': d5_male['total'] if d5_male['total'] != None else 0.0,
                'psycho_improvement_female': d5_female['total'] if d5_female['total'] != None else 0.0,

                'artistic_improvement_male': d6_male['total'] if d6_male['total'] != None else 0.0,
                'artistic_improvement_female': d6_female['total'] if d6_female['total'] != None else 0.0
            })

        return {
            'clm_round': clm_round,
            'clm_rounds': clm_rounds,
            'per_gov': per_gov,
            'domain_gov': domain_gov
        }


class RSAddView(LoginRequiredMixin,
                GroupRequiredMixin,
                FormView):
    template_name = 'clm/rs_create_form.html'
    form_class = RSForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/rs-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/rs-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='RS',
                assessment_slug='rs_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('RS')
        return super(RSAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(RSAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = RS.objects.get(id=self.request.GET.get('enrollment_id'))
            data = RSSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']

            data['learning_result'] = ''
        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(RSAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return RSForm(self.request.POST, instance=None, request=self.request)
        else:
            return RSForm(None, instance=None, request=self.request, initial=self.get_initial())


class RSEditView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):
    template_name = 'clm/rs_edit_form.html'
    form_class = RSForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/rs-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/rs-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='RS',
                assessment_slug='rs_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:rs_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('RS')
        return super(RSEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = RS.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return RSForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = RSSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']

            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:
                    if "RS_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["RS_ASSESSMENT/attended_arabic"]

                    if "RS_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["RS_ASSESSMENT/modality_arabic"]

                    if "RS_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["RS_ASSESSMENT/arabic"]

                    if "RS_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["RS_ASSESSMENT/attended_english"]

                    if "RS_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["RS_ASSESSMENT/modality_english"]

                    if "RS_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["RS_ASSESSMENT/english"]

                    if "RS_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["RS_ASSESSMENT/attended_math"]

                    if "RS_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["RS_ASSESSMENT/modality_math"]

                    if "RS_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["RS_ASSESSMENT/math"]

                    if "RS_ASSESSMENT/attended_science" in p_test:
                        data['attended_science'] = p_test["RS_ASSESSMENT/attended_science"]

                    if "RS_ASSESSMENT/modality_science" in p_test:
                        data['modality_science'] = p_test["RS_ASSESSMENT/modality_science"]

                    if "RS_ASSESSMENT/science" in p_test:
                        data['science'] = p_test["RS_ASSESSMENT/science"]

                    if "RS_ASSESSMENT/attended_biology" in p_test:
                        data['attended_biology'] = p_test["RS_ASSESSMENT/attended_biology"]

                    if "RS_ASSESSMENT/modality_biology" in p_test:
                        data['modality_biology'] = p_test["RS_ASSESSMENT/modality_biology"]

                    if "RS_ASSESSMENT/biology" in p_test:
                        data['biology'] = p_test["RS_ASSESSMENT/biology"]

                    if "RS_ASSESSMENT/attended_chemistry" in p_test:
                        data['attended_chemistry'] = p_test["RS_ASSESSMENT/attended_chemistry"]

                    if "RS_ASSESSMENT/modality_chemistry" in p_test:
                        data['modality_chemistry'] = p_test["RS_ASSESSMENT/modality_chemistry"]

                    if "RS_ASSESSMENT/chemistry" in p_test:
                        data['chemistry'] = p_test["RS_ASSESSMENT/chemistry"]

                    if "RS_ASSESSMENT/attended_physics" in p_test:
                        data['attended_physics'] = p_test["RS_ASSESSMENT/attended_physics"]

                    if "RS_ASSESSMENT/modality_physics" in p_test:
                        data['modality_physics'] = p_test["RS_ASSESSMENT/modality_physics"]

                    if "RS_ASSESSMENT/physics" in p_test:
                        data['physics'] = p_test["RS_ASSESSMENT/physics"]

            return RSForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = RS.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(RSEditView, self).form_valid(form)


class RSListView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FilterView,
                 ExportMixin,
                 SingleTableView,
                 RequestConfig):
    table_class = RSTable
    model = RS
    template_name = 'clm/rs_list.html'
    table = RSTable(RS.objects.all(), order_by='id')
    group_required = [u"CLM_RS"]

    filterset_class = RSFilter

    def get_queryset(self):
        force_default_language(self.request)

        return RS.objects.filter(partner=self.request.user.partner_id,
                                 round__current_year=True).order_by('-id')
        # return RS.objects.filter(partner=self.request.user.partner_id,
        #                             round__end_date_rs__year=Person.CURRENT_YEAR).order_by('-id')
        # return RS.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by('-id')


class CBECEAddView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'clm/cbece_create_form.html'
    form_class = CBECEForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/cbece-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/cbece-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='CBECE',
                assessment_slug='cbece_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:cbece_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('CBECE')
        return super(CBECEAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(CBECEAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = CBECE.objects.get(id=self.request.GET.get('enrollment_id'))
            data = CBECESerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''
        if self.request.GET.get('outreach_id'):
            instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
            data = BLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''
        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(CBECEAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return CBECEForm(self.request.POST, instance=None, request=self.request)
        else:
            return CBECEForm(None, instance=None, request=self.request, initial=self.get_initial())


class CBECEEditView(LoginRequiredMixin,
                    GroupRequiredMixin,
                    FormView):
    template_name = 'clm/cbece_edit_form.html'
    form_class = CBECEForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/cbece-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/cbece-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='CBECE',
                assessment_slug='cbece_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:cbece_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('CBECE')
        return super(CBECEEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = CBECE.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return CBECEForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = CBECESerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']

            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:
                    if "CBECE_ASSESSMENT/attended_arabic" in p_test:
                        data['attended_arabic'] = p_test["CBECE_ASSESSMENT/attended_arabic"]

                    if "CBECE_ASSESSMENT/modality_arabic" in p_test:
                        data['modality_arabic'] = p_test["CBECE_ASSESSMENT/modality_arabic"]

                    if "CBECE_ASSESSMENT/arabic" in p_test:
                        data['arabic'] = p_test["CBECE_ASSESSMENT/arabic"]

                    if "CBECE_ASSESSMENT/attended_english" in p_test:
                        data['attended_english'] = p_test["CBECE_ASSESSMENT/attended_english"]

                    if "CBECE_ASSESSMENT/modality_english" in p_test:
                        data['modality_english'] = p_test["CBECE_ASSESSMENT/modality_english"]

                    if "CBECE_ASSESSMENT/english" in p_test:
                        data['english'] = p_test["CBECE_ASSESSMENT/english"]

                    if "CBECE_ASSESSMENT/attended_math" in p_test:
                        data['attended_math'] = p_test["CBECE_ASSESSMENT/attended_math"]

                    if "CBECE_ASSESSMENT/modality_math" in p_test:
                        data['modality_math'] = p_test["CBECE_ASSESSMENT/modality_math"]

                    if "CBECE_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["CBECE_ASSESSMENT/math"]

                    if "CBECE_ASSESSMENT/attended_social" in p_test:
                        data['attended_social'] = p_test["CBECE_ASSESSMENT/attended_social"]

                    if "CBECE_ASSESSMENT/modality_social" in p_test:
                        data['modality_social'] = p_test["CBECE_ASSESSMENT/modality_social"]

                    if "CBECE_ASSESSMENT/social_emotional" in p_test:
                        data['social_emotional'] = p_test["CBECE_ASSESSMENT/social_emotional"]

                    if "CBECE_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_psychomotor'] = p_test["CBECE_ASSESSMENT/attended_psychomotor"]

                    if "CBECE_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_psychomotor'] = p_test["CBECE_ASSESSMENT/modality_psychomotor"]

                    if "CBECE_ASSESSMENT/psychomotor" in p_test:
                        data['psychomotor'] = p_test["CBECE_ASSESSMENT/psychomotor"]

                    if "CBECE_ASSESSMENT/attended_science" in p_test:
                        data['attended_science'] = p_test["CBECE_ASSESSMENT/attended_science"]

                    if "CBECE_ASSESSMENT/modality_science" in p_test:
                        data['modality_science'] = p_test["CBECE_ASSESSMENT/modality_science"]

                    if "CBECE_ASSESSMENT/science" in p_test:
                        data['science'] = p_test["CBECE_ASSESSMENT/science"]

                    if "CBECE_ASSESSMENT/attended_artistic" in p_test:
                        data['attended_artistic'] = p_test["CBECE_ASSESSMENT/attended_artistic"]

                    if "CBECE_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["CBECE_ASSESSMENT/modality_artistic"]

                    if "CBECE_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["CBECE_ASSESSMENT/artistic"]

            return CBECEForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(CBECEEditView, self).form_valid(form)


class CBECEMonitoringQuestionerView(LoginRequiredMixin,
                                    GroupRequiredMixin,
                                    FormView):
    template_name = 'clm/cbece_monitoring_questioner.html'
    form_class = CBECEMonitoringQuestionerForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEMonitoringQuestionerView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(CBECEMonitoringQuestionerView, self).form_valid(form)


class CBECEListView(LoginRequiredMixin,
                    GroupRequiredMixin,
                    FilterView,
                    ExportMixin,
                    SingleTableView,
                    RequestConfig):
    table_class = CBECETable
    model = CBECE
    template_name = 'clm/cbece_list.html'
    table = CBECETable(CBECE.objects.all(), order_by='id')
    group_required = [u"CLM_CBECE"]

    filterset_class = CBECEFilter

    def get_queryset(self):
        force_default_language(self.request)
        return CBECE.objects.filter(partner=self.request.user.partner_id,
                                    round__current_year=True).order_by('-id')

        # return CBECE.objects.filter(partner=self.request.user.partner_id,
        #                             round__end_date_cbece__year=Person.CURRENT_YEAR).order_by('-id')
        # return CBECE.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by('-id')


class GeneralQuestionnaireListView(LoginRequiredMixin,
                                   GroupRequiredMixin,
                                   FilterView,
                                   ExportMixin,
                                   SingleTableView,
                                   RequestConfig):
    table_class = GeneralQuestionnaireTable
    model = GeneralQuestionnaire
    template_name = 'clm/general_questionnaire_list.html'
    table = GeneralQuestionnaireTable(GeneralQuestionnaire.objects.all(), order_by='id')
    group_required = [u"CLM_General_Questionnaire"]

    filterset_class = GeneralQuestionnaireFilter

    def get_queryset(self):
        force_default_language(self.request)
        return GeneralQuestionnaire.objects.all().order_by('-id')


class GeneralQuestionnaireAddView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'clm/general_questionnaire_create_form.html'
    form_class = GeneralQuestionnaireForm
    success_url = '/clm/general-questionnaire-list/'
    group_required = [u"CLM_General_Questionnaire"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/general-questionnairen-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/general-questionnaire-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('GeneralQuestionnaire')
        return super(GeneralQuestionnaireAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(GeneralQuestionnaireAddView, self).get_initial()
        data = {
            'new_questionnaire': self.request.GET.get('new_questionnaire', ''),
        }
        if self.request.GET.get('questionnaire_id'):
            instance = GeneralQuestionnaire.objects.get(id=self.request.GET.get('questionnaire_id'))
            data = GeneralQuestionnaireSerializer(instance).data
        if data:
            data['new_questionnaire'] = self.request.GET.get('new_questionnaire', 'yes')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(GeneralQuestionnaireAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return GeneralQuestionnaireForm(self.request.POST, instance=None, request=self.request)
        else:
            return GeneralQuestionnaireForm(None, instance=None, request=self.request, initial=self.get_initial())


class GeneralQuestionnaireEditView(LoginRequiredMixin,
                                   GroupRequiredMixin,
                                   FormView):
    template_name = 'clm/general_questionnaire_edit_form.html'
    form_class = GeneralQuestionnaireForm
    success_url = '/clm/general_questionnaire_list/'
    group_required = [u"CLM_General_Questionnaire"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/general-questionnaire-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/general-questionnaire-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('GeneralQuestionnaire')
        return super(GeneralQuestionnaireEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = GeneralQuestionnaire.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return GeneralQuestionnaireForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = GeneralQuestionnaireSerializer(instance).data
            return GeneralQuestionnaireForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = GeneralQuestionnaire.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(GeneralQuestionnaireEditView, self).form_valid(form)


class CBECEReferralView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FormView):
    template_name = 'clm/cbece_referral.html'
    form_class = CBECEReferralForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEReferralView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(CBECEReferralView, self).form_valid(form)


class CBECEFollowupView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FormView):
    template_name = 'clm/cbece_followup.html'
    form_class = CBECEFollowupForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEFollowupView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(CBECEFollowupView, self).form_valid(form)


####################### API VIEWS #############################


class BLNViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    model = BLN
    # current_round = CLMRound.objects.filter(current_year=True)
    # queryset = BLN.objects.filter(round__in=current_round)
    queryset = BLN.objects.all()
    serializer_class = BLNSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]

        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class ABLNViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    model = ABLN
    # current_round = CLMRound.objects.filter(current_year=True)
    queryset = ABLN.objects.all()
    # .filter(round__in=current_round)
    serializer_class = ABLNSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]
        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class OutreachViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    model = Outreach
    queryset = Outreach.objects.all()
    serializer_class = OutreachSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]
        # if self.request.GET.get('school', None):
        #     return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class GeneralQuestionnaireViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    model = GeneralQuestionnaire
    queryset = GeneralQuestionnaire.objects.all()
    serializer_class = GeneralQuestionnaireSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]
        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()


class RSViewSet(mixins.RetrieveModelMixin,
                mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    model = RS
    # current_round = CLMRound.objects.filter(current_year=True)
    queryset = RS.objects.all()
    # .filter(round__in=current_round)
    serializer_class = RSSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime
        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]
        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class CBECEViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    model = CBECE
    # current_round = CLMRound.objects.filter(current_year=True)
    queryset = CBECE.objects.all()
    # .filter(round__in=current_round)
    serializer_class = CBECESerializer
    # serializer_class = CBECEExportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime
        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')[:5000]
            # .order_by('-id')
        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

        # rows = qs.order_by('id').values_list(
        #     'id',
        #     'new_registry',
        #     'partner',
        #     # 'round__name',
        #     # 'governorate__name_en',
        #     # 'district__name_en',
        #     # 'cadaster__name_en',
        #     'location',
        #     # 'center__name',
        #     'language',
        #     # 'student__address',
        #     'registration_level',
        #     'first_attendance_date',
        #     # 'student__id_number',
        #     # 'student__number',
        #     # 'student_first_name',
        #     # 'student_father_name',
        #     # 'student_last_name',
        #     # 'student_mother_fullname',
        #     # 'student_sex',
        #     # 'student__nationality__name',
        #     'other_nationality',
        #     # 'student__birthday_day',
        #     # 'student__birthday_month',
        #     # 'student__birthday_year',
        #     # 'student__p_code',
        #     # 'disability__name_en',
        #     'education_status',
        #     'miss_school_date',
        #     'internal_number',
        #     'rims_case_number',
        #     'source_of_identification',
        #     'source_of_identification_specify',
        #     'source_of_transportation',
        #     # 'hh_educational_level__name',
        #     # 'father_educational_level__name',
        #     'phone_number',
        #     'phone_owner',
        #     'second_phone_number',
        #     'second_phone_owner',
        #     'main_caregiver',
        #     # 'main_caregiver_nationality__name',
        #     'other_caregiver_relationship',
        #     'caretaker_first_name',
        #     'caretaker_middle_name',
        #     'caretaker_last_name',
        #     'caretaker_mother_name',
        #     'id_type',
        #     'case_number',
        #     'parent_individual_case_number',
        #     'individual_case_number',
        #     'recorded_number',
        #     'parent_national_number',
        #     'national_number',
        #     'parent_syrian_national_number',
        #     'syrian_national_number',
        #     'parent_sop_national_number',
        #     'sop_national_number',
        #     'parent_other_number',
        #     'other_number',
        #     # 'student__family_status',
        #     # 'student__have_children',
        #     'student_number_children',
        #     'have_labour_single_selection',
        #     'labours_single_selection',
        #     'labours_other_specify',
        #     'labour_hours',
        #     'labour_weekly_income',
        #     'participation',
        #     'barriers_single',
        #     'barriers_other',
        #     'round_complete',
        #     'basic_stationery',
        #     'pss_kit',
        #     'learning_result',
        #     'learning_result_other',
        #     'parent_attended_visits',
        #     # 'owner__username',
        #     # 'modified_by__username',
        # )[:100]

        return rows

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class BridgingViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    model = Bridging
    queryset = Bridging.objects.all()
    serializer_class = BridgingSerializer
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

# def BridgingDeleteView(request, pk):
#     if request.user.is_authenticated:
#         try:
#             registration =  Bridging.objects.get(pk=pk)
#             registration.delete()
#             result = {"isSuccessful": True}
#         except Bridging.DoesNotExist:
#             result = {"isSuccessful": False}
#     else:
#         result = {"isSuccessful": False}
#     return JsonResponse(result)


def BridgingMarkDeleteView(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Bridging.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            result = {"isSuccessful": True}
        except Bridging.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


class SelfPerceptionGradesViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    model = SelfPerceptionGrades
    queryset = SelfPerceptionGrades.objects.all()
    serializer_class = SelfPerceptionGradesSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CLMStudentViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    model = BLN
    queryset = BLN.objects.all()
    serializer_class = BLNSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        clm_type = self.request.GET.get('clm_type', 'BLN')
        terms = self.request.GET.get('term', 0)
        if clm_type == 'RS':
            self.model = RS
            self.serializer_class = RSSerializer
        elif clm_type == 'CBECE':
            self.model = CBECE
            self.serializer_class = CBECESerializer

        qs = self.model.objects.filter(partner=self.request.user.partner_id)

        if terms:
            for term in terms.split():
                qs = qs.filter(
                    Q(student__first_name__contains=term) |
                    Q(student__father_name__contains=term) |
                    Q(student__last_name__contains=term)
                ).distinct()
            return qs


class BLNExportViewSet(LoginRequiredMixin, ListView):
    current_round = CLMRound.objects.filter(current_year=True)
    qs_students = BLN.objects.filter(round__in=current_round)
    qs_fc = BLN_FC.objects.filter(enrollment__round__in=current_round)

    def get_queryset_students(self):
        if not self.request.user.is_staff:
            return self.qs_students.filter(partner=self.request.user.partner)
        return self.qs_students

    def get_queryset_fc(self):
        if not self.request.user.is_staff:
            return self.qs_fc.filter(enrollment__partner=self.request.user.partner)
        return self.qs_fc.order_by('enrollment', 'fc_type')

    def get(self, request, *args, **kwargs):
        return bln_build_xls_extraction(self.get_queryset_students(), self.get_queryset_fc())


class ABLNExportViewSet(LoginRequiredMixin, ListView):
    current_round = CLMRound.objects.filter(current_year=True)
    qs_students = ABLN.objects.filter(round__in=current_round)
    qs_fc = ABLN_FC.objects.filter(enrollment__round__in=current_round)

    def get_queryset_students(self):
        if not self.request.user.is_staff:
            return self.qs_students.filter(partner=self.request.user.partner)
        return self.qs_students

    def get_queryset_fc(self):
        if not self.request.user.is_staff:
            return self.qs_fc.filter(enrollment__partner=self.request.user.partner)
        return self.qs_fc.order_by('enrollment', 'fc_type')

    def get(self, request, *args, **kwargs):
        return abln_build_xls_extraction(self.get_queryset_students(), self.get_queryset_fc())


class CBECEExportViewSet(LoginRequiredMixin, ListView):
    current_round = CLMRound.objects.filter(current_year=True)
    qs_students = CBECE.objects.filter(round__in=current_round)
    qs_fc = CBECE_FC.objects.filter(enrollment__round__in=current_round)

    def get_queryset_students(self):
        if not self.request.user.is_staff:
            return self.qs_students.filter(partner=self.request.user.partner)
        return self.qs_students

    def get_queryset_fc(self):
        if not self.request.user.is_staff:
            return self.qs_fc.filter(enrollment__partner=self.request.user.partner)
        return self.qs_fc.order_by('enrollment', 'fc_type')

    def get(self, request, *args, **kwargs):
        return cbece_build_xls_extraction(self.get_queryset_students(), self.get_queryset_fc())


class RSExportViewSet(LoginRequiredMixin, ListView):
    current_round = CLMRound.objects.filter(current_year=True)
    qs_students = RS.objects.filter(round__in=current_round)
    qs_fc = RS_FC.objects.filter(enrollment__round__in=current_round)

    def get_queryset_students(self):
        if not self.request.user.is_staff:
            return self.qs_students.filter(partner=self.request.user.partner)
        return self.qs_students

    def get_queryset_fc(self):
        if not self.request.user.is_staff:
            return self.qs_fc.filter(enrollment__partner=self.request.user.partner)
        return self.qs_fc.order_by('enrollment', 'fc_type')

    def get(self, request, *args, **kwargs):
        # return rs_build_xls_extraction(self.get_queryset_students())
        return rs_build_xls_extraction(self.get_queryset_students(), self.get_queryset_fc())


def load_districts(request):
    cities = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    cities = []
    if request.GET.get('id_district'):
        id_district = request.GET.get('id_district')
        cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    schools = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})



class ExecABLNUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'clm/execs.html'

    def get_context_data(self, **kwargs):
        instances = ABLN.objects.filter(round_id=8)
        instances.update(round_id=9)

        return {
            'result': instances.count(),
        }

class OutreachAddView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'clm/outreach_create_form.html'
    form_class = OutreachForm
    success_url = '/clm/outreach-list/'
    group_required = [u"CLM_outreach"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/outreach-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/outreach-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='Outreach',
                assessment_slug='outreach_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:outreach_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('Outreach')
        return super(OutreachAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(OutreachAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            instance = Outreach.objects.get(id=self.request.GET.get('enrollment_id'))
            data = OutreachSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(OutreachAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return OutreachForm(self.request.POST, instance=None, request=self.request)
        else:
            return OutreachForm(None, instance=None, request=self.request, initial=self.get_initial())


class OutreachEditView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'clm/outreach_edit_form.html'
    form_class = OutreachForm
    success_url = '/clm/outreach-list/'
    group_required = [u"CLM_outreach"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/outreach-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/outreach-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('Outreach')

        return super(OutreachEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return OutreachForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = OutreachSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            return OutreachForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(OutreachEditView, self).form_valid(form)


class OutreachListView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FilterView,
                       ExportMixin,
                       SingleTableView,
                       RequestConfig):
    table_class = OutreachTable
    model = Outreach
    template_name = 'clm/outreach_list.html'
    table = OutreachTable(Outreach.objects.all(), order_by='id')
    group_required = [u"CLM_outreach"]

    filterset_class = OutreachFilter

    def get_queryset(self):
        force_default_language(self.request)

        return Outreach.objects.filter(partner=self.request.user.partner_id).order_by('-id')


class OutreachExportViewSet(LoginRequiredMixin, ListView):
    current_round = CLMRound.objects.filter(current_year=True)
    qs_students = Outreach.objects.filter(round__in=current_round)

    def get_queryset_students(self):
        if not self.request.user.is_staff:
            return self.qs_students.filter(partner=self.request.user.partner)
        return self.qs_students

    def get(self, request, *args, **kwargs):
        return outreach_build_xls_extraction(self.get_queryset_students())


class BridgingAddView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'clm/bridging_form.html'
    form_class = BridgingForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bridging-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bridging-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='Bridging',
                assessment_slug='bridging_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bridging_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('Bridging')
        return super(BridgingAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(BridgingAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }

        if self.request.GET.get('search_model') and self.request.GET.get('enrollment_id'):
            search_model = self.request.GET.get('search_model')
            if search_model == 'BLN':
                instance = BLN.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BLNSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            elif search_model == 'ABLN':
                instance = ABLN.objects.get(id=self.request.GET.get('enrollment_id'))
                data = ABLNSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            elif search_model == 'CBECE':
                instance = CBECE.objects.get(id=self.request.GET.get('enrollment_id'))
                data = CBECESerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            else:
                instance = Bridging.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
        else:
            if self.request.GET.get('enrollment_id'):
                instance = Bridging.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''

            if self.request.GET.get('child_id'):
                instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
                data = ChildSerializer(instance).data

            if self.request.GET.get('outreach_id'):
                instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''

        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(request=self.request)
        return super(BridgingAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return BridgingForm(self.request.POST, self.request.FILES, instance=None, request=self.request)
        else:
            return BridgingForm(None, instance=None, request=self.request, initial=self.get_initial())


class BridgingEditView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'clm/bridging_form.html'
    form_class = BridgingForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bridging-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bridging-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='Bridging',
                assessment_slug='bridging_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bridging_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('Bridging')
        return super(BridgingEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return BridgingForm(self.request.POST, self.request.FILES, instance=instance, request=self.request)
        else:
            data = BridgingSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:

                    if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                        data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                        data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                    if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                        data['arabic_reading_comprehension'] = p_test["Bridging_ASSESSMENT/arabic_reading_comprehension"]

                    if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                        data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                        data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                    if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                        data['english_reading_comprehension'] = p_test["Bridging_ASSESSMENT/english_reading_comprehension"]


                    if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                        data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                        data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                    if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                        data['french_reading_comprehension'] = p_test["Bridging_ASSESSMENT/french_reading_comprehension"]

                    if "Bridging_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Bridging_ASSESSMENT/math"]

            return BridgingForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingEditView, self).form_valid(form)


class BridgingListView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FilterView,
                       ExportMixin,
                       SingleTableView,
                       RequestConfig):
    table_class = BridgingTable
    model = Bridging
    template_name = 'clm/bridging_list.html'
    table = BridgingTable(Bridging.objects.all(), order_by='student__full_name')
    group_required = [u"CLM_Bridging"]

    filterset_class = BridgingFilter

    def get_queryset(self):
        qs = Bridging.objects.filter(round__current_year=True, deleted=False)
        if not has_group(self.request.user, 'CLM_BRIDGING_ALL') and not self.request.user.is_staff and self.request.user.partner:
            qs = qs.filter(partner_id=self.request.user.partner_id)
            if self.request.user.school:
                qs = qs.filter(school_id=self.request.user.school_id)
        elif not has_group(self.request.user, 'CLM_BRIDGING_ALL') and not self.request.user.is_staff and not self.request.user.partner:
            qs = qs.none()
        return qs


@login_required(login_url='/users/login')
def bridging_export_data(request, **kwargs):
    try:
        cursor = connection.cursor()
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        round_id = request.GET.get('round', None)

        vw_bridging_data = 'SELECT * FROM vw_bridging_data WHERE id > 0'
        query_params = []

        if round_id:
            vw_bridging_data += " AND round_id = %s"
            query_params.append(round_id)

        clm_bridging_all = request.user.groups.filter(name='CLM_BRIDGING_ALL').exists()
        is_staff = request.user.is_staff

        if not clm_bridging_all and not is_staff and request.user.partner:
            school_id = 0
            partner_id = request.user.partner_id

            vw_bridging_data += " AND partner_id = %s"
            query_params.append(partner_id)

            if request.user.school:
                school_id = request.user.school.id
            if school_id > 0:
                vw_bridging_data += " AND school_id = %s"
                query_params.append(school_id)

        elif not clm_bridging_all and not is_staff and not request.user.partner:
            vw_bridging_data += " AND id = 0 "

        vw_bridging_data += " ORDER BY student_first_name, student_fathername, last_name "

        cursor.execute(vw_bridging_data, query_params)
        bridging_data = cursor.fetchall()

        logging.debug("Executing query: %s", vw_bridging_data)
        logging.debug("Query params: %s", str(query_params))

        headers = [col[0] for col in cursor.description]

        # Create CSV
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)

        # Add BOM for Arabic text
        csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
        csv_writer.writerow(headers)  # Write headers

        for row in bridging_data:
            encoded_row = []
            for cell in row:
                if isinstance(cell, (str, bytes)):  # Handle string and bytes
                    encoded_row.append(cell.decode('utf-8') if isinstance(cell, bytes) else cell)
                elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                    encoded_row.append(cell.strftime('%Y-%m-%d'))
                else:  # Convert other data types to string
                    encoded_row.append(str(cell))
            csv_writer.writerow(encoded_row)

        unique_id = str(uuid.uuid4())
        file_name = "bridging_{}.csv".format(unique_id)
        file_path = os.path.join('export', file_name)

        # Save file
        default_storage.save(file_path, ContentFile(csv_output.getvalue().encode('utf-8')))

        # Store export history
        ExportHistory.objects.create(
            export_type='Bridging List',
            created_by=user,
            partner_name=partner_name
        )

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/users/login')
def bridging_school_export(request, **kwargs):
    try:
        cursor = connection.cursor()
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        school_id = int(kwargs.get('school_id'))

        clm_bridging_all = request.user.groups.filter(name='CLM_BRIDGING_ALL').exists()
        is_staff = request.user.is_staff

        vw_bridging_data = 'SELECT * FROM vw_bridging_data WHERE id > 0'
        query_params = []

        if not clm_bridging_all and not is_staff and request.user.partner:
            partner_id = request.user.partner_id
            vw_bridging_data += " AND partner_id = %s"
            query_params.append(partner_id)

        elif not clm_bridging_all and not is_staff and not request.user.partner:
            vw_bridging_data += " AND id = 0"

        if school_id > 0:
            vw_bridging_data += " AND school_id = %s"
            query_params.append(school_id)

        vw_bridging_data += " ORDER BY student_first_name, student_fathername, last_name"

        cursor.execute(vw_bridging_data, query_params)
        bridging_data = cursor.fetchall()

        logging.debug("Executing query: %s", vw_bridging_data)
        logging.debug("Query params: %s", str(query_params))

        headers = [col[0] for col in cursor.description]

        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)

        csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
        csv_writer.writerow(headers)

        for row in bridging_data:
            encoded_row = []
            for cell in row:
                if isinstance(cell, (str, bytes)):  # Handle string and bytes
                    encoded_row.append(cell.decode('utf-8') if isinstance(cell, bytes) else cell)
                elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                    encoded_row.append(cell.strftime('%Y-%m-%d'))
                else:  # Convert other data types to string
                    encoded_row.append(str(cell))
                # Local 2.7
                # if isinstance(cell, str) or isinstance(cell, unicode):  # Handle Unicode strings
                #     encoded_row.append(force_text(cell).encode('utf-8'))
                # elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                #     encoded_row.append(cell.strftime('%Y-%m-%d'))
                # else:  # Convert other data types to string
                #     encoded_row.append(str(cell).encode('utf-8'))
            csv_writer.writerow(encoded_row)

        unique_id = str(uuid.uuid4())
        file_name = "bridging_school_{}.csv".format(unique_id)
        file_path = os.path.join('export', file_name)


        default_storage.save(file_path, ContentFile(csv_output.getvalue().encode('utf-8')))

        # Store export history
        ExportHistory.objects.create(
            export_type='School List - Bridging',
            created_by=user,
            partner_name=partner_name
        )

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)


class BridgingPage(LoginRequiredMixin,
                   TemplateView):
        template_name = 'clm/bridging.html'


class BridgingAttendanceReport(LoginRequiredMixin,
                   TemplateView):

    template_name = 'clm/bridging_attendance_report.html'
    rounds = CLMRound.objects.filter(current_year=True).all()

    def get_context_data(self, **kwargs):
        context = super(BridgingAttendanceReport, self).get_context_data(**kwargs)
        context['rounds'] = CLMRound.objects.filter(current_year=True).all()
        return context

