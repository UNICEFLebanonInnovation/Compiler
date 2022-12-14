# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.users.utils import force_default_language
from student_registration.outreach.models import OutreachChild
from student_registration.child.models import Child
from student_registration.outreach.serializers import ChildSerializer
from .filters import (
    MainFilter
)
from .tables import (
    BootstrapTable,
    MainTable,
)
from .models import (
    Registration,
)

from .forms import (
    MainForm,
)
from .serializers import (
    MainSerializer
)


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'mscc/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])

        return {
            'instance': instance,
        }


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/create_form.html'
    form_class = MainForm
    success_url = '/MSCC/List/'
    group_required = [u"MSCC"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/mscc/add-child/'
        if self.request.POST.get('save_and_continue', None):
            return '/mscc/edit-child/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(MainAddView, self).get_initial()
        data = {
            'student_outreached': self.request.GET.get('student_outreached', ''),
        }
        if self.request.GET.get('registration_id'):
            instance = Registration.objects.get(id=self.request.GET.get('registration_id'))
            data = MainSerializer(instance).data
            data['child_nationality'] = data['child_nationality_id']
            data['learning_result'] = ''

        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data

        if self.request.GET.get('outreach_id'):
            instance = Child.objects.get(id=self.request.GET.get('outreach_id'))
            data = MainSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['learning_result'] = ''

        if data:
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
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
    template_name = 'mscc/edit_form.html'
    form_class = MainForm
    success_url = '/MSCC/List/'
    group_required = [u"MSCC"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/mscc/add-child/'
        if self.request.POST.get('save_and_continue', None):
            return '/mscc/edit-child/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

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
            data['child_nationality'] = data['child_nationality_id']
            data['child_disability'] = data['child_disability_id']
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']
            data['father_educational_level'] = data['father_educational_level_id']
            data['mother_educational_level'] = data['mother_educational_level_id']
            data['id_type'] = data['id_type_id']
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)


class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = MainTable
    model = Registration
    template_name = 'mscc/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u"MSCC"]

    filterset_class = MainFilter

    def get_queryset(self):
        force_default_language(self.request)
        return Registration.objects.all().order_by('-id')

        # return Registration.objects.filter(partner=self.request.user.partner_id).order_by('-id')



# ####################### API VIEWS #############################

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
