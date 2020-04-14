# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db.models import Q
from django.views.generic import DetailView, ListView, RedirectView, CreateView, FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from dal import autocomplete
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin
from django.contrib import admin
from student_registration.backends.models import Notification
from student_registration.users.utils import force_default_language
from .models import (
    EducationYear,
    School,
    ClassRoom,
    Section,
    PublicDocument,
    PartnerOrganization,
    Evaluation,
)

from .serializers import (
    SchoolSerializer,
    ClassRoomSerializer,
    SectionSerializer,
)
from .forms import ProfileForm, PartnerForm, EvaluationForm,Classroom_Form, Classroom_Form_c1, Classroom_Form_c3,\
    Classroom_Form_c4, Classroom_Form_c5, Classroom_Form_c6, Classroom_Form_c7, Classroom_Form_c8, \
    Classroom_Form_c9, Classroom_Form_cprep
from django.forms import modelformset_factory, formset_factory, inlineformset_factory, forms
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages


class SchoolViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    model = School
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ClassRoomViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):

    model = ClassRoom
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SectionViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):

    model = Section
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProfileView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):

    template_name = 'schools/profile.html'
    form_class = ProfileForm
    success_url = '/schools/profile/'
    group_required = [u"SCHOOL", u"ALP_SCHOOL"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            school = self.request.user.school

            notifications = Notification.objects.filter(type='general', schools=school)

            if school.is_2nd_shift and not school.is_alp:
                notifications = notifications.filter(school_type='2ndshift')
            if school.is_alp and not school.is_2nd_shift:
                notifications = notifications.filter(school_type='ALP')

            kwargs['notifications'] = notifications[:50]
            kwargs['unread_notifications'] = notifications.filter(status=False).count()
            tickets = Notification.objects.filter(
                type='helpdesk',
                school_id=school.id
            )
            kwargs['tickets'] = tickets[:50]
            kwargs['unread_tickets'] = tickets.filter(status=False).count()
        return super(ProfileView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = School.objects.get(id=self.request.user.school_id)
        if self.request.method == "POST":
            return ProfileForm(self.request.POST, instance=instance)
        else:
            return ProfileForm(instance=instance)

    def form_valid(self, form):
        instance = School.objects.get(id=self.request.user.school_id)
        form.save(request=self.request, instance=instance)
        return super(ProfileView, self).form_valid(form)


class PartnerView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):

    template_name = 'schools/partner.html'
    form_class = PartnerForm
    success_url = '/schools/partner/'
    group_required = [u"CLM"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(PartnerView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = PartnerOrganization.objects.get(id=self.request.user.partner_id)
        if self.request.method == "POST":
            return PartnerForm(self.request.POST, instance=instance)
        else:
            return PartnerForm(instance=instance)

    def form_valid(self, form):
        instance = PartnerOrganization.objects.get(id=self.request.user.partner_id)
        form.save(request=self.request, instance=instance)
        return super(PartnerView, self).form_valid(form)


class PublicDocumentView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         TemplateView):

    model = PublicDocument
    queryset = PublicDocument.objects.all()
    template_name = 'schools/documents.html'
    group_required = [u"SCHOOL", u"ALP_SCHOOL"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        return {
            'documents': self.queryset
        }


class AutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return School.objects.none()

        qs = School.objects.all()

        if self.q:
            qs = School.objects.filter(
                Q(name__istartswith=self.q) | Q(number__istartswith=self.q)
            )

        return qs


class EvaluationView(FormView):
    template_name = 'schools/evaluation.html'
    form_class = EvaluationForm
    success_url = '/schools/evaluation/'

    def get_form(self, form_class=None):
        education_year = EducationYear.objects.get(current_year=True)
        if self.request:
            if self.request.user:
                if self.request.user.school_id:
                    evaluation = Evaluation.objects.filter(school_id=self.request.user.school_id, education_year=education_year)
                    instance = Evaluation.objects.get(id=evaluation)

        if self.request.method == "POST":
            return EvaluationForm(self.request.POST, instance=instance)
        else:
            return EvaluationForm(instance=instance)

    def form_valid(self, form):
        education_year = EducationYear.objects.get(current_year=True)
        instance = Evaluation.objects.get(school_id=self.request.user.school_id, education_year=education_year)
        form.save(request=self.request, instance=instance)
        return super(EvaluationView, self).form_valid(form)


class Update_Class(UpdateView):
    model = Evaluation
    form_class = Classroom_Form

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form(self.request.POST, instance=instance)
        else:
            return Classroom_Form(instance=instance)


class Update_Class_c1(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c1

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c1, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c1(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c1(instance=instance)


class Update_Class_C3(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c3

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_C3, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c3(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c3(instance=instance)


class Update_Class_c4(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c4

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c4, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c4(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c4(instance=instance)


class Update_Class_c5(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c5

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c5, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c5(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c5(instance=instance)


class Update_Class_c6(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c6

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c6, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c6(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c6(instance=instance)


class Update_Class_c7(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c7

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c7, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c7(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c7(instance=instance)


class Update_Class_c8(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c8

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c8, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c8(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c8(instance=instance)


class Update_Class_c9(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_c9

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_c9, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_c9(self.request.POST, instance=instance)
        else:
            return Classroom_Form_c9(instance=instance)


class Update_Class_cprep(UpdateView):
    model = Evaluation
    form_class = Classroom_Form_cprep

    template_name = 'schools/classform.html'
    success_url = '/schools/evaluation/'
    context_object_name = 'school_class'

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(Update_Class_cprep, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Evaluation.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            instance.save()
            return Classroom_Form_cprep(self.request.POST, instance=instance)
        else:
            return Classroom_Form_cprep(instance=instance)
