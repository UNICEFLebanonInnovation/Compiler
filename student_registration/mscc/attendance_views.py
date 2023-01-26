# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, CreateView, View
from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from rest_framework import status
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin


from .tables import (
    BootstrapTable,
    MainTable,
)
from .models import Registration
from  student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild

from .attendance_forms import (
    MainAttendanceForm,
    ChildAttendanceForm
)

from .utils import *


class MainAttendanceCreateView(LoginRequiredMixin, CreateView):
    form_class = MainAttendanceForm
    template_name = 'mscc/attendance_main.html'
    group_required = [u"MSCC_ATTENDANCE"]

    def get_initial_child_formset(self, initial_records):
        attendance_child_inline_formset = inlineformset_factory(
            MSCCAttendance,
            MSCCAttendanceChild,
            form=ChildAttendanceForm,
            extra=len(initial_records),
            fk_name='attendance_day',
            fields=('attended', 'absence_reason','absence_reason', 'child_id'),
            can_delete=False
        )
        return attendance_child_inline_formset(initial=initial_records)

    def get_child_formset(self, parameters):
        attendance_child_inline_formset = inlineformset_factory(
            MSCCAttendance,
            MSCCAttendanceChild,
            form=ChildAttendanceForm,
            fk_name='attendance_day',
            fields=('attended', 'absence_reason', 'absence_reason',  'child_id'),
            can_delete=False
        )
        return attendance_child_inline_formset(parameters)

    def get_form_kwargs(self):
        kwargs = super(MainAttendanceCreateView, self).get_form_kwargs()
        if self.request.method == 'POST':
            kwargs['attendance_child_formset'] = self.get_child_formset(self.request.POST)
        else:
            queryset = Bridging.objects.none()
            load_students = self.request.GET.get('load_students', None)
            if load_students =='yes':
                queryset = Registration.objects.filter(center_id=self.request.user.center.id)
                queryset = queryset.order_by('-id')
            data = []
            for line in queryset:
                child = {
                    'child_id': line.child.id,
                    'child_name': line.child.full_name
                }
                data.append(child)
            kwargs['attendance_child_formset'] = self.get_initial_child_formset(data)

        if ('load_students' in self.request.GET)  \
            or \
            self.request.method == 'POST':
            kwargs['saveStage'] = True
        else:
            kwargs['saveStage'] = False
        return kwargs


        # if self.request.method == 'POST':
        #     kwargs['saveStage'] = True
        # else:
        #     kwargs['saveStage'] = False
        # return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        attendance_child_formset = self.get_child_formset(self.request.POST)
        child_count = len(attendance_child_formset)
        if self.request.POST['day_off'] == 'yes' and child_count > 0:
            form.add_error('day_off', 'Day is off')

        if form.is_valid() and attendance_child_formset.is_valid():
            return self.form_valid(form, attendance_child_formset)
        else:
            return self.form_invalid(form, attendance_child_formset)

    def get(self, request, *args, **kwargs):
        attendance_date = self.request.GET.get('attendance_date', '')

        attendance = None
        center_id = self.request.user.center.id
        if attendance_date != '':
            attendance = MSCCAttendance.objects.filter(center_id=center_id,
                                                       attendance_date=attendance_date,
                                                       ).values('id').first()
        if attendance:
            attendance_id = attendance['id']
            return redirect(reverse('mscc:attendance_main_edit', kwargs={'pk': attendance_id}))
        else:
            return super(MainAttendanceCreateView, self).get(request)

    def form_valid(self, form, attendance_child_formset):
        self.object = form.save(commit=False)
        self.object.save()
        # saving ProductMeta Instances
        for child_form in attendance_child_formset:
            child_form.instance.child_id = child_form.cleaned_data['child_id']
        attendance_children = attendance_child_formset.save(commit=False)
        for attendance_child in attendance_children:
            attendance_child.attendance_day = self.object
            attendance_child.save()
        messages.success(self.request, 'The attendance information was saved')
        return super(MainAttendanceCreateView, self).form_valid(form)

    def form_invalid(self, form, attendance_child_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  attendance_child_formset=attendance_child_formset
                                  )
        )

    def get_initial(self):
        initial_values = {}
        if self.request.GET.get('attendance_date', None):
            initial_values['attendance_date'] = self.request.GET.get('attendance_date', 0)
        if self.request.GET.get('day_off', None):
            initial_values['day_off'] = self.request.GET.get('day_off', '')
        return initial_values

    def get_success_message(self):
        return "The attendance information was saved"

    def get_success_url(self):
        return reverse('mscc:attendance_main')


class MainAttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MSCCAttendance
    form_class = MainAttendanceForm
    template_name = 'mscc/attendance_main.html'
    group_required = [u"MSCC_ATTENDANCE"]

    def get_success_url(self):
        return reverse('mscc:attendance_main_edit', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainAttendanceUpdateView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        attendance_id = self.kwargs['pk']
        instance = MSCCAttendance.objects.get(id=attendance_id)
        update_disabled = True
        # center_id = self.request.user.center.id
        messages.success(self.request, 'There is already an attendance record for this date.')
        if self.request.method == "POST":
            instance.save()
            form = MainAttendanceForm(self.request.POST, instance=instance,
                                      attendance_child_formset=self.get_child_formset(self.request.POST)
                                      , saveStage=True, update_disabled=update_disabled)
        else:
            form = MainAttendanceForm(instance=instance,
                                      attendance_child_formset=self.get_formset(attendance_id),
                                      saveStage=True, update_disabled=update_disabled)

        form.helper.form_action = reverse('mscc:attendance_main_edit', args=[attendance_id])

        return form

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        attendance_child_formset = self.get_child_formset(self.request.POST)
        child_count = len(attendance_child_formset)
        if self.request.POST['day_off'] == 'yes' and child_count > 0:
            form.add_error('day_off', 'Day is off')

        if form.is_valid() and attendance_child_formset.is_valid():
            return self.form_valid(form, attendance_child_formset)
        else:
            return self.form_invalid(form, attendance_child_formset)

    def form_valid(self, form, attendance_child_formset):
        self.object = form.save(commit=False)
        self.object.save()

        for child_form in attendance_child_formset:
            child_form.instance.id = child_form.cleaned_data['id'].id
            child_form.instance.child_id = child_form.cleaned_data['child_id']

        attendance_children = attendance_child_formset.save(commit=False)
        for attendance_child in attendance_children:
            attendance_child.attendance_day = self.object
            attendance_child.save()
        messages.success(self.request, 'The attendance information was saved')
        return super(MainAttendanceUpdateView, self).form_valid(form)

    def form_invalid(self, form, attendance_child_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  attendance_child_formset=attendance_child_formset
                                  )
        )

    def get_formset(self, attendance_id):
        queryset = MSCCAttendanceChild.objects.filter(attendance_day__id=attendance_id)
        queryset = queryset.order_by('-id')

        data = []
        for line in queryset:
            child = {
                'id': line.id,
                'child_id': line.child.id,
                'child_name': line.child.full_name,
                'attended': line.attended,
                'absence_reason': line.absence_reason,
                'absence_reason': line.absence_reason_other
            }
            data.append(child)
        return self.get_initial_child_formset(data)

    def get_initial_child_formset(self, initial_records):
        attendance_child_inline_formset = inlineformset_factory(
            MSCCAttendance,
            MSCCAttendanceChild,
            form=ChildAttendanceForm,
            extra=len(initial_records),
            fk_name='attendance_day',
            fields=('id', 'attended', 'absence_reason', 'absence_reason_other', 'child_id'),
            can_delete=False
        )
        return attendance_child_inline_formset(initial=initial_records)

    def get_child_formset(self, parameters):
        attendance_child_inline_formset = inlineformset_factory(
            MSCCAttendance,
            MSCCAttendanceChild,
            form=ChildAttendanceForm,
            fk_name='attendance_day',
            fields=('id', 'attended', 'absence_reason', 'absence_reason_other', 'child_id'),
            can_delete=False
        )
        return attendance_child_inline_formset(parameters)


class ChildAttendanceView(FormView):
    template_name = 'mscc/attendance_children.html'
    form_class = ChildAttendanceForm

    def form_valid(self, form):
        return super(ChildAttendanceView, self).form_valid(form)

