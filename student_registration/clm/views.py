# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import tablib

from django.utils.translation import ugettext as _
from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func
from django.db.models.expressions import RawSQL

from import_export.formats import base_formats
from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

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

        queryset = self.get_queryset()
        data = tablib.Dataset()

        data.headers = [
            _('CLM round'),
            _('Governorate'),
            _('District'),
            _('Location'),
            _('The language supported in the program'),

            _('First name'),
            _('Father name'),
            _('Last name'),
            _('Sex'),
            _('Birthday day'),
            _('Birthday month'),
            _('Birthday year'),
            _('Birthday'),
            _('Nationality'),
            _('Mother fullname'),

            _('P-Code If a child lives in a tent / Brax in a random camp'),
            _('Does the child have any disability or special need?'),
            _('Internal number'),
            _('ID number'),
            _('Comments'),

            _('What is the educational level of a person who is valuable to the child?'),
            _('Does the child participate in work?'),
            _('What is the type of work ?'),
            _('How many hours does this child work in a day?'),

            _('What is the family status of the child?'),
            _("Does the child have children?"),

            _('Arabic - Pre'),
            _('Language - Pre'),
            _('Math - Pre'),

            _('Assessment Result - Pre'),

            _('Arabic - Post'),
            _('Language - Post'),
            _('Math - Post'),

            _('Academic Result - Post'),

            _('Arabic - Improvement'),
            _('Language - Improvement'),
            _('Math - Improvement'),
            _('Academic Result - Improvement'),

            _('How was the level of child participation in the program?'),
            _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
            _('Based on the overall score, what is the recommended learning path?'),

            _("First time registered?"),
            _("Student outreached?"),
            _("Have barcode with him?"),

        ]

        content = []
        for line in queryset:
            if not line.student:
                continue
            student = line.student
            content = [
                line.round.name if line.round else '',
                line.governorate.name if line.governorate else '',
                line.district.name if line.district else '',
                line.location,
                line.language,

                student.first_name,
                student.father_name,
                student.last_name,
                student.sex,
                student.birthday_day,
                student.birthday_month,
                student.birthday_year,
                student.birthday,
                student.nationality.name if student.nationality else '',
                student.mother_fullname,

                student.p_code,
                line.disability.name if line.disability else '',
                line.internal_number,
                student.id_number,
                line.comments,

                line.hh_educational_level,
                line.have_labour,
                line.labours,
                line.labour_hours,

                student.family_status,
                student.have_children,

                line.get_assessment_value('arabic', 'pre_test'),
                line.get_assessment_value('foreign_language', 'pre_test'),
                line.get_assessment_value('math', 'pre_test'),

                line.pre_test_score,

                line.get_assessment_value('arabic', 'post_test'),
                line.get_assessment_value('foreign_language', 'post_test'),
                line.get_assessment_value('math', 'post_test'),

                line.post_test_score,

                line.arabic_improvement,
                line.foreign_language_improvement,
                line.math_improvement,
                line.assessment_improvement,

                line.participation,
                line.barriers,
                line.learning_result,

                line.new_registry,
                line.student_outreached,
                line.have_barcode,
            ]
            data.append(content)

        file_format = base_formats.XLSX()
        data = file_format.export_data(data)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=bln_registrations_list.xlsx'
        return response


class RSExportViewSet(LoginRequiredMixin, ListView):

    model = RS
    queryset = RS.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        data = tablib.Dataset()

        data.headers = [
            _('CLM round'),
            _('Program type'),
            _('Program site'),
            _('Attending in school'),
            _('Governorate'),
            _('District'),
            _('Location'),
            _('The language supported in the program'),

            _('First name'),
            _('Father name'),
            _('Last name'),
            _('Sex'),
            _('Birthday day'),
            _('Birthday month'),
            _('Birthday year'),
            _('Birthday'),
            _('Nationality'),
            _('Mother fullname'),

            _('P-Code If a child lives in a tent / Brax in a random camp'),
            _('Does the child have any disability or special need?'),
            _('Internal number'),
            _('ID number'),
            _('Comments'),

            _('What is the educational level of a person who is valuable to the child?'),
            _('Does the child participate in work?'),
            _('What is the type of work ?'),
            _('How many hours does this child work in a day?'),

            _('What is the family status of the child?'),
            _("Does the child have children?"),

            _('Registered in school'),
            _('Shift'),
            _('Class'),
            _('Reason of referral'),

            _('Arabic reading - Pre-test'),
            _('Arabic reading - Post-test'),
            _('Arabic reading - Improvement'),

            _('Arabic - Pre'),
            _('Language - Pre'),
            _('Science - Pre'),
            _('Math - Pre'),

            _('Assessment Result - Pre'),

            _('Arabic - Post'),
            _('Language - Post'),
            _('Science - Post'),
            _('Math - Post'),

            _('Assessment Result - Post'),
            _('Arabic - Improvement'),
            _('Language - Improvement'),
            _('Science - Improvement'),
            _('Math - Improvement'),
            _('Assessment Result - Improvement'),

            _('Strategy Evaluation Result - Pre'),
            _('Strategy Evaluation Result - Post'),
            _('Strategy Evaluation Result - Improvement'),

            _('Motivation - Pre'),
            _('Motivation - Post'),
            _('Motivation - Improvement'),

            _('Self Assessment - Pre'),
            _('Self Assessment - Post'),
            _('Self Assessment - Improvement'),

            _('How was the level of child participation in the program?'),
            _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
            _('Based on the overall score, what is the recommended learning path?'),

            _("First time registered?"),

        ]

        content = []
        for line in queryset:
            if not line.student:
                continue
            student = line.student
            content = [
                line.round.name if line.round else '',
                line.type,
                line.site,
                line.school.name if line.school else '',
                line.governorate.name if line.governorate else '',
                line.district.name if line.district else '',
                line.location,
                line.language,

                student.first_name,
                student.father_name,
                student.last_name,
                student.sex,
                student.birthday_day,
                student.birthday_month,
                student.birthday_year,
                student.birthday,
                student.nationality.name if student.nationality else '',
                student.mother_fullname,

                student.p_code,
                line.disability.name if line.disability else '',
                line.internal_number,
                student.id_number,
                line.comments,

                line.hh_educational_level,
                line.have_labour,
                line.labours,
                line.labour_hours,

                student.family_status,
                student.have_children,

                line.registered_in_school.name if line.registered_in_school else '',
                line.shift,
                line.grade.name if line.grade else '',
                line.referral,

                line.pre_reading_score,
                line.post_reading_score,
                line.arabic_reading_improvement,

                line.pre_test_arabic,
                line.pre_test_language,
                line.pre_test_math,
                line.pre_test_science,

                line.pretest_result,

                line.post_test_arabic,
                line.post_test_language,
                line.post_test_math,
                line.post_test_science,

                line.posttest_result,

                line.arabic_improvement,
                line.language_improvement,
                line.science_improvement,
                line.math_improvement,
                line.academic_test_improvement,

                line.pre_test_score,
                line.post_test_score,
                line.assessment_improvement,
                line.pre_motivation_score,
                line.post_motivation_score,
                line.motivation_improvement,
                line.pre_self_assessment_score,
                line.post_self_assessment_score,
                line.self_assessment_improvement,

                line.participation,
                line.barriers,
                line.learning_result,

                line.new_registry,
            ]
            data.append(content)

        file_format = base_formats.XLSX()
        data = file_format.export_data(data)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=rs_registrations_list.xlsx'
        return response


class CBECEExportViewSet(LoginRequiredMixin, ListView):

    model = CBECE
    queryset = CBECE.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        data = tablib.Dataset()

        data.headers = [
            _('CLM round'),
            _('Cycle'),
            _('Program site'),
            _('Attending in school'),
            _('Governorate'),
            _('District'),
            _('Location'),
            _('The language supported in the program'),

            _('Where was the child referred?'),
            _('First name'),
            _('Father name'),
            _('Last name'),
            _('Sex'),
            _('Birthday day'),
            _('Birthday month'),
            _('Birthday year'),
            _('Birthday'),
            _('Nationality'),
            _('Mother fullname'),

            _('P-Code If a child lives in a tent / Brax in a random camp'),
            _('Does the child have any disability or special need?'),
            _('Internal number'),
            _('ID number'),
            _('Comments'),
            _('Child MUAC'),

            _('What is the educational level of a person who is valuable to the child?'),
            _('Does the child participate in work?'),
            _('What is the type of work ?'),
            _('How many hours does this child work in a day?'),

            _('Language Art Domain - Pre'),
            _('Cognitive Domain - Pre'),
            _('Science Domain - Pre'),
            _('Social Emotional Domain - Pre'),
            _('Psychomotor Domain - Pre'),
            _('Artistic Domain - Pre'),

            _('Academic Result - Pre'),

            _('Language Art Domain - Post'),
            _('Cognitive Domain - Post'),
            _('Science Domain - Post'),
            _('Social Emotional Domain - Post'),
            _('Psychomotor Domain - Post'),
            _('Artistic Domain - Post'),

            _('Academic Result - Post'),

            _('Language Art Domain - Improvement'),
            _('Cognitive Domain - Improvement'),
            _('Science Domain - Improvement'),
            _('Social Emotional Domain - Improvement'),
            _('Psychomotor Domain - Improvement'),
            _('Artistic Domain - Improvement'),

            _('Academic Result - Improvement'),

            _('How was the level of child participation in the program?'),
            _('The main barriers affecting the daily attendance and performance of the child or drop out of school?'),
            _('Based on the overall score, what is the recommended learning path?'),

            _("First time registered?"),
            _("Student outreached?"),
            _("Have barcode with him?"),

        ]

        content = []
        for line in queryset:
            if not line.student:
                continue
            student = line.student
            content = [
                line.round.name if line.round else '',
                line.cycle.name if line.cycle else '',
                line.site,
                line.school.name if line.school else '',
                line.governorate.name if line.governorate else '',
                line.district.name if line.district else '',
                line.location,
                line.language,

                line.referral,
                student.first_name,
                student.father_name,
                student.last_name,
                student.sex,
                student.birthday_day,
                student.birthday_month,
                student.birthday_year,
                student.birthday,
                student.nationality.name if student.nationality else '',
                student.mother_fullname,

                student.p_code,
                line.disability.name if line.disability else '',
                line.internal_number,
                student.id_number,
                line.comments,
                line.child_muac,

                line.hh_educational_level,
                line.have_labour,
                line.labours,
                line.labour_hours,

                line.get_assessment_value('LanguageArtDomain', 'pre_test'),
                line.get_assessment_value('CognitiveDomian', 'pre_test'),
                line.get_assessment_value('ScienceDomain', 'pre_test'),
                line.get_assessment_value('SocialEmotionalDomain', 'pre_test'),
                line.get_assessment_value('PsychomotorDomain', 'pre_test'),
                line.get_assessment_value('ArtisticDomain', 'pre_test'),

                line.pre_test_score,

                line.get_assessment_value('LanguageArtDomain', 'post_test'),
                line.get_assessment_value('CognitiveDomian', 'post_test'),
                line.get_assessment_value('ScienceDomain', 'post_test'),
                line.get_assessment_value('SocialEmotionalDomain', 'post_test'),
                line.get_assessment_value('PsychomotorDomain', 'post_test'),
                line.get_assessment_value('ArtisticDomain', 'post_test'),

                line.post_test_score,

                line.art_improvement,
                line.cognitive_improvement,
                line.science_improvement,
                line.social_improvement,
                line.psycho_improvement,
                line.artistic_improvement,

                line.assessment_improvement,

                line.participation,
                line.barriers,
                line.learning_result,

                line.new_registry,
                line.student_outreached,
                line.have_barcode,
            ]
            data.append(content)

        file_format = base_formats.XLSX()
        data = file_format.export_data(data)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=cbece_registrations_list.xlsx'
        return response
