# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from student_registration.users.templatetags.custom_tags import has_group
from rest_framework import viewsets, mixins, permissions

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from openpyxl import Workbook

from rest_framework import status
from django.db.models import F, Q
from django.core.urlresolvers import reverse
from django.shortcuts import render
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from fuzzywuzzy import fuzz

from django.views.decorators.http import require_POST

from .tables import (
    BootstrapTable,
    CenterTable

)
from .models import (
    Center,
    Location,
    ProgramStaff
)
from student_registration.schools.models import PartnerOrganization

from .forms import (
    CenterForm,
    ProgramStaffForm
)
from .serializers import (
    LocationSerializer,
    ProgramStaffSerializer
)
from .filters import (
    CenterFilter
)

from .utils import *

from dal import autocomplete


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Location.objects.none()

        qs = Location.objects.all()
        if self.q:
            qs = Location.objects.filter(
                Q(name__istartswith=self.q) | Q(p_code__istartswith=self.q)
            )
        return qs


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'location/center_profile.html'
    group_required = [u"MSCC"]

    def get_context_data(self, **kwargs):
        center_id = self.kwargs['pk']
        instance = Center.objects.get(id=center_id)
        program_staffs = ProgramStaff.objects.filter(center__id=center_id).order_by('facilitator_name')
        current_tab = self.request.GET.get('current_tab', 'info')

        return {
            'instance': instance,
            'program_staffs':program_staffs,
            'current_tab': current_tab
        }


class CenterFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name ='location/center_form.html'
    form_class = CenterForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return reverse('locations:center_profile', kwargs={'pk': pk})
        else:
            return reverse('mscc:list')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CenterFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return CenterForm(self.request.POST, pk=pk,  request=self.request)
        else:
            if pk:
                instance = Center.objects.get(id=pk)
                return CenterForm(instance=instance, pk=pk, request=self.request)
            return CenterForm( pk=pk, request=self.request)

    def form_valid(self, form):
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request,  instance=instance)
        return super(CenterFormView, self).form_valid(form)


class CenterListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = CenterTable
    model = Center
    template_name = 'location/center_list.html'
    table = BootstrapTable(Center.objects.all(), order_by='id')
    group_required = [u"MSCC", u"MSCC_PARTNER"]
    filterset_class = CenterFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id
        if has_group(user, 'MSCC_UNICEF'):
            return Center.objects.order_by('-id')
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            return Center.objects.filter(partner__id=partner_id).order_by('-id')
        elif has_group(user, 'MSCC_CENTER') and center_id:
            return Center.objects.filter(id=center_id).order_by('-id')

        return Center.objects.none()


class ProgramStaffFormView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           FormView):
    template_name = 'location/program_staff_form.html'
    form_class = ProgramStaffForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        center_id = self.kwargs.get('center_id')
        if center_id is not None:
            return reverse('locations:center_profile', kwargs={'pk': center_id})
        else:
            return reverse('mscc:list')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['center_id'] = self.kwargs['center_id']
        return super(ProgramStaffFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        center_id = int(self.kwargs.get('center_id'))
        pk = self.kwargs.get('pk', None)
        if self.request.method == "POST":
            return ProgramStaffForm(self.request.POST, pk=pk, center_id=center_id, request=self.request)
        else:
            if pk:
                instance = ProgramStaff.objects.get(id=pk)
                return ProgramStaffForm(instance=instance, pk=pk, center_id=center_id, request=self.request)
            return ProgramStaffForm(pk=pk, center_id=center_id, request=self.request)

    def form_valid(self, form):
        center_id = self.kwargs.get('center_id')
        instance = self.kwargs.get('pk', None)
        form.save(request=self.request, center_id=center_id, instance=instance)
        return super(ProgramStaffFormView, self).form_valid(form)


class ProgramStaffViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):

    model = ProgramStaff
    queryset = ProgramStaff.objects.all()
    serializer_class = ProgramStaffSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = self.queryset
        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


def program_staff_delete(request, pk):
    if request.user.is_authenticated:
        try:
            program_staff = ProgramStaff.objects.get(id=pk)
            program_staff.delete()
            result = {"isSuccessful": True}
        except ProgramStaff.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


###################### API VIEWS #############################

class LocationViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset


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
