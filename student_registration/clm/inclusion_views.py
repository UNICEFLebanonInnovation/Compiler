# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.backends.djqscsv import render_to_csv_response
from student_registration.users.utils import force_default_language
from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer

from .tables import BootstrapTable
from .inclusion_tables import InclusionTable
from .inclusion_filters import InclusionFilter
from .models import Inclusion
from .inclusion_forms import InclusionForm, InclusionReferralForm, InclusionAssessmentForm
from .utils import is_allowed_create, is_allowed_edit
from .inclusion_serializers import InclusionSerializer


class InclusionAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):

    template_name = 'clm/inclusion_add_form.html'
    form_class = InclusionForm
    success_url = '/clm/inclusion-list/'
    group_required = [u"CLM_Inclusion"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/inclusion-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/inclusion-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        # kwargs['is_allowed_create'] = is_allowed_create('Inclusion')
        return super(InclusionAddView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.save(self.request)
        return super(InclusionAddView, self).form_valid(form)


class InclusionEditView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FormView):

    template_name = 'clm/inclusion_edit_form.html'
    form_class = InclusionForm
    success_url = '/clm/inclusion-list/'
    group_required = [u"CLM_Inclusion"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/inclusion-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/inclusion-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        # kwargs['is_allowed_edit'] = is_allowed_edit('Inclusion')
        return super(InclusionEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Inclusion.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return InclusionForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = InclusionSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            return InclusionForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Inclusion.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(InclusionEditView, self).form_valid(form)


class InclusionListView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FilterView,
                        ExportMixin,
                        SingleTableView,
                        RequestConfig):

    table_class = InclusionTable
    model = Inclusion
    template_name = 'clm/inclusion_list.html'
    table = BootstrapTable(Inclusion.objects.all(), order_by='id')
    group_required = [u"CLM_Inclusion"]
    filterset_class = InclusionFilter

    def get_queryset(self):
        force_default_language(self.request)
        return Inclusion.objects.filter(partner=self.request.user.partner_id).order_by('-id')


class InclusionReferralView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):

    template_name = 'clm/inclusion_referral.html'
    form_class = InclusionReferralForm
    success_url = '/clm/inclusion-list/'
    group_required = [u"CLM_Inclusion"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(InclusionReferralView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Inclusion.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = Inclusion.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(InclusionReferralView, self).form_valid(form)


class InclusionAssessmentView(LoginRequiredMixin,
                              GroupRequiredMixin,
                              FormView):

    template_name = 'clm/inclusion_assessment.html'
    form_class = InclusionAssessmentForm
    success_url = '/clm/inclusion-list/'
    group_required = [u"CLM_Inclusion"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(InclusionAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Inclusion.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)
        else:
            return form_class(instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Inclusion.objects.get(id=self.kwargs['pk'], partner=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(InclusionAssessmentView, self).form_valid(form)


class InclusionExportViewSet(LoginRequiredMixin, ListView):

    model = Inclusion
    queryset = Inclusion.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(partner=self.request.user.partner)
        return self.queryset

    def get(self, request, *args, **kwargs):

        headers = {
            'id': 'enropllment_id',
            'partner__name': 'Partner',
            'source_of_identification': 'Source of Identification',
            'first_attendance_date': 'first attendance date',
            'governorate__name_en': 'Governorate',
            'district__name_en': 'District',
            'location': 'Location',
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
            'student__number': 'unique number',
            'disability__name_en': 'Does the child have any disability or special need?',
            'internal_number': 'Internal number',
            'comments': 'Comments',

            'phone_number': 'Phone number',
            'phone_number_confirm': 'Phone number confirm',

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
            'caretaker_first_name': 'Caretaker first name',
            'caretaker_middle_name': 'Caretaker middle name',
            'caretaker_last_name': 'Caretaker last name',
            'caretaker_mother_name': 'Caretaker mother name',

            'have_labour': 'Does the child participate in work?',
            'labour_type': 'What is the type of work?',

            'participation': 'Level of participation / Absence',
            'barriers': 'The main barriers affecting the daily attendance and performance of the child or drop out of school?',
            'learning_result': 'Based on the overall score, what is the recommended learning path?',
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
        }

        field_list = (
            'id',
            'partner__name',
            'source_of_identification',
            'first_attendance_date',
            'governorate__name_en',
            'district__name_en',
            'location',
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
            'student__number',
            'disability__name_en',
            'internal_number',
            'comments',

            'phone_number',
            'phone_number_confirm',

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
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',

            'have_labour',
            'labour_type',

            'participation',
            'barriers',
            'learning_result',

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

            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )

        qs = self.get_queryset().values(
            'id',
            'partner__name',
            'first_attendance_date',
            'governorate__name_en',
            'district__name_en',
            'location',
            # 'language',
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
            'student__number',
            'student__family_status',
            'student__have_children',
            'disability__name_en',
            'internal_number',
            'comments',
            'have_labour',
            'labour_type',
            'participation',
            'barriers',
            'learning_result',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',

            'phone_number',
            'phone_number_confirm',
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
            'source_of_identification',
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
        )

        return render_to_csv_response(qs, field_header_map=headers, field_order=field_list)
