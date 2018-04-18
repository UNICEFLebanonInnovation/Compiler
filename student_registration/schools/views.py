# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db.models import Q
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from dal import autocomplete
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin

from student_registration.backends.models import Notification
from student_registration.users.utils import force_default_language
from .models import (
    School,
    ClassRoom,
    Section,
    PublicDocument,
    PartnerOrganization,
)

from .serializers import (
    SchoolSerializer,
    ClassRoomSerializer,
    SectionSerializer,
)
from .forms import ProfileForm, PartnerForm


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
