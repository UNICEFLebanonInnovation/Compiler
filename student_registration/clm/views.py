# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func
from django.db.models.expressions import RawSQL

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
from .filters import BLNFilter, RSFilter, CBECEFilter
from .tables import BootstrapTable, BLNTable, RSTable, CBECETable
from .models import BLN, RS, CBECE, SelfPerceptionGrades
from .forms import BLNForm, RSForm, CBECEForm
from .serializers import BLNSerializer, RSSerializer, CBECESerializer, SelfPerceptionGradesSerializer


class CLMView(LoginRequiredMixin,
              GroupRequiredMixin,
              TemplateView):

    template_name = 'clm/index.html'

    group_required = [u"CLM"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        return {}


class BLNAddView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):

    template_name = 'clm/common_form.html'
    form_class = BLNForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bln-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
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
            data['new_registry'] = self.request.GET.get('new_registry', '')
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

    template_name = 'clm/common_form.html'
    form_class = BLNForm
    success_url = '/clm/bln-list/'
    group_required = [u"CLM_BLN"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bln-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BLNEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = BLN.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return BLNForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = BLNSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            return BLNForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = BLN.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BLNEditView, self).form_valid(form)


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

        if model == 'BLN':
            enrollment = BLN.objects.get(id=int(enrollment_id))
        elif model == 'RS':
            enrollment = RS.objects.get(id=int(enrollment_id))
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
        return BLN.objects.filter(partner=self.request.user.partner_id)


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
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov), 2) if total_male_gov else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov), 2) if total_female_gov else 0.0,

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

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
            })

        return {
            'clm_round': clm_round,
            'clm_rounds': clm_rounds,
            'per_gov': per_gov
        }


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
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov), 2) if total_male_gov else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov), 2) if total_female_gov else 0.0,

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

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
            })

        return {
            'clm_round': clm_round,
            'clm_rounds': clm_rounds,
            'per_gov': per_gov
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
                'completion_male': round((float(completion_male_gov) * 100.0) / float(total_male_gov.count()), 2) if total_male_gov.count() else 0.0,
                'completion_female': round((float(completion_female_gov) * 100.0) / float(total_female_gov.count()), 2) if total_female_gov.count() else 0.0,

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

                'repetition_male': round((float(repeat_class_male_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
                'repetition_female': round((float(repeat_class_female_gov) / float(total_gov)) * 100.0, 2) if total_gov else 0.0,
            })

            d1_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_LanguageArtDomain')::float)", params=[]), post=RawSQL("((scores->>'post_LanguageArtDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d1_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_LanguageArtDomain')::float)", params=[]), post=RawSQL("((scores->>'post_LanguageArtDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d3_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_CognitiveDomain')::float)", params=[]), post=RawSQL("((scores->>'post_CognitiveDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d3_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_CognitiveDomain')::float)", params=[]), post=RawSQL("((scores->>'post_CognitiveDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d4_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_SocialEmotionalDomain')::float)", params=[]), post=RawSQL("((scores->>'post_SocialEmotionalDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d4_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_SocialEmotionalDomain')::float)", params=[]), post=RawSQL("((scores->>'post_SocialEmotionalDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d5_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_PsychomotorDomain')::float)", params=[]), post=RawSQL("((scores->>'post_PsychomotorDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d5_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_PsychomotorDomain')::float)", params=[]), post=RawSQL("((scores->>'post_PsychomotorDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

            d6_male = total_male_gov.annotate(pre=RawSQL("((scores->>'pre_ArtisticDomain')::float)", params=[]), post=RawSQL("((scores->>'post_ArtisticDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)
            d6_female = total_female_gov.annotate(pre=RawSQL("((scores->>'pre_ArtisticDomain')::float)", params=[]), post=RawSQL("((scores->>'post_ArtisticDomain')::float)", params=[])).aggregate(total=((Sum('post') - Sum('pre')) / Sum('pre')) * 100.0)

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

    template_name = 'clm/common_form.html'
    form_class = RSForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/rs-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
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

    template_name = 'clm/common_form.html'
    form_class = RSForm
    success_url = '/clm/rs-list/'
    group_required = [u"CLM_RS"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/rs-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
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
        return RS.objects.filter(partner=self.request.user.partner_id)


class CBECEAddView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):

    template_name = 'clm/common_form.html'
    form_class = CBECEForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/cbece-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
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
            data['new_registry'] = self.request.GET.get('new_registry', '')
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

    template_name = 'clm/common_form.html'
    form_class = CBECEForm
    success_url = '/clm/cbece-list/'
    group_required = [u"CLM_CBECE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/cbece-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CBECEEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = CBECE.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return CBECEForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = CBECESerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            return CBECEForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = CBECE.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(CBECEEditView, self).form_valid(form)


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
        return CBECE.objects.filter(partner=self.request.user.partner_id)


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
        qs = self.queryset
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

        qs = self.model.objects.all()

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
            'round__name': 'CLM Round',
            'governorate__name': 'Governorate',
            'district__name': 'District',
            'location': 'Location',
            'language': 'The language supported in the program',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Nationality',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'disability__name': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'comments': 'Comments',
            'hh_educational_level__name': 'What is the educational level of a person who is valuable to the child?',
            'have_labour': 'Does the child participate in work?',
            'labours': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',
            'pre_test_arabic': 'Pre-test Arabic',
            'pre_test_foreign_language': 'Pre-test Foreign language',
            'pre_test_math': 'Pre-test Math',
            'pre_test_score': 'Pre-test score',
            'post_test_arabic': 'Post-test Arabic',
            'post_test_foreign_language': 'Post-test Foreign language',
            'post_test_math': 'Post-test Math',
            'post_test_score': 'Post-test Score',
            'participation': 'How was the level of child participation in the program?',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'new_registry': 'First time registered?',
            'student_outreached': 'Student outreached?',
            'have_barcode': 'Have barcode with him?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',
        }

        qs = self.get_queryset().extra(select={
            'pre_test_arabic': "pre_test->>'BLN_ASSESSMENT/arabic'",
            'pre_test_foreign_language': "pre_test->>'BLN_ASSESSMENT/foreign_language'",
            'pre_test_math': "pre_test->>'BLN_ASSESSMENT/math'",
            'post_test_arabic': "pre_test->>'BLN_ASSESSMENT/arabic'",
            'post_test_foreign_language': "pre_test->>'BLN_ASSESSMENT/foreign_language'",
            'post_test_math': "pre_test->>'BLN_ASSESSMENT/math'",
        }).values(
            'round__name',
            'governorate__name',
            'district__name',
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
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__family_status',
            'student__have_children',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level__name',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_arabic',
            'pre_test_foreign_language',
            'pre_test_math',
            'pre_test_score',
            'post_test_arabic',
            'post_test_foreign_language',
            'post_test_math',
            'post_test_score',
            'participation',
            'barriers',
            'learning_result',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )

        return render_to_csv_response(qs, field_header_map=headers)


class RSExportViewSet(LoginRequiredMixin, ListView):

    model = RS
    queryset = RS.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):

        headers = {
            'round__name': 'CLM Round',
            'type': 'Program type',
            'site': 'Program site',
            'school__name': 'Attending in school',
            'governorate__name': 'Governorate',
            'district__name': 'District',
            'location': 'Location',
            'language': 'The language supported in the program',
            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Nationality',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'disability__name': 'Does the child have any disability or special need?',
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

            'pre_test_score': 'Strategy Evaluation Result - Pre',
            'post_test_score': 'Strategy Evaluation Result - Post',

            'pre_motivation_score': 'Motivation - Pre',
            'post_motivation_score': 'Motivation - Post',
            'pre_self_assessment_score': 'Self Assessment - Pre',
            'post_self_assessment_score': 'Self Assessment - Post',

            'participation': 'How was the level of child participation in the program?',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'new_registry': 'First time registered?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',
        }

        qs = self.get_queryset().values(
            'round__name',
            'type',
            'site',
            'school__name',
            'governorate__name',
            'district__name',
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
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__family_status',
            'student__have_children',
            'disability__name',
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

            'participation',
            'barriers',
            'learning_result',

            'new_registry',
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
            'round__name': 'CLM Round',
            'cycle__name': 'Cycle',
            'site': 'Program site',
            'school__name': 'Attending in school',
            'governorate__name': 'Governorate',
            'district__name': 'District',
            'location': 'Location',
            'language': 'The language supported in the program',
            'referral': 'Where was the child referred?',

            'student__first_name': 'First name',
            'student__father_name': 'Father name',
            'student__last_name': 'Last name',
            'student__sex': 'Sex',
            'student__birthday_day': 'Birthday - day',
            'student__birthday_month': 'Birthday - month',
            'student__birthday_year': 'Birthday - year',
            'student__nationality__name': 'Nationality',
            'student__mother_fullname': 'Mother fullname',
            'student__p_code': 'P-Code If a child lives in a tent / Brax in a random camp',
            'student__id_number': 'ID number',
            'student__family_status': 'What is the family status of the child?',
            'student__have_children': 'Does the child have children?',
            'disability__name': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'comments': 'Comments',
            'child_muac': 'Child MUAC',

            'hh_educational_level__name': 'What is the educational level of a person who is valuable to the child?',
            'have_labour': 'Does the child participate in work?',
            'labours': 'What is the type of work?',
            'labour_hours': 'How many hours does this child work in a day?',

            'pre_test_score': 'Academic Result - Pre',
            'post_test_score': 'Academic Result - Post',

            'pre_test_LanguageArtDomain1': 'Language Art Domain - Pre - Cycle 1',
            'pre_test_CognitiveDomian1': 'Cognitive Domain - Pre - Cycle 1',
            'pre_test_ScienceDomain1': 'Science Domain - Pre - Cycle 1',
            'pre_test_SocialEmotionalDomain1': 'Social Emotional Domain - Pre - Cycle 1',
            'pre_test_PsychomotorDomain1': 'Psychomotor Domain - Pre - Cycle 1',
            'pre_test_ArtisticDomain1': 'Artistic Domain - Pre - Cycle 1',

            'post_test_LanguageArtDomain1': 'Language Art Domain - Post - Cycle 1',
            'post_test_CognitiveDomian1': 'Cognitive Domain - Post - Cycle 1',
            'post_test_ScienceDomain1': 'Science Domain - Post - Cycle 1',
            'post_test_SocialEmotionalDomain1': 'Social Emotional Domain - Post - Cycle 1',
            'post_test_PsychomotorDomain1': 'Psychomotor Domain - Post - Cycle 1',
            'post_test_ArtisticDomain1': 'Artistic Domain - Post - Cycle 1',

            'pre_test_LanguageArtDomain2': 'Language Art Domain - Pre - Cycle 2',
            'pre_test_CognitiveDomian2': 'Cognitive Domain - Pre - Cycle 2',
            'pre_test_ScienceDomain2': 'Science Domain - Pre - Cycle 2',
            'pre_test_SocialEmotionalDomain2': 'Social Emotional Domain - Pre - Cycle 2',
            'pre_test_PsychomotorDomain2': 'Psychomotor Domain - Pre - Cycle 2',
            'pre_test_ArtisticDomain2': 'Artistic Domain - Pre - Cycle 2',

            'post_test_LanguageArtDomain2': 'Language Art Domain - Post - Cycle 2',
            'post_test_CognitiveDomian2': 'Cognitive Domain - Post - Cycle 2',
            'post_test_ScienceDomain2': 'Science Domain - Post - Cycle 2',
            'post_test_SocialEmotionalDomain2': 'Social Emotional Domain - Post - Cycle 2',
            'post_test_PsychomotorDomain2': 'Psychomotor Domain - Post - Cycle 2',
            'post_test_ArtisticDomain2': 'Artistic Domain - Post - Cycle 2',

            'pre_test_LanguageArtDomain3': 'Language Art Domain - Pre - Cycle 3',
            'pre_test_CognitiveDomian3': 'Cognitive Domain - Pre - Cycle 3',
            'pre_test_ScienceDomain3': 'Science Domain - Pre - Cycle 3',
            'pre_test_SocialEmotionalDomain3': 'Social Emotional Domain - Pre - Cycle 3',
            'pre_test_PsychomotorDomain3': 'Psychomotor Domain - Pre - Cycle 3',
            'pre_test_ArtisticDomain3': 'Artistic Domain - Pre - Cycle 3',

            'post_test_LanguageArtDomain3': 'Language Art Domain - Post - Cycle 3',
            'post_test_CognitiveDomian3': 'Cognitive Domain - Post - Cycle 3',
            'post_test_ScienceDomain3': 'Science Domain - Post - Cycle 3',
            'post_test_SocialEmotionalDomain3': 'Social Emotional Domain - Post - Cycle 3',
            'post_test_PsychomotorDomain3': 'Psychomotor Domain - Post - Cycle 3',
            'post_test_ArtisticDomain3': 'Artistic Domain - Post - Cycle 3',

            'participation': 'How was the level of child participation in the program?',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
            'new_registry': 'First time registered?',
            'student_outreached': 'Student outreached?',
            'have_barcode': 'Have barcode with him?',
            'owner__username': 'owner',
            'modified_by__username': 'modified_by',
            'created': 'created',
            'modified': 'modified',
        }

        qs = self.get_queryset().extra(select={
            'pre_test_LanguageArtDomain1': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain1'",
            'pre_test_CognitiveDomian1': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian1'",
            'pre_test_ScienceDomain1': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain1'",
            'pre_test_SocialEmotionalDomain1': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain1'",
            'pre_test_PsychomotorDomain1': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain1'",
            'pre_test_ArtisticDomain1': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain1'",

            'post_test_LanguageArtDomain1': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain1'",
            'post_test_CognitiveDomian1': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian1'",
            'post_test_ScienceDomain1': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain1'",
            'post_test_SocialEmotionalDomain1': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain1'",
            'post_test_PsychomotorDomain1': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain1'",
            'post_test_ArtisticDomain1': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain1'",

            'pre_test_LanguageArtDomain2': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain2'",
            'pre_test_CognitiveDomian2': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian2'",
            'pre_test_ScienceDomain2': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain2'",
            'pre_test_SocialEmotionalDomain2': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain2'",
            'pre_test_PsychomotorDomain2': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain2'",
            'pre_test_ArtisticDomain2': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain2'",

            'post_test_LanguageArtDomain2': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain2'",
            'post_test_CognitiveDomian2': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian2'",
            'post_test_ScienceDomain2': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain2'",
            'post_test_SocialEmotionalDomain2': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain2'",
            'post_test_PsychomotorDomain2': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain2'",
            'post_test_ArtisticDomain2': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain2'",

            'pre_test_LanguageArtDomain3': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain3'",
            'pre_test_CognitiveDomian3': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian3'",
            'pre_test_ScienceDomain3': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain3'",
            'pre_test_SocialEmotionalDomain3': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain3'",
            'pre_test_PsychomotorDomain3': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain3'",
            'pre_test_ArtisticDomain3': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain3'",

            'post_test_LanguageArtDomain3': "pre_test->>'CBECE_ASSESSMENT/LanguageArtDomain3'",
            'post_test_CognitiveDomian3': "pre_test->>'CBECE_ASSESSMENT/CognitiveDomian3'",
            'post_test_ScienceDomain3': "pre_test->>'CBECE_ASSESSMENT/ScienceDomain3'",
            'post_test_SocialEmotionalDomain3': "pre_test->>'CBECE_ASSESSMENT/SocialEmotionalDomain3'",
            'post_test_PsychomotorDomain3': "pre_test->>'CBECE_ASSESSMENT/PsychomotorDomain3'",
            'post_test_ArtisticDomain3': "pre_test->>'CBECE_ASSESSMENT/ArtisticDomain3'",

        }).values(
            'round__name',
            'cycle__name',
            'site',
            'school__name',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'referral',

            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__sex',
            'student__birthday_day',
            'student__birthday_month',
            'student__birthday_year',
            'student__nationality__name',
            'student__mother_fullname',
            'student__p_code',
            'student__id_number',
            'student__family_status',
            'student__have_children',
            'disability__name',
            'internal_number',
            'comments',
            'child_muac',

            'hh_educational_level__name',
            'have_labour',
            'labours',
            'labour_hours',

            'pre_test_score',
            'post_test_score',

            'pre_test_LanguageArtDomain1',
            'pre_test_CognitiveDomian1',
            'pre_test_ScienceDomain1',
            'pre_test_SocialEmotionalDomain1',
            'pre_test_PsychomotorDomain1',
            'pre_test_ArtisticDomain1',

            'post_test_LanguageArtDomain1',
            'post_test_CognitiveDomian1',
            'post_test_ScienceDomain1',
            'post_test_SocialEmotionalDomain1',
            'post_test_PsychomotorDomain1',
            'post_test_ArtisticDomain1',

            'pre_test_LanguageArtDomain2',
            'pre_test_CognitiveDomian2',
            'pre_test_ScienceDomain2',
            'pre_test_SocialEmotionalDomain2',
            'pre_test_PsychomotorDomain2',
            'pre_test_ArtisticDomain2',

            'post_test_LanguageArtDomain2',
            'post_test_CognitiveDomian2',
            'post_test_ScienceDomain2',
            'post_test_SocialEmotionalDomain2',
            'post_test_PsychomotorDomain2',
            'post_test_ArtisticDomain2',

            'pre_test_LanguageArtDomain3',
            'pre_test_CognitiveDomian3',
            'pre_test_ScienceDomain3',
            'pre_test_SocialEmotionalDomain3',
            'pre_test_PsychomotorDomain3',
            'pre_test_ArtisticDomain3',

            'post_test_LanguageArtDomain3',
            'post_test_CognitiveDomian3',
            'post_test_ScienceDomain3',
            'post_test_SocialEmotionalDomain3',
            'post_test_PsychomotorDomain3',
            'post_test_ArtisticDomain3',

            'participation',
            'barriers',
            'learning_result',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )

        return render_to_csv_response(qs, field_header_map=headers)
