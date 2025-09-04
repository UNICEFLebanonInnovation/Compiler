# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import date
import tablib
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from import_export.formats import base_formats
from student_registration.alp.templatetags.util_tags import has_group, is_owner

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from .filters import EnrollmentFilter, EnrollmentOldDataFilter
from .tables import BootstrapTable, EnrollmentTable, EnrollmentOldDataTable
from student_registration.alp.models import Outreach
from student_registration.alp.serializers import OutreachSerializer
from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer
from student_registration.schools.models import ClassRoom, School
from .models import (
    Enrollment,
    EducationYear,
)
from .forms import (
    EnrollmentForm,
    EnrollmentRegionForm,
    EditOldDataForm,
)
from .serializers import (
    EnrollmentSerializer,
)


class AddView(LoginRequiredMixin,
              GroupRequiredMixin,
              FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = EnrollmentForm
    success_url = '/enrollments/list/'
    group_required = [u"ENROL_CREATE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/enrollments/add/'
        return self.success_url

    def get_context_data(self, **kwargs):

        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(AddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(AddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }
        if self.request.GET.get('enrollment_id'):
            if self.request.GET.get('school_type', None) == 'alp':
                instance = Outreach.objects.get(id=self.request.GET.get('enrollment_id'))
                data = OutreachSerializer(instance).data

                data['classroom'] = ''
                data['participated_in_alp'] = 'yes'
                data['last_informal_edu_round'] = instance.alp_round_id
                data['last_informal_edu_final_result'] = instance.refer_to_level_id

                data['last_education_level'] = ClassRoom.objects.get(name='n/a').id
                data['last_school_type'] = 'na'
                data['last_school_shift'] = 'na'
                data['last_school'] = School.objects.get(number='na').id
                data['last_education_year'] = 'na'
                data['last_year_result'] = 'na'

            else:
                instance = Enrollment.objects.get(id=self.request.GET.get('enrollment_id'))
                data = EnrollmentSerializer(instance).data

                data['classroom'] = ''
                data['last_education_level'] = instance.classroom_id
                data['last_school_type'] = 'public_in_country'
                data['last_school_shift'] = 'second'
                data['last_school'] = instance.school_id
                data['last_education_year'] = data['education_year_name']
                data['last_year_result'] = instance.last_year_grading_result

            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
        if data:
            data['new_registry'] = self.request.GET.get('new_registry', '')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    # def get_form(self, form_class=None):
    #     if self.request.method == "POST":
    #         return EnrollmentForm(self.request.POST, request=self.request)
    #     else:
    #         return EnrollmentForm(self.get_initial())

    def form_valid(self, form):
        form.save(self.request)
        return super(AddView, self).form_valid(form)


class EditView(LoginRequiredMixin,
               GroupRequiredMixin,
               FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = EnrollmentForm
    success_url = '/enrollments/list/'
    group_required = [u"ENROL_EDIT"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/enrollments/add/'
        return self.success_url

    def get_context_data(self, **kwargs):

        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'], school=self.request.user.school)
        if self.request.method == "POST":
            return EnrollmentForm(self.request.POST, self.request.FILES, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
            return EnrollmentForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'], school=self.request.user.school)

        if self.request.FILES:
            if self.request.FILES['document_lastyear']:
                instance.document_lastyear = self.request.FILES['document_lastyear']
                instance.save()
        else:
            if instance.document_lastyear:
                v = instance.document_lastyear
                instance.document_lastyear = v
                instance.save()
        form.save(request=self.request, instance=instance)
        return super(EditView, self).form_valid(form)


class EditRegionView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'bootstrap4/common_form.html'
    form_class = EnrollmentRegionForm
    success_url = '/enrollments/student_by_regions/'
    group_required = [u"ENROL_EDIT"]

    def get_context_data(self, **kwargs):

        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditRegionView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return EnrollmentRegionForm(self.request.POST, self.request.FILES, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
            return EnrollmentRegionForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.FILES:
            if self.request.FILES['document_lastyear']:
                instance.document_lastyear = self.request.FILES['document_lastyear']
                instance.save()
        else:
            if instance.document_lastyear:
                v = instance.document_lastyear
                instance.document_lastyear = v
                instance.save()
        form.save(request=self.request, instance=instance)
        return super(EditRegionView, self).form_valid(form)


class EditOldDataView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = EditOldDataForm
    success_url = '/enrollments/list-old-data/'
    group_required = [u"ENROL_EDIT_OLD"]

    def get_context_data(self, **kwargs):

        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditOldDataView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'], school=self.request.user.school)
        if self.request.method == "POST":
            return EditOldDataForm(self.request.POST, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            return EditOldDataForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'], school=self.request.user.school)
        form.save(request=self.request, instance=instance)
        return super(EditOldDataView, self).form_valid(form)


class ListingOldDataView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         FilterView,
                         ExportMixin,
                         SingleTableView,
                         RequestConfig):

    table_class = EnrollmentOldDataTable
    model = Enrollment
    template_name = 'enrollments/list_old_data.html'
    table = BootstrapTable(Enrollment.objects.all(), order_by='id')
    filterset_class = EnrollmentOldDataFilter
    group_required = [u"ENROL_EDIT_OLD"]

    def get_queryset(self):

        education_year = EducationYear.objects.get(current_year=True)
        return Enrollment.objects.exclude(moved=True).filter(
            education_year__id__lt=education_year.id,
            school=self.request.user.school_id
        )

class ListingView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = EnrollmentTable
    model = Enrollment
    template_name = 'enrollments/list.html'
    table = BootstrapTable(Enrollment.objects.all(), order_by='id')
    filterset_class = EnrollmentFilter
    group_required = [u"SCHOOL"]

    def get_queryset(self):

        education_year = EducationYear.objects.get(current_year=True)
        return Enrollment.objects.exclude(moved=True).filter(
            education_year=education_year,
            school=self.request.user.school_id,
            dropout_status=False
        )

