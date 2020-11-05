# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func
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
from .filters import BLNFilter, ABLNFilter, RSFilter, CBECEFilter
from .tables import BootstrapTable, BLNTable, ABLNTable, RSTable, CBECETable
from .models import BLN, ABLN, RS, CBECE, SelfPerceptionGrades, Disability, Assessment
from .forms import (
    BLNForm,
    ABLNForm,
    RSForm,
    CBECEForm,
    BLNReferralForm,
    BLNFollowupForm,
    ABLNReferralForm,
    ABLNFollowupForm,
    BLNAssessmentForm,
    ABLNAssessmentForm,
    CBECEAssessmentForm,
    CBECEFollowupForm,
    CBECEReferralForm,
    CBECEMonitoringQuestionerForm,
    BLNMonitoringQuestionerForm,
    ABLNMonitoringQuestionerForm
)
from .serializers import BLNSerializer, ABLNSerializer, RSSerializer, CBECESerializer, SelfPerceptionGradesSerializer
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
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(BLNAddView, self).form_valid(form)


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

                    if "BLN_ASSESSMENT/modality_artistic" in p_test:
                        data['modality_artistic'] = p_test["BLN_ASSESSMENT/modality_artistic"]

                    if "BLN_ASSESSMENT/artistic" in p_test:
                        data['artistic'] = p_test["BLN_ASSESSMENT/artistic"]

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
    table = BootstrapTable(BLN.objects.all(), order_by='id')
    group_required = [u"CLM_BLN"]

    filterset_class = BLNFilter

    def get_queryset(self):
        force_default_language(self.request)
        return BLN.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by(
            '-id')


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
    table = BootstrapTable(ABLN.objects.all(), order_by='id')
    group_required = [u"CLM_ABLN"]

    filterset_class = ABLNFilter

    def get_queryset(self):
        force_default_language(self.request)
        return ABLN.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by(
            '-id')


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

                    if "ABLN_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_psychomotor'] = p_test["ABLN_ASSESSMENT/attended_psychomotor"]

                    if "ABLN_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_psychomotor'] = p_test["ABLN_ASSESSMENT/modality_psychomotor"]

                    if "ABLN_ASSESSMENT/psychomotor" in p_test:
                        data['psychomotor'] = p_test["ABLN_ASSESSMENT/psychomotor"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = ABLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(ABLNPostAssessmentView, self).form_valid(form)

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

                    if "BLN_ASSESSMENT/attended_psychomotor" in p_test:
                        data['attended_psychomotor'] = p_test["BLN_ASSESSMENT/attended_psychomotor"]

                    if "BLN_ASSESSMENT/modality_psychomotor" in p_test:
                        data['modality_psychomotor'] = p_test["BLN_ASSESSMENT/modality_psychomotor"]

                    if "BLN_ASSESSMENT/psychomotor" in p_test:
                        data['psychomotor'] = p_test["BLN_ASSESSMENT/psychomotor"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(BLNPostAssessmentView, self).form_valid(form)


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
    template_name = 'clm/create_form.html'
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
        kwargs['is_allowed_create'] = True
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

            data['pre_test_arabic'] = 0
            data['pre_test_language'] = 0
            data['pre_test_math'] = 0
            data['pre_test_science'] = 0
            data['post_test_arabic'] = 0
            data['post_test_language'] = 0
            data['post_test_math'] = 0
            data['post_test_science'] = 0
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', '')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(RSAddView, self).form_valid(form)


class RSEditView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):
    template_name = 'clm/edit_form.html'
    form_class = RSForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/rs-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/rs-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = True
        return super(RSEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = RS.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return RSForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = RSSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
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
    table = BootstrapTable(RS.objects.all(), order_by='id')
    group_required = [u"CLM_RS"]

    filterset_class = RSFilter

    def get_queryset(self):
        force_default_language(self.request)
        return RS.objects.filter(partner=self.request.user.partner_id).order_by('-id')


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
    table = BootstrapTable(CBECE.objects.all(), order_by='id')
    group_required = [u"CLM_CBECE"]

    filterset_class = CBECEFilter

    def get_queryset(self):
        force_default_language(self.request)
        return CBECE.objects.filter(partner=self.request.user.partner_id,
                                    round__start_date_cbece__year=Person.CURRENT_YEAR).order_by('-id')
        # return CBECE.objects.filter(partner=self.request.user.partner_id, created__year=Person.CURRENT_YEAR).order_by('-id')


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
    queryset = BLN.objects.all()
    serializer_class = BLNSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d'))
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
    queryset = ABLN.objects.all()
    serializer_class = ABLNSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d'))
        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class RSViewSet(mixins.RetrieveModelMixin,
                mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    model = RS
    queryset = RS.objects.all()
    serializer_class = RSSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = self.queryset
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
    queryset = CBECE.objects.all()
    serializer_class = CBECESerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = self.queryset
        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


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
    model = BLN
    queryset = BLN.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):
        headers = {
            'id': 'enrollment_id',
            'new_registry': 'First time registered?',
            'partner__name': 'Partner',
            'source_of_identification': 'Source of Identification',
            'first_attendance_date': 'first attendance date',
            'round__name': 'CLM Round',
            'governorate__name_en': 'Governorate',
            'district__name_en': 'District',
            'cadaster__name_en': 'Cadaster',
            'location': 'Location',
            'student__address': 'Student Address',
            'language': 'The language supported in the program',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Student Nationality',
            'other_nationality': 'Student Nationality Specify',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__number': 'unique number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'student_number_children': 'Child number of children',
            'disability__name_en': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'education_status': 'Education status',
            'miss_school_date': 'Miss school date',
            'comments': 'Comments',

            'phone_number': 'Phone number',
            'phone_number_confirm': 'Phone number confirm',
            'phone_owner': 'phone owner',
            'second_phone_number': 'Second Phone number',
            'second_phone_number_confirm': 'Second Phone number confirm',
            'second_phone_owner': 'Second phone owner',

            'id_type': 'ID Type',
            'case_number': 'UNHCR case number',
            'case_number_confirm': 'UNHCR case number confirm',
            'individual_case_number': 'Child individual ID',
            'individual_case_number_confirm': 'Child individual ID confirm',
            'parent_individual_case_number': 'Parent individual ID',
            'parent_individual_case_number_confirm': 'Parent individual ID confirm',
            'recorded_number': 'UNHCR recorded barcode',
            'recorded_number_confirm': 'UNHCR recorded barcode confirm',
            'national_number': 'Child Lebanese ID number',
            'national_number_confirm': 'Child Lebanese ID number confirm',
            'syrian_national_number': 'Child Syrian ID number',
            'syrian_national_number_confirm': 'Child Syrian ID number confirm',
            'sop_national_number': 'Child Palestinian ID number',
            'sop_national_number_confirm': 'Child Palestinian ID number confirm',
            'parent_national_number': 'Parent Lebanese ID number',
            'parent_national_number_confirm': 'Parent Lebanese ID number confirm',
            'parent_syrian_national_number': 'Parent Syrian ID number',
            'parent_syrian_national_number_confirm': 'Parent Syrian ID number confirm',
            'parent_sop_national_number': 'Parent Palestinian ID number',
            'parent_sop_national_number_confirm': 'Parent Palestinian ID number confirm',
            'parent_other_number': 'ID number of the Caretaker',
            'parent_other_number_confirm': 'ID number of the Caretaker confirm',
            'other_number': 'ID number of the child',
            'other_number_confirm': 'ID number of the child confirm',

            'main_caregiver': 'Main Caregiver',
            'main_caregiver_nationality__name': 'main caregiver nationality',
            'other_caregiver_relationship': 'other caregiver relationship',
            'caretaker_first_name': 'Caretaker first name',
            'caretaker_middle_name': 'Caretaker middle name',
            'caretaker_last_name': 'Caretaker last name',
            'caretaker_mother_name': 'Caretaker mother name',

            'hh_educational_level__name': 'What is the educational level of the mother?',
            'father_educational_level__name': 'What is the educational level of the father?',
            'have_labour_single_selection': 'Does the child participate in work?',
            'labours_single_selection': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',
            'labour_weekly_income': 'Child weekly income',
            'basic_stationery': 'Did the child receive basic stationery?',
            'pss_kit': 'Did the child benefit from the PSS kit?',
            'remote_learning': 'Was the child involved in remote learning?',
            'remote_learning_reasons_not_engaged': 'what other reasons for this child not being engaged?',
            'reasons_not_engaged_other': 'reasons not engaged other',
            'reliable_internet': 'Does the family have reliable internet service in their area during remote learning?',
            'gender_participate': 'Did both girls and boys in the same family participate in the class and have access to the phone/device?',
            'gender_participate_explain': 'Explain',
            'remote_learning_engagement': 'Frequency of Child Engagement in remote learning?',
            'meet_learning_outcomes': 'How well did the child meet the learning outcomes?',
            'parent_learning_support_rate': 'How do you rate the parents learning support provided to the child through this Remote learning phase?',
            'covid_message': 'Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_message_how_often': 'How often?',
            'covid_parents_message': 'Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_parents_message_how_often': 'How often?',
            'follow_up_done': 'Was any follow-up done to ensure messages were well received, understood and adopted?',
            'follow_up_done_with_who': 'With who child and/or caregiver?',

            'unsuccessful_pretest_reason': 'Reason why not doing the Pre-test',
            'unsuccessful_posttest_reason': 'Reason why not doing the Post-test',

            'pre_test_attended_arabic': 'pre test attended arabic',
            'pre_test_modality_arabic': 'pre test modality arabic',
            'pre_test_arabic': 'pre test arabic',
            'pre_test_attended_english': 'pre test attended english',
            'pre_test_modality_english': 'pre test modality english',
            'pre_test_english': 'pre test english',
            'pre_test_attended_psychomotor': 'pre test attended psychomotor',
            'pre_test_modality_psychomotor': 'pre test modality psychomotor',
            'pre_test_psychomotor': 'pre test psychomotor',
            'pre_test_attended_math': 'pre test attended math',
            'pre_test_modality_math': 'pre test modality math',
            'pre_test_math': 'pre test math',
            'pre_test_attended_social': 'pre test attended social',
            'pre_test_modality_social': 'pre test modality social',
            'pre_test_social_emotional': 'pre test social emotional',
            'pre_test_score': 'pre test score',
            'post_test_attended_arabic': 'post test attended arabic',
            'post_test_modality_arabic': 'post test modality arabic',
            'post_test_arabic': 'post test arabic',
            'post_test_attended_english': 'post test attended english',
            'post_test_modality_english': 'post test modality english',
            'post_test_english': 'post test english',
            'post_test_attended_psychomotor': 'post test attended psychomotor',
            'post_test_modality_psychomotor': 'post test modality psychomotor',
            'post_test_psychomotor': 'post test psychomotor',
            'post_test_attended_math': 'post test attended math',
            'post_test_modality_math': 'post test modality math',
            'post_test_math': 'post test math',
            'post_test_attended_social': 'post test attended social',
            'post_test_modality_social': 'post test modality social',
            'post_test_social_emotional': 'post test social emotional',
            'post_test_score': 'post test score',

            'participation': 'Level of participation / Absence',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'student_outreached': 'Student outreached?',
            'have_barcode': 'Have barcode with him?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',

            'referral_programme_type_1': 'Referral programme type 1',
            'referral_partner_1': 'Referral partner 1',
            'referral_date_1': 'Referral date 1',
            'confirmation_date_1': 'Referral confirmation date 1',

            'referral_programme_type_2': 'Referral programme type 2',
            'referral_partner_2': 'Referral partner 2',
            'referral_date_2': 'Referral date 2',
            'confirmation_date_2': 'Referral confirmation date 2',

            'referral_programme_type_3': 'Referral programme type 3',
            'referral_partner_3': 'Referral partner 3',
            'referral_date_3': 'Referral date 3',
            'confirmation_date_3': 'Referral confirmation date 3',

            'followup_call_date_1': 'Follow-up call 1 date',
            'followup_call_reason_1': 'Follow-up call 1 reason',
            'followup_call_result_1': 'Follow-up call 1 result',

            'followup_call_date_2': 'Follow-up call 2 date',
            'followup_call_reason_2': 'Follow-up call 2 reason',
            'followup_call_result_2': 'Follow-up call 2 result',

            'followup_visit_date_1': 'Follow-up visit 1 date',
            'followup_visit_reason_1': 'Follow-up visit 1 reason',
            'followup_visit_result_1': 'Follow-up visit 1 result',
        }

        field_list = (
            'id'
            'new_registry',
            'partner__name',
            'source_of_identification',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'student__address',
            'language',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code'
            'student__id_number'
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'internal_number',
            'education_status',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',

            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number', 'ID number of the Caretaker',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',

            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',

            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',

            'pre_test_attended_arabic',
            'pre_test_modality_arabic',
            'pre_test_arabic',

            'pre_test_attended_english',
            'pre_test_modality_english',
            'pre_test_english',

            'pre_test_attended_psychomotor',
            'pre_test_modality_psychomotor',
            'pre_test_psychomotor',

            'pre_test_attended_math',
            'pre_test_modality_math',
            'pre_test_math',

            'pre_test_attended_social',
            'pre_test_modality_social',
            'pre_test_social_emotional',

            'pre_test_score',

            'post_test_attended_arabic',
            'post_test_modality_arabic',
            'post_test_arabic',

            'post_test_attended_english',
            'post_test_modality_english',
            'post_test_english',

            'post_test_attended_psychomotor',
            'post_test_modality_psychomotor',
            'post_test_psychomotor',

            'post_test_attended_math',
            'post_test_modality_math',
            'post_test_math',

            'post_test_attended_social',
            'post_test_modality_social',
            'post_test_social_emotional',

            'post_test_score',

            'participation',
            'barriers',
            'learning_result',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',

            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',

            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',

            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',

            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1'
        )

        qs = self.get_queryset().extra(select={
            # 'participation': "CONCAT(participation, '_absence')",

            'pre_test_attended_arabic': "pre_test->>'BLN_ASSESSMENT/attended_arabic'",
            'pre_test_modality_arabic': "pre_test->>'BLN_ASSESSMENT/modality_arabic'",
            'pre_test_arabic': "pre_test->>'BLN_ASSESSMENT/arabic'",

            'pre_test_attended_english': "pre_test->>'BLN_ASSESSMENT/attended_english'",
            'pre_test_modality_english': "pre_test->>'BLN_ASSESSMENT/modality_english'",
            'pre_test_english': "pre_test->>'BLN_ASSESSMENT/english'",

            'pre_test_attended_psychomotor': "pre_test->>'BLN_ASSESSMENT/attended_psychomotor'",
            'pre_test_modality_psychomotor': "pre_test->>'BLN_ASSESSMENT/modality_psychomotor'",
            'pre_test_psychomotor': "pre_test->>'BLN_ASSESSMENT/psychomotor'",

            'pre_test_attended_math': "pre_test->>'BLN_ASSESSMENT/attended_math'",
            'pre_test_modality_math': "pre_test->>'BLN_ASSESSMENT/modality_math'",
            'pre_test_math': "pre_test->>'BLN_ASSESSMENT/math'",

            'pre_test_attended_social': "pre_test->>'BLN_ASSESSMENT/attended_social'",
            'pre_test_modality_social': "pre_test->>'BLN_ASSESSMENT/modality_social'",
            'pre_test_social_emotional': "pre_test->>'BLN_ASSESSMENT/social_emotional'",

            'post_test_attended_arabic': "post_test->>'BLN_ASSESSMENT/attended_arabic'",
            'post_test_modality_arabic': "post_test->>'BLN_ASSESSMENT/modality_arabic'",
            'post_test_arabic': "post_test->>'BLN_ASSESSMENT/arabic'",

            'post_test_attended_english': "post_test->>'BLN_ASSESSMENT/attended_english'",
            'post_test_modality_english': "post_test->>'BLN_ASSESSMENT/modality_english'",
            'post_test_english': "post_test->>'BLN_ASSESSMENT/english'",

            'post_test_attended_psychomotor': "post_test->>'BLN_ASSESSMENT/attended_psychomotor'",
            'post_test_modality_psychomotor': "post_test->>'BLN_ASSESSMENT/modality_psychomotor'",
            'post_test_psychomotor': "post_test->>'BLN_ASSESSMENT/psychomotor'",

            'post_test_attended_math': "post_test->>'BLN_ASSESSMENT/attended_math'",
            'post_test_modality_math': "post_test->>'BLN_ASSESSMENT/modality_math'",
            'post_test_math': "post_test->>'BLN_ASSESSMENT/math'",

            'post_test_attended_social': "post_test->>'BLN_ASSESSMENT/attended_social'",
            'post_test_modality_social': "post_test->>'BLN_ASSESSMENT/modality_social'",
            'post_test_social_emotional': "post_test->>'BLN_ASSESSMENT/social_emotional'",

        }).values(
            'id',
            'new_registry',
            'partner__name',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'student__address',
            'language',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'internal_number',
            'education_status',
            'miss_school_date',
            'comments',
            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'pre_test_attended_arabic',
            'pre_test_modality_arabic',
            'pre_test_arabic',

            'pre_test_attended_english',
            'pre_test_modality_english',
            'pre_test_english',

            'pre_test_attended_psychomotor',
            'pre_test_modality_psychomotor',
            'pre_test_psychomotor',

            'pre_test_attended_math',
            'pre_test_modality_math',
            'pre_test_math',

            'pre_test_attended_social',
            'pre_test_modality_social',
            'pre_test_social_emotional',

            'pre_test_score',

            'post_test_attended_arabic',
            'post_test_modality_arabic',
            'post_test_arabic',

            'post_test_attended_english',
            'post_test_modality_english',
            'post_test_english',

            'post_test_attended_psychomotor',
            'post_test_modality_psychomotor',
            'post_test_psychomotor',

            'post_test_attended_math',
            'post_test_modality_math',
            'post_test_math',

            'post_test_attended_social',
            'post_test_modality_social',
            'post_test_social_emotional',

            'post_test_score',

            'participation',
            'barriers',
            'learning_result',
            'cycle_completed',
            'enrolled_at_school',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',

            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'source_of_identification',
            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',
        )
        # print(qs.query)
        return render_to_csv_response(qs, field_header_map=headers, field_order=field_list)


class ABLNExportViewSet(LoginRequiredMixin, ListView):
    model = ABLN
    queryset = ABLN.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):
        headers = {
            'id': 'enropllment_id',
            'new_registry': 'First time registered?',
            'partner__name': 'Partner',
            'source_of_identification': 'Source of Identification',
            'first_attendance_date': 'first attendance date',
            'round__name': 'CLM Round',
            'governorate__name_en': 'Governorate',
            'district__name_en': 'District',
            'cadaster__name_en': 'Cadaster',
            'location': 'Location',
            'student__address': 'Student Address',
            'language': 'The language supported in the program',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Student Nationality',
            'other_nationality': 'Student Nationality Specify',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__number': 'unique number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'student_number_children': 'Child number of children',
            'disability__name_en': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'education_status': 'Education status',
            'miss_school_date': 'Miss school date',
            'comments': 'Comments',

            'phone_number': 'Phone number',
            'phone_number_confirm': 'Phone number confirm',
            'phone_owner': 'phone owner',
            'second_phone_number': 'Second Phone number',
            'second_phone_number_confirm': 'Second Phone number confirm',
            'second_phone_owner': 'Second phone owner',

            'id_type': 'ID Type',
            'case_number': 'UNHCR case number',
            'case_number_confirm': 'UNHCR case number confirm',
            'individual_case_number': 'Child individual ID',
            'individual_case_number_confirm': 'Child individual ID confirm',
            'parent_individual_case_number': 'Parent individual ID',
            'parent_individual_case_number_confirm': 'Parent individual ID confirm',
            'recorded_number': 'UNHCR recorded barcode',
            'recorded_number_confirm': 'UNHCR recorded barcode confirm',
            'national_number': 'Child Lebanese ID number',
            'national_number_confirm': 'Child Lebanese ID number confirm',
            'syrian_national_number': 'Child Syrian ID number',
            'syrian_national_number_confirm': 'Child Syrian ID number confirm',
            'sop_national_number': 'Child Palestinian ID number',
            'sop_national_number_confirm': 'Child Palestinian ID number confirm',
            'parent_national_number': 'Parent Lebanese ID number',
            'parent_national_number_confirm': 'Parent Lebanese ID number confirm',
            'parent_syrian_national_number': 'Parent Syrian ID number',
            'parent_syrian_national_number_confirm': 'Parent Syrian ID number confirm',
            'parent_sop_national_number': 'Parent Palestinian ID number',
            'parent_sop_national_number_confirm': 'Parent Palestinian ID number confirm',
            'parent_other_number': 'ID number of the Caretaker',
            'parent_other_number_confirm': 'ID number of the Caretaker confirm',
            'other_number': 'ID number of the child',
            'other_number_confirm': 'ID number of the child confirm',
            'main_caregiver': 'Main Caregiver',
            'main_caregiver_nationality__name': 'main caregiver nationality',
            'other_caregiver_relationship': 'other caregiver relationship',
            'caretaker_first_name': 'Caretaker first name',
            'caretaker_middle_name': 'Caretaker middle name',
            'caretaker_last_name': 'Caretaker last name',
            'caretaker_mother_name': 'Caretaker mother name',

            'hh_educational_level__name': 'What is the educational level of the mother?',
            'father_educational_level__name': 'What is the educational level of the father?',
            'have_labour_single_selection': 'Does the child participate in work?',
            'labours_single_selection': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',
            'labour_weekly_income': 'Child weekly income',
            'basic_stationery': 'Did the child receive basic stationery?',
            'pss_kit': 'Did the child benefit from the PSS kit?',
            'remote_learning': 'Was the child involved in remote learning?',
            'remote_learning_reasons_not_engaged': 'what other reasons for this child not being engaged?',
            'reasons_not_engaged_other': 'reasons not engaged other',
            'reliable_internet': 'Does the family have reliable internet service in their area during remote learning?',
            'gender_participate': 'Did both girls and boys in the same family participate in the class and have access to the phone/device?',
            'gender_participate_explain': 'Explain',
            'remote_learning_engagement': 'Frequency of Child Engagement in remote learning?',
            'meet_learning_outcomes': 'How well did the child meet the learning outcomes?',
            'parent_learning_support_rate': 'How do you rate the parents learning support provided to the child through this Remote learning phase?',
            'covid_message': 'Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_message_how_often': 'How often?',
            'covid_parents_message': 'Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_parents_message_how_often': 'How often?',
            'follow_up_done': 'Was any follow-up done to ensure messages were well received, understood and adopted?',
            'follow_up_done_with_who': 'With who child and/or caregiver?',

            'unsuccessful_pretest_reason': 'Reason why not doing the Pre-test',
            'unsuccessful_posttest_reason': 'Reason why not doing the Post-test',

            'pre_test_attended_arabic': 'pre test attended arabic',
            'pre_test_modality_arabic': 'pre test modality arabic',
            'pre_test_arabic': 'pre test arabic',
            'pre_test_attended_psychomotor': 'pre test attended psychomotor',
            'pre_test_modality_psychomotor': 'pre test modality psychomotor',
            'pre_test_psychomotor': 'pre test psychomotor',
            'pre_test_attended_math': 'pre test attended math',
            'pre_test_modality_math': 'pre test modality math',
            'pre_test_math': 'pre test math',
            'pre_test_attended_social': 'pre test attended social',
            'pre_test_modality_social': 'pre test modality social',
            'pre_test_social_emotional': 'pre test social emotional',
            'pre_test_score': 'pre test score',
            'post_test_attended_arabic': 'post test attended arabic',
            'post_test_modality_arabic': 'post test modality arabic',
            'post_test_arabic': 'post test arabic',
            'post_test_attended_psychomotor': 'post test attended psychomotor',
            'post_test_modality_psychomotor': 'post test modality psychomotor',
            'post_test_psychomotor': 'post test psychomotor',
            'post_test_attended_math': 'post test attended math',
            'post_test_modality_math': 'post test modality math',
            'post_test_math': 'post test math',
            'post_test_attended_social': 'post test attended social',
            'post_test_modality_social': 'post test modality social',
            'post_test_social_emotional': 'post test social emotional',
            'post_test_score': 'post test score',
            'participation': 'Level of participation / Absence',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'student_outreached': 'Student outreached?',
            'have_barcode': 'Have barcode with him?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',

            'referral_programme_type_1': 'Referral programme type 1',
            'referral_partner_1': 'Referral partner 1',
            'referral_date_1': 'Referral date 1',
            'confirmation_date_1': 'Referral confirmation date 1',

            'referral_programme_type_2': 'Referral programme type 2',
            'referral_partner_2': 'Referral partner 2',
            'referral_date_2': 'Referral date 2',
            'confirmation_date_2': 'Referral confirmation date 2',

            'referral_programme_type_3': 'Referral programme type 3',
            'referral_partner_3': 'Referral partner 3',
            'referral_date_3': 'Referral date 3',
            'confirmation_date_3': 'Referral confirmation date 3',

            'followup_call_date_1': 'Follow-up call 1 date',
            'followup_call_reason_1': 'Follow-up call 1 reason',
            'followup_call_result_1': 'Follow-up call 1 result',

            'followup_call_date_2': 'Follow-up call 2 date',
            'followup_call_reason_2': 'Follow-up call 2 reason',
            'followup_call_result_2': 'Follow-up call 2 result',

            'followup_visit_date_1': 'Follow-up visit 1 date',
            'followup_visit_reason_1': 'Follow-up visit 1 reason',
            'followup_visit_result_1': 'Follow-up visit 1 result',
        }

        field_list = (
            'id',
            'new_registry',
            'partner__name',
            'source_of_identification',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'language',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'internal_number',
            'education_status',
            'miss_school_date',
            'comments',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',

            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',

            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',

            'pre_test_arabic',
            'post_test_arabic',
            'pre_test_math',
            'post_test_math',
            'pre_test_social_emotional',
            'post_test_social_emotional',
            'pre_test_psychomotor',
            'post_test_psychomotor',
            'pre_test_artistic',
            'post_test_artistic',
            'pre_test_score',
            'post_test_score',

            'participation',
            'barriers',
            'learning_result',
            'cycle_completed',
            'enrolled_at_school',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',

            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',

            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',

            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',

            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',

            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )

        qs = self.get_queryset().extra(select={
            # 'participation': "CONCAT(participation, '_absence')",

            'pre_test_attended_arabic': "pre_test->>'ABLN_ASSESSMENT/attended_arabic'",
            'pre_test_modality_arabic': "pre_test->>'ABLN_ASSESSMENT/modality_arabic'",
            'pre_test_arabic': "pre_test->>'ABLN_ASSESSMENT/arabic'",

            'pre_test_attended_psychomotor': "pre_test->>'ABLN_ASSESSMENT/attended_psychomotor'",
            'pre_test_modality_psychomotor': "pre_test->>'ABLN_ASSESSMENT/modality_psychomotor'",
            'pre_test_psychomotor': "pre_test->>'ABLN_ASSESSMENT/psychomotor'",

            'pre_test_attended_math': "pre_test->>'ABLN_ASSESSMENT/attended_math'",
            'pre_test_modality_math': "pre_test->>'ABLN_ASSESSMENT/modality_math'",
            'pre_test_math': "pre_test->>'ABLN_ASSESSMENT/math'",

            'pre_test_attended_social': "pre_test->>'ABLN_ASSESSMENT/attended_social'",
            'pre_test_modality_social': "pre_test->>'ABLN_ASSESSMENT/modality_social'",
            'pre_test_social_emotional': "pre_test->>'ABLN_ASSESSMENT/social_emotional'",

            'post_test_attended_arabic': "post_test->>'ABLN_ASSESSMENT/attended_arabic'",
            'post_test_modality_arabic': "post_test->>'ABLN_ASSESSMENT/modality_arabic'",
            'post_test_arabic': "post_test->>'ABLN_ASSESSMENT/arabic'",

            'post_test_attended_psychomotor': "post_test->>'ABLN_ASSESSMENT/attended_psychomotor'",
            'post_test_modality_psychomotor': "post_test->>'ABLN_ASSESSMENT/modality_psychomotor'",
            'post_test_psychomotor': "post_test->>'ABLN_ASSESSMENT/psychomotor'",

            'post_test_attended_math': "post_test->>'ABLN_ASSESSMENT/attended_math'",
            'post_test_modality_math': "post_test->>'ABLN_ASSESSMENT/modality_math'",
            'post_test_math': "post_test->>'ABLN_ASSESSMENT/math'",

            'post_test_attended_social': "post_test->>'ABLN_ASSESSMENT/attended_social'",
            'post_test_modality_social': "post_test->>'ABLN_ASSESSMENT/modality_social'",
            'post_test_social_emotional': "post_test->>'ABLN_ASSESSMENT/social_emotional'",
        }).values(
            'id',
            'new_registry',
            'partner__name',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'student__address',
            'language',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'education_status',
            'miss_school_date',
            'internal_number',
            'education_status',
            'miss_school_date',
            'comments',
            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',

            'pre_test_attended_arabic',
            'pre_test_modality_arabic',
            'pre_test_arabic',

            'pre_test_attended_psychomotor',
            'pre_test_modality_psychomotor',
            'pre_test_psychomotor',

            'pre_test_attended_math',
            'pre_test_modality_math',
            'pre_test_math',

            'pre_test_attended_social',
            'pre_test_modality_social',
            'pre_test_social_emotional',

            'pre_test_score',

            'post_test_attended_arabic',
            'post_test_modality_arabic',
            'post_test_arabic',

            'post_test_attended_psychomotor',
            'post_test_modality_psychomotor',
            'post_test_psychomotor',

            'post_test_attended_math',
            'post_test_modality_math',
            'post_test_math',

            'post_test_attended_social',
            'post_test_modality_social',
            'post_test_social_emotional',

            'post_test_score',
            'participation',
            'barriers',
            'learning_result',
            'cycle_completed',
            'enrolled_at_school',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'source_of_identification',
            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1',
        )
        # print(qs.query)
        return render_to_csv_response(qs, field_header_map=headers, field_order=field_list)


class RSExportViewSet(LoginRequiredMixin, ListView):
    model = RS
    queryset = RS.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):
        headers = {
            'new_registry': 'First time registered?',
            'partner__name': 'Partner',
            'round__name': 'CLM Round',
            'type': 'Program type',
            'site': 'Program site',
            'school__name': 'Attending in school',
            'governorate__name_en': 'Governorate',
            'district__name_en': 'District',
            'location': 'Location',
            'language': 'The language supported in the program',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Student Nationality',
            # 'other_nationality': 'Student Nationality Specify',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__number': 'unique number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'disability__name_en': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'comments': 'Comments',
            'hh_educational_level__name': 'What is the educational level of a person who is valuable to the child?',
            'have_labour': 'Does the child participate in work?',
            'labours': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',
            'registered_in_school__name': 'Registered in school',
            'shift': 'Shift',
            'grade__name': 'Class',
            'referral': 'Reason of referral',

            'pre_reading_score': 'Arabic reading - Pre-test',
            'post_reading_score': 'Arabic reading - Post-test',

            'pre_test_arabic': 'Pre-test Arabic',
            'pre_test_language': 'Pre-test language',
            'pre_test_math': 'Pre-test Math',
            'pre_test_science': 'Pre-test Science',

            'post_test_arabic': 'Post-test Arabic',
            'post_test_language': 'Post-test language',
            'post_test_math': 'Post-test Math',
            'post_test_science': 'Post-test Science',

            'pre_strategy_q1': 'تفحص الطلاب الصور - Strategy Evaluation Result - Pre',
            'pre_strategy_q2': 'قام الطلاب بربط الصور بما عرفوه مسبقا - Strategy Evaluation Result - Pre',
            'pre_strategy_q3': 'تفحص الطلاب الكلمات التي يعرفونها من السابق في التعليمات - Strategy Evaluation Result - Pre',
            'pre_strategy_q4': ' استعان الطلاب بالصور لفهم التعليمات - Strategy Evaluation Result - Pre',
            'pre_test_score': 'Strategy Evaluation Result - Pre',

            'post_strategy_q1': 'تفحص الطلاب الصور - Strategy Evaluation Result - Post',
            'post_strategy_q2': 'قام الطلاب بربط الصور بما عرفوه مسبقا - Strategy Evaluation Result - Post',
            'post_strategy_q3': 'تفحص الطلاب الكلمات التي يعرفونها من السابق في التعليمات - Strategy Evaluation Result - Post',
            'post_strategy_q4': ' استعان الطلاب بالصور لفهم التعليمات - Strategy Evaluation Result - Post',
            'post_test_score': 'Strategy Evaluation Result - Post',

            'pre_motivation_score': 'Motivation - Pre',
            'pre_motive_q1': 'أستمتع كثيرا بالنشاطات التي نقوم بها في دروس اللغة الإنجليزية - Motivation - Pre',
            'pre_motive_q2': 'لا احب ان أتكلم بلغة لا اعرفها جيدا - Motivation - Pre',
            'pre_motive_q3': 'احب ان يكون لدي أصدقاء يتكلمون لغات لا أعرفها - Motivation - Pre',
            'pre_motive_q4': 'لا احب ان اتعلم لغات جديدة غير التي اتعلمها في المدرسة - Motivation - Pre',

            'post_motivation_score': 'Motivation - Post',
            'post_motive_q1': 'أستمتع كثيرا بالنشاطات التي نقوم بها في دروس اللغة الإنجليزية - Motivation - Post',
            'post_motive_q2': 'لا احب ان أتكلم بلغة لا اعرفها جيدا - Motivation - Post',
            'post_motive_q3': 'احب ان يكون لدي أصدقاء يتكلمون لغات لا أعرفها - Motivation - Post',
            'post_motive_q4': 'لا احب ان اتعلم لغات جديدة غير التي اتعلمها في المدرسة - Motivation - Post',

            'pre_self_assessment_score': 'Self Assessment - Pre',
            'pre_self_q1': 'أستطيع الجلوس بهدوء عندما يجب عليّ ذلك - Self Assessment - Pre',
            'pre_self_q2': 'انتظر دوري للتّكلّم داخل الصّف - Self Assessment - Preّ',
            'pre_self_q3': 'أحافظ على هدوئي عندما أحزن أو أفرح - Self Assessment - Pre',
            'pre_self_q4': 'أستطيع إنجاز الوظائف الأكثر صعوبة إذا حاولت ذلك - Self Assessment - Pre',
            'pre_self_q5': 'أتعلّم ما درسته في المدرسة - Self Assessment - Pre',
            'pre_self_q6': 'عندما أجيب بشكل خاطئ، أعيد المحاولة حتّى أحصل على الإجابة الصّحيحة - Self Assessment - Pre',
            'pre_self_q7': 'عندما لا أحرز نتيجة جيّدة في الامتحان، أعمل جاهدًا للنّجاح في المرّة المقبلة - Self Assessment - Pre',
            'pre_self_q8': 'أعمل جاهدًا لإنهاء وظائفي المدرسيّة - Self Assessment - Pre',
            'pre_self_q9': 'أتمّم وظائفي المدرسية لأنّني أريد تعلّم أشياء جديدة - Self Assessment - Pre',
            'pre_self_q10': 'أتمّم وظائفي المدرسية لأنّني مهتم بالموضوع وبالتعلّم - Self Assessment - Pre',
            'pre_self_q11': 'اشعر بكثير من المرح مع أصدقائي في المدرسة - Self Assessment - Pre',
            'pre_self_q12': 'يحبني أصدقائي كما أنا - Self Assessment - Pre',
            'pre_self_q13': ' يصغي اليّ أستاذي باهتمام عندما أتحدث - Self Assessment - Pre',
            'pre_self_q14': 'عندما أكون بحاجة إلى المساعدة أحصل عليها من معلمي - Self Assessment - Pre',

            'post_self_assessment_score': 'Self Assessment - Post',
            'post_self_q1': 'أستطيع الجلوس بهدوء عندما يجب عليّ ذلك - Self Assessment - Post',
            'post_self_q2': 'انتظر دوري للتّكلّم داخل الصّفّ - Self Assessment - Post',
            'post_self_q3': 'أحافظ على هدوئي عندما أحزن أو أفرح - Self Assessment - Post',
            'post_self_q4': 'أستطيع إنجاز الوظائف الأكثر صعوبة إذا حاولت ذلك - Self Assessment - Post',
            'post_self_q5': 'أتعلّم ما درسته في المدرسة - Self Assessment - Post',
            'post_self_q6': 'عندما أجيب بشكل خاطئ، أعيد المحاولة حتّى أحصل على الإجابة الصّحيحة - Self Assessment - Post',
            'post_self_q7': 'عندما لا أحرز نتيجة جيّدة في الامتحان، أعمل جاهدًا للنّجاح في المرّة المقبلة - Self Assessment - Post',
            'post_self_q8': 'أعمل جاهدًا لإنهاء وظائفي المدرسيّة - Self Assessment - Post',
            'post_self_q9': 'أتمّم وظائفي المدرسية لأنّني أريد تعلّم أشياء جديدة - Self Assessment - Post',
            'post_self_q10': 'أتمّم وظائفي المدرسية لأنّني مهتم بالموضوع وبالتعلّم - Self Assessment - Post',
            'post_self_q11': 'اشعر بكثير من المرح مع أصدقائي في المدرسة - Self Assessment - Post',
            'post_self_q12': 'يحبني أصدقائي كما أنا - Self Assessment - Post',
            'post_self_q13': ' يصغي اليّ أستاذي باهتمام عندما أتحدث - Self Assessment - Post',
            'post_self_q14': 'عندما أكون بحاجة إلى المساعدة أحصل عليها من معلمي - Self Assessment - Post',

            'participation': 'Level of participation / Absence',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',
        }

        qs = self.get_queryset().extra(select={
            # 'participation': "CONCAT(participation, '_absence')",

            'pre_strategy_q1': "pre_test->>'RS_ASSESSMENT/FL1'",
            'pre_strategy_q2': "pre_test->>'RS_ASSESSMENT/FL2'",
            'pre_strategy_q3': "pre_test->>'RS_ASSESSMENT/FL3'",
            'pre_strategy_q4': "pre_test->>'RS_ASSESSMENT/FL4'",

            'post_strategy_q1': "post_test->>'RS_ASSESSMENT/FL1'",
            'post_strategy_q2': "post_test->>'RS_ASSESSMENT/FL2'",
            'post_strategy_q3': "post_test->>'RS_ASSESSMENT/FL3'",
            'post_strategy_q4': "post_test->>'RS_ASSESSMENT/FL4'",

            'pre_motive_q1': "pre_motivation->>'RS_ASSESSMENT/FL5'",
            'pre_motive_q2': "pre_motivation->>'RS_ASSESSMENT/FL6'",
            'pre_motive_q3': "pre_motivation->>'RS_ASSESSMENT/FL7'",
            'pre_motive_q4': "pre_motivation->>'RS_ASSESSMENT/FL8'",

            'post_motive_q1': "post_motivation->>'RS_ASSESSMENT/FL5'",
            'post_motive_q2': "post_motivation->>'RS_ASSESSMENT/FL6'",
            'post_motive_q3': "post_motivation->>'RS_ASSESSMENT/FL7'",
            'post_motive_q4': "post_motivation->>'RS_ASSESSMENT/FL8'",

            'pre_self_q1': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_1'",
            'pre_self_q2': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_2'",
            'pre_self_q3': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_3'",
            'pre_self_q4': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_4'",
            'pre_self_q5': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_5'",
            'pre_self_q6': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_6'",
            'pre_self_q7': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_7'",
            'pre_self_q8': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_8'",
            'pre_self_q9': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_9'",
            'pre_self_q10': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_10'",
            'pre_self_q11': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_11'",
            'pre_self_q12': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_12'",
            'pre_self_q13': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_13'",
            'pre_self_q14': "pre_self_assessment->>'SELF_ASSESSMENT/assessment_14'",

            'post_self_q1': "post_self_assessment->>'SELF_ASSESSMENT/assessment_1'",
            'post_self_q2': "post_self_assessment->>'SELF_ASSESSMENT/assessment_2'",
            'post_self_q3': "post_self_assessment->>'SELF_ASSESSMENT/assessment_3'",
            'post_self_q4': "post_self_assessment->>'SELF_ASSESSMENT/assessment_4'",
            'post_self_q5': "post_self_assessment->>'SELF_ASSESSMENT/assessment_5'",
            'post_self_q6': "post_self_assessment->>'SELF_ASSESSMENT/assessment_6'",
            'post_self_q7': "post_self_assessment->>'SELF_ASSESSMENT/assessment_7'",
            'post_self_q8': "post_self_assessment->>'SELF_ASSESSMENT/assessment_8'",
            'post_self_q9': "post_self_assessment->>'SELF_ASSESSMENT/assessment_9'",
            'post_self_q10': "post_self_assessment->>'SELF_ASSESSMENT/assessment_10'",
            'post_self_q11': "post_self_assessment->>'SELF_ASSESSMENT/assessment_11'",
            'post_self_q12': "post_self_assessment->>'SELF_ASSESSMENT/assessment_12'",
            'post_self_q13': "post_self_assessment->>'SELF_ASSESSMENT/assessment_13'",
            'post_self_q14': "post_self_assessment->>'SELF_ASSESSMENT/assessment_14'",

        }).values(
            'new_registry',
            'partner__name',
            'round__name',
            'type',
            'site',
            'school__name',
            'governorate__name_en',
            'district__name_en',
            'location',
            'language',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            # 'other_nationality',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__number',
            'student__family_status',
            'student__have_children',
            'disability__name_en',
            'internal_number',
            'comments',
            'hh_educational_level__name',
            'have_labour',
            'labours',
            'labour_hours',

            'registered_in_school__name',
            'shift',
            'grade__name',
            'referral',

            'pre_reading_score',
            'post_reading_score',

            'pre_test_arabic',
            'pre_test_language',
            'pre_test_math',
            'pre_test_science',

            'post_test_arabic',
            'post_test_language',
            'post_test_math',
            'post_test_science',

            'pre_test_score',
            'post_test_score',

            'pre_motivation_score',
            'post_motivation_score',
            'pre_self_assessment_score',
            'post_self_assessment_score',

            'pre_strategy_q1',
            'pre_strategy_q2',
            'pre_strategy_q3',
            'pre_strategy_q4',

            'post_strategy_q1',
            'post_strategy_q2',
            'post_strategy_q3',
            'post_strategy_q4',

            'pre_motive_q1',
            'pre_motive_q2',
            'pre_motive_q3',
            'pre_motive_q4',

            'post_motive_q1',
            'post_motive_q2',
            'post_motive_q3',
            'post_motive_q4',

            'pre_self_q1',
            'pre_self_q2',
            'pre_self_q3',
            'pre_self_q4',
            'pre_self_q5',
            'pre_self_q6',
            'pre_self_q7',
            'pre_self_q8',
            'pre_self_q9',
            'pre_self_q10',
            'pre_self_q11',
            'pre_self_q12',
            'pre_self_q13',
            'pre_self_q14',

            'post_self_q1',
            'post_self_q2',
            'post_self_q3',
            'post_self_q4',
            'post_self_q5',
            'post_self_q6',
            'post_self_q7',
            'post_self_q8',
            'post_self_q9',
            'post_self_q10',
            'post_self_q11',
            'post_self_q12',
            'post_self_q13',
            'post_self_q14',

            'participation',
            'barriers',
            'learning_result',

            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )

        return render_to_csv_response(qs, field_header_map=headers)


class CBECEExportViewSet(LoginRequiredMixin, ListView):
    model = CBECE
    queryset = CBECE.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):
        headers = {
            'id': 'enropllment_id',
            'new_registry': 'First time registered?',
            'partner__name': 'Partner',
            'source_of_identification': 'Source of Identification',
            'first_attendance_date': 'first attendance date',
            'round__name': 'CLM Round',
            'governorate__name_en': 'Governorate',
            'district__name_en': 'District',
            'cadaster__name_en': 'Cadaster',
            'location': 'Location',
            'language': 'The language supported in the program',
            'student__address': 'Student Address',
            'registration_level': 'Registration level',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Student Nationality',
            'other_nationality': 'Student Nationality Specify',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__number': 'unique number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'student_number_children': 'Child number of children',
            'disability__name_en': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'education_status': 'Education status',
            'miss_school_date': 'Miss school date',
            'comments': 'Comments',

            'phone_number': 'Phone number',
            'phone_number_confirm': 'Phone number confirm',
            'phone_owner': 'phone owner',
            'second_phone_number': 'Second Phone number',
            'second_phone_number_confirm': 'Second Phone number confirm',
            'second_phone_owner': 'Second phone owner',

            'id_type': 'ID Type',
            'case_number': 'UNHCR case number',
            'case_number_confirm': 'UNHCR case number confirm',
            'individual_case_number': 'Child individual ID',
            'individual_case_number_confirm': 'Child individual ID confirm',
            'parent_individual_case_number': 'Parent individual ID',
            'parent_individual_case_number_confirm': 'Parent individual ID confirm',
            'recorded_number': 'UNHCR recorded barcode',
            'recorded_number_confirm': 'UNHCR recorded barcode confirm',
            'national_number': 'Child Lebanese ID number',
            'national_number_confirm': 'Child Lebanese ID number confirm',
            'syrian_national_number': 'Child Syrian ID number',
            'syrian_national_number_confirm': 'Child Syrian ID number confirm',
            'sop_national_number': 'Child Palestinian ID number',
            'sop_national_number_confirm': 'Child Palestinian ID number confirm',
            'parent_national_number': 'Parent Lebanese ID number',
            'parent_national_number_confirm': 'Parent Lebanese ID number confirm',
            'parent_syrian_national_number': 'Parent Syrian ID number',
            'parent_syrian_national_number_confirm': 'Parent Syrian ID number confirm',
            'parent_sop_national_number': 'Parent Palestinian ID number',
            'parent_sop_national_number_confirm': 'Parent Palestinian ID number confirm',
            'parent_other_number': 'ID number of the Caretaker',
            'parent_other_number_confirm': 'ID number of the Caretaker confirm',
            'other_number': 'ID number of the child',
            'other_number_confirm': 'ID number of the child confirm',
            'main_caregiver': 'Main Caregiver',
            'main_caregiver_nationality__name': 'main caregiver nationality',
            'other_caregiver_relationship': 'other caregiver relationship',
            'caretaker_first_name': 'Caretaker first name',
            'caretaker_middle_name': 'Caretaker middle name',
            'caretaker_last_name': 'Caretaker last name',
            'caretaker_mother_name': 'Caretaker mother name',

            'hh_educational_level__name': 'What is the educational level of the mother?',
            'father_educational_level__name': 'What is the educational level of the father?',
            'have_labour_single_selection': 'Does the child participate in work?',
            'labours_single_selection': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',
            'labour_weekly_income': 'Child weekly income',
            'basic_stationery': 'Did the child receive basic stationery?',
            'remote_learning': 'Was the child involved in remote learning?',
            'remote_learning_reasons_not_engaged': 'what other reasons for this child not being engaged?',
            'reasons_not_engaged_other': 'reasons not engaged other',
            'reliable_internet': 'Does the family have reliable internet service in their area during remote learning?',
            'gender_participate': 'Did both girls and boys in the same family participate in the class and have access to the phone/device?',
            'gender_participate_explain': 'Explain',
            'remote_learning_engagement': 'Frequency of Child Engagement in remote learning?',
            'meet_learning_outcomes': 'How well did the child meet the learning outcomes?',
            'parent_learning_support_rate': 'How do you rate the parents learning support provided to the child through this Remote learning phase?',
            'covid_message': 'Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_message_how_often': 'How often?',
            'covid_parents_message': 'Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures?',
            'covid_parents_message_how_often': 'How often?',
            'follow_up_done': 'Was any follow-up done to ensure messages were well received, understood and adopted?',
            'follow_up_done_with_who': 'With who child and/or caregiver?',

            'pre_test_attended_arabic': 'pre test attended arabic',
            'pre_test_modality_arabic': 'pre test modality arabic',
            'pre_test_arabic': 'pre test arabic',
            'pre_test_attended_english': 'pre test attended english',
            'pre_test_modality_english': 'pre test modality english',
            'pre_test_english': 'pre test english',
            'pre_test_attended_psychomotor': 'pre test attended psychomotor',
            'pre_test_modality_psychomotor': 'pre test modality psychomotor',
            'pre_test_psychomotor': 'pre test psychomotor',
            'pre_test_attended_math': 'pre test attended math',
            'pre_test_modality_math': 'pre test modality math',
            'pre_test_math': 'pre test math',
            'pre_test_attended_social': 'pre test attended social',
            'pre_test_modality_social': 'pre test modality social',
            'pre_test_social_emotional': 'pre test social emotional',
            # 'pre_test_attended_science': 'pre test attended science',
            # 'pre_test_modality_science"': 'pre test modality science"',
            # 'pre_test_science"': 'pre test science"',
            # 'pre_test_attended_artistic': 'pre test attended artistic',
            # 'pre_test_modality_artistic': 'pre test modality artistic',
            # 'pre_test_social_artistic': 'pre test artistic',
            'pre_test_score': 'pre test score',
            #
            # 'post_test_attended_arabic': 'post test attended arabic',
            # 'post_test_modality_arabic': 'post test modality arabic',
            # 'post_test_arabic': 'post test arabic',
            # 'post_test_attended_english': 'post test attended english',
            # 'post_test_modality_english': 'post test modality english',
            # 'post_test_english': 'post test english',
            # 'post_test_attended_psychomotor': 'post test attended psychomotor',
            # 'post_test_modality_psychomotor': 'post test modality psychomotor',
            # 'post_test_psychomotor': 'post test psychomotor',
            # 'post_test_attended_math': 'post test attended math',
            # 'post_test_modality_math': 'post test modality math',
            # 'post_test_math': 'post test math',
            # 'post_test_attended_social': 'post test attended social',
            # 'post_test_modality_social': 'post test modality social',
            # 'post_test_social_emotional': 'post test social emotional',
            # 'post_test_attended_science': 'post test attended science',
            # 'post_test_modality_science"': 'post test modality science"',
            # 'post_test_science"': 'post test science"',
            # 'post_test_attended_artistic': 'post test attended artistic',
            # 'post_test_modality_artistic': 'post test modality artistic',
            # 'post_test_social_artistic': 'post test artistic',
            # 'post_test_score': 'post test score',

            'participation': 'Level of participation / Absence',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'student_outreached': 'Student outreached?',
            'have_barcode': 'Have barcode with him?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',

            'referral_programme_type_1': 'Referral programme type 1',
            'referral_partner_1': 'Referral partner 1',
            'referral_date_1': 'Referral date 1',
            'confirmation_date_1': 'Referral confirmation date 1',

            'referral_programme_type_2': 'Referral programme type 2',
            'referral_partner_2': 'Referral partner 2',
            'referral_date_2': 'Referral date 2',
            'confirmation_date_2': 'Referral confirmation date 2',

            'referral_programme_type_3': 'Referral programme type 3',
            'referral_partner_3': 'Referral partner 3',
            'referral_date_3': 'Referral date 3',
            'confirmation_date_3': 'Referral confirmation date 3',

            'followup_call_date_1': 'Follow-up call 1 date',
            'followup_call_reason_1': 'Follow-up call 1 reason',
            'followup_call_result_1': 'Follow-up call 1 result',

            'followup_call_date_2': 'Follow-up call 2 date',
            'followup_call_reason_2': 'Follow-up call 2 reason',
            'followup_call_result_2': 'Follow-up call 2 result',

            'followup_visit_date_1': 'Follow-up visit 1 date',
            'followup_visit_reason_1': 'Follow-up visit 1 reason',
            'followup_visit_result_1': 'Follow-up visit 1 result',
        }

        field_list = (

            'id'
            'new_registry',
            'partner__name',
            'source_of_identification',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'student__address',
            'language',
            'registration_level',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code'
            'student__id_number'
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'internal_number',
            'education_status',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',

            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number', 'ID number of the Caretaker',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',

            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',

            'pre_test_attended_arabic',
            'pre_test_modality_arabic',
            'pre_test_arabic',

            'pre_test_attended_english',
            'pre_test_modality_english',
            'pre_test_english',
            #
            'pre_test_attended_psychomotor',
            'pre_test_modality_psychomotor',
            'pre_test_psychomotor',

            'pre_test_attended_math',
            'pre_test_modality_math',
            'pre_test_math',

            'pre_test_attended_social',
            'pre_test_modality_social',
            'pre_test_social_emotional',

            # 'pre_test_attended_science',
            # 'pre_test_modality_science',
            # 'pre_test_science',
            #
            # 'pre_test_attended_artistic',
            # 'pre_test_modality_artistic',
            # 'pre_test_artistic',
            #
            'pre_test_score',

            # 'post_test_attended_arabic',
            # 'post_test_modality_arabic',
            # 'post_test_arabic',
            #
            # 'post_test_attended_english',
            # 'post_test_modality_english',
            # 'post_test_english',
            #
            # 'post_test_attended_psychomotor',
            # 'post_test_modality_psychomotor',
            # 'post_test_psychomotor',
            #
            # 'post_test_attended_math',
            # 'post_test_modality_math',
            # 'post_test_math',
            #
            # 'post_test_attended_social',
            # 'post_test_modality_social',
            # 'post_test_social_emotional',
            #
            # 'post_test_attended_science',
            # 'post_test_modality_science',
            # 'post_test_science',
            #
            # 'post_test_attended_artistic',
            # 'post_test_modality_artistic',
            # 'post_test_artistic',
            #
            # 'post_test_score',

            'participation',
            'barriers',
            'learning_result',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',

            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',

            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',

            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',

            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1'
        )

        qs = self.get_queryset().extra(select={
            # 'participation': "CONCAT(participation, '_absence')",

            'pre_test_attended_arabic': "pre_test->>'CBECE_ASSESSMENT/attended_arabic'",
            'pre_test_modality_arabic': "pre_test->>'CBECE_ASSESSMENT/modality_arabic'",
            'pre_test_arabic': "pre_test->>'CBECE_ASSESSMENT/arabic'",

            'pre_test_attended_english': "pre_test->>'CBECE_ASSESSMENT/attended_english'",
            'pre_test_modality_english': "pre_test->>'CBECE_ASSESSMENT/modality_english'",
            'pre_test_english': "pre_test->>'CBECE_ASSESSMENT/english'",

            'pre_test_attended_psychomotor': "pre_test->>'CBECE_ASSESSMENT/attended_psychomotor'",
            'pre_test_modality_psychomotor': "pre_test->>'CBECE_ASSESSMENT/modality_psychomotor'",
            'pre_test_psychomotor': "pre_test->>'CBECE_ASSESSMENT/psychomotor'",

            'pre_test_attended_math': "pre_test->>'CBECE_ASSESSMENT/attended_math'",
            'pre_test_modality_math': "pre_test->>'CBECE_ASSESSMENT/modality_math'",
            'pre_test_math': "pre_test->>'CBECE_ASSESSMENT/math'",

            'pre_test_attended_social': "pre_test->>'CBECE_ASSESSMENT/attended_social'",
            'pre_test_modality_social': "pre_test->>'CBECE_ASSESSMENT/modality_social'",
            'pre_test_social_emotional': "pre_test->>'CBECE_ASSESSMENT/social_emotional'",

            'pre_test_attended_science': "pre_test->>'CBECE_ASSESSMENT/attended_science'",
            'pre_test_modality_science': "pre_test->>'CBECE_ASSESSMENT/modality_science'",
            'pre_test_science': "pre_test->>'CBECE_ASSESSMENT/science'",

            'pre_test_attended_artistic': "pre_test->>'CBECE_ASSESSMENT/attended_artistic'",
            'pre_test_modality_artistic': "pre_test->>'CBECE_ASSESSMENT/modality_artistic'",
            'pre_test_artistic': "pre_test->>'CBECE_ASSESSMENT/artistic'",

            'post_test_attended_arabic': "post_test->>'CBECE_ASSESSMENT/attended_arabic'",
            'post_test_modality_arabic': "post_test->>'CBECE_ASSESSMENT/modality_arabic'",
            'post_test_arabic': "post_test->>'CBECE_ASSESSMENT/arabic'",

            'post_test_attended_english': "post_test->>'CBECE_ASSESSMENT/attended_english'",
            'post_test_modality_english': "post_test->>'CBECE_ASSESSMENT/modality_english'",
            'post_test_english': "post_test->>'CBECE_ASSESSMENT/english'",

            'post_test_attended_psychomotor': "post_test->>'CBECE_ASSESSMENT/attended_psychomotor'",
            'post_test_modality_psychomotor': "post_test->>'CBECE_ASSESSMENT/modality_psychomotor'",
            'post_test_psychomotor': "post_test->>'CBECE_ASSESSMENT/psychomotor'",

            'post_test_attended_math': "post_test->>'CBECE_ASSESSMENT/attended_math'",
            'post_test_modality_math': "post_test->>'CBECE_ASSESSMENT/modality_math'",
            'post_test_math': "post_test->>'CBECE_ASSESSMENT/math'",

            'post_test_attended_social': "post_test->>'CBECE_ASSESSMENT/attended_social'",
            'post_test_modality_social': "post_test->>'CBECE_ASSESSMENT/modality_social'",
            'post_test_social_emotional': "post_test->>'CBECE_ASSESSMENT/social_emotional'",

            'post_test_attended_science': "post_test->>'CBECE_ASSESSMENT/attended_science'",
            'post_test_modality_science': "post_test->>'CBECE_ASSESSMENT/modality_science'",
            'post_test_science': "post_test->>'CBECE_ASSESSMENT/science'",

            'post_test_attended_artistic': "post_test->>'CBECE_ASSESSMENT/attended_artistic'",
            'post_test_modality_artistic': "post_test->>'CBECE_ASSESSMENT/modality_artistic'",
            'post_test_artistic': "post_test->>'CBECE_ASSESSMENT/artistic'"

        }).values(
            'id',
            'new_registry',
            'partner__name',
            'first_attendance_date',
            'round__name',
            'governorate__name_en',
            'district__name_en',
            'cadaster__name_en',
            'location',
            'student__address',
            'language',
            'registration_level',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'other_nationality',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__number',
            'student__family_status',
            'student__have_children',
            'student_number_children',
            'disability__name_en',
            'internal_number',
            'education_status',
            'miss_school_date',
            'comments',
            'hh_educational_level__name',
            'father_educational_level__name',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_hours',
            'labour_weekly_income',
            'basic_stationery',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',

            'pre_test_attended_arabic',
            'pre_test_modality_arabic',
            'pre_test_arabic',

            'pre_test_attended_english',
            'pre_test_modality_english',
            'pre_test_english',

            'pre_test_attended_psychomotor',
            'pre_test_modality_psychomotor',
            'pre_test_psychomotor',

            'pre_test_attended_math',
            'pre_test_modality_math',
            'pre_test_math',

            'pre_test_attended_social',
            'pre_test_modality_social',
            'pre_test_social_emotional',

            # 'pre_test_attended_science',
            # 'pre_test_modality_science',
            # 'pre_test_science',

            # 'pre_test_attended_artistic',
            # 'pre_test_modality_artistic',
            # 'pre_test_artistic',

            'pre_test_score',

            # 'post_test_attended_arabic',
            # 'post_test_modality_arabic',
            # 'post_test_arabic',
            #
            # 'post_test_attended_english',
            # 'post_test_modality_english',
            # 'post_test_english',
            #
            # 'post_test_attended_psychomotor',
            # 'post_test_modality_psychomotor',
            # 'post_test_psychomotor',
            #
            # 'post_test_attended_math',
            # 'post_test_modality_math',
            # 'post_test_math',
            #
            # 'post_test_attended_social',
            # 'post_test_modality_social',
            # 'post_test_social_emotional',
            #
            # 'post_test_attended_science',
            # 'post_test_modality_science',
            # 'post_test_science',
            #
            # 'post_test_attended_artistic',
            # 'post_test_modality_artistic',
            # 'post_test_artistic',
            #
            # 'post_test_score',

            'participation',
            'barriers',
            'learning_result',
            'cycle_completed',
            'enrolled_at_school',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',

            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'source_of_identification',
            'main_caregiver',
            'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',

            'followup_call_date_1',
            'followup_call_reason_1',
            'followup_call_result_1',
            'followup_call_date_2',
            'followup_call_reason_2',
            'followup_call_result_2',
            'followup_visit_date_1',
            'followup_visit_reason_1',
            'followup_visit_result_1'
        )
        # print(qs.query)
        return render_to_csv_response(qs, field_header_map=headers, field_order=field_list)

def load_districts(request):
    id_governorate = request.GET.get('id_governorate')
    cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    id_district = request.GET.get('id_district')
    cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def search_clm_child(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    clm_type = request.GET.get('clm_type', 'BLN')
    term = request.GET.get('term', 0)
    terms = request.GET.get('term', 0)
    model = BLN
    if clm_type == 'RS':
        model = RS
    elif clm_type == 'ABLN':
        model = ABLN
    elif clm_type == 'CBECE':
        model = CBECE
    # qs = model.objects.filter(partner=request.user.partner_id)
    qs = {}

    if terms:
        if len(terms.split()) > 1:
            qs = model.objects.annotate(fullname=Concat('student__first_name', Value(' '),
                                                        'student__father_name', Value(' '),
                                                        'student__last_name')) \
                .filter(partner=request.user.partner_id) \
                .filter(fullname__icontains=terms) \
                .values('id', 'student__first_name', 'student__father_name',
                        'student__last_name', 'student__mother_fullname',
                        'student__sex', 'student__birthday_day', 'student__birthday_month',
                        'student__birthday_year', 'round__name', 'internal_number').distinct()
        else:
            # for term in terms:
            qs = model.objects.filter(partner=request.user.partner_id).filter(
                Q(student__first_name__contains=term) |
                Q(student__father_name__contains=term) |
                Q(student__last_name__contains=term) |
                Q(student__id_number__startswith=term) |
                Q(student__number__startswith=term) |
                Q(internal_number__startswith=term)
            ).values('id', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct()

    return JsonResponse({'result': json.dumps(list(qs))})


class ExecABLNUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'clm/execs.html'

    def get_context_data(self, **kwargs):
        instances = ABLN.objects.filter(round_id=8)
        instances.update(round_id=9)

        return {
            'result': instances.count(),
        }
