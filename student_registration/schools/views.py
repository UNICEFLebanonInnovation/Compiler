# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db.models import Q
from django.views.generic import DetailView, ListView, RedirectView, CreateView, FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from dal import autocomplete
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
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
    Location,
    Club,
    Meeting,
    CommunityInitiative,
    HealthVisit
)

from .serializers import (
    SchoolSerializer,
    ClassRoomSerializer,
    SectionSerializer
)
from .tables import (
    BootstrapTable,
    SchoolTable,
    ClubTable,
    MeetingTable,
    CommunityInitiativeTable,
    HealthVisitTable

)
from .filters import (
    SchoolFilter
)
from .forms import ProfileForm,SchoolForm, ClubForm, MeetingForm, CommunityInitiativeForm , HealthVisitForm,  \
    PartnerForm, EvaluationForm,Classroom_Form, Classroom_Form_c1, Classroom_Form_c3,\
    Classroom_Form_c4, Classroom_Form_c5, Classroom_Form_c6, Classroom_Form_c7, Classroom_Form_c8, \
    Classroom_Form_c9, Classroom_Form_cprep
from .utils import *

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


def load_districts(request):
    cities = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    cities = []
    if request.GET.get('id_district'):
        id_district = request.GET.get('id_district')
        cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    schools = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})


class SchoolListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):
    table_class = SchoolTable
    model = School
    template_name = 'schools/school_list.html'
    table = BootstrapTable(School.objects.all(), order_by='id')
    group_required = [u"CLM_Bridging"]
    filterset_class = SchoolFilter

    def get_queryset(self):
        force_default_language(self.request)

        clm_bridging_all = self.request.user.groups.filter(name='CLM_BRIDGING_ALL').exists()
        is_staff = self.request.user.is_staff

        queryset = School.objects.filter(is_first_shift='yes').all()

        if not clm_bridging_all and not is_staff and self.request.user.partner:
            school_id = 0
            if self.request.user.school:
                school_id = self.request.user.school.id
            partner_id = self.request.user.partner_id

            if school_id and school_id > 0:
                queryset = School.objects.filter(id=school_id)

            elif partner_id > 0:
                queryset = School.objects.filter(is_first_shift='yes',
                                                 id__in=PartnerOrganization
                                                 .objects
                                                 .filter(id=partner_id)
                                                 .values_list('schools', flat=True))
            else:
                queryset =queryset.none()

        return queryset


class SchoolAddView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):
    template_name = 'schools/school_create_form.html'
    form_class = SchoolForm
    success_url = '/schools/school-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/school-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/school-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('Bridging')
        return super(SchoolAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(SchoolAddView, self).get_initial()
        data = {
            'new_school': self.request.GET.get('new_school', ''),
        }
        if self.request.GET.get('school_id'):
            instance = School.objects.get(id=self.request.GET.get('school_id'))
            data = SchoolSerializer(instance).data

        if data:
            data['new_school'] = self.request.GET.get('new_school', 'yes')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(SchoolAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return SchoolForm(self.request.POST, instance=None, request=self.request)
        else:
            return SchoolForm(None, instance=None, request=self.request, initial=self.get_initial())


class SchoolEditView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'schools/school_edit_form.html'
    form_class = SchoolForm
    success_url = '/schools/school-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/school-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/school-edit/' + str(self.request.session.get('instance_id')) + '/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('Bridging')
        return super(SchoolEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = School.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return SchoolForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = SchoolSerializer(instance).data
            return SchoolForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = School.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(SchoolEditView, self).form_valid(form)


class ClubListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = ClubTable
    model = Club
    template_name = 'schools/club_list.html'
    table = BootstrapTable(Club.objects.all(), order_by='id')
    group_required = [u"CLM_Bridging"]

    def get_queryset(self):
        force_default_language(self.request)
        school_id = int(self.kwargs['school_id'])
        return Club.objects.filter(school_id=school_id).order_by('-id')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs['school_id'] = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(ClubListView, self).get_context_data(**kwargs)


class ClubFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'schools/club_form.html'
    form_class = ClubForm
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return '/schools/club-list/' + school_id

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['school_id']  = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(ClubFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return ClubForm(self.request.POST, pk=pk, school_id=school_id, request=self.request)
        else:
            if pk:
                instance = Club.objects.get(id=pk)

                return ClubForm(instance=instance, school_id=school_id, pk=pk, request=self.request)
            return ClubForm(school_id=school_id, pk=pk, request=self.request)

    def form_valid(self, form):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, school_id=school_id, instance=instance)
        return super(ClubFormView, self).form_valid(form)


class MeetingListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = MeetingTable
    model = Meeting
    template_name = 'schools/meeting_list.html'
    table = BootstrapTable(Meeting.objects.all(), order_by='id')
    group_required = [u"CLM_Bridging"]

    def get_queryset(self):
        force_default_language(self.request)
        school_id = int(self.kwargs['school_id'])
        return Meeting.objects.filter(school_id=school_id).order_by('-id')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs['school_id'] = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(MeetingListView, self).get_context_data(**kwargs)


class MeetingFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'schools/meeting_form.html'
    form_class = MeetingForm
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return '/schools/meeting-list/' + school_id

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['school_id']  = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(MeetingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return MeetingForm(self.request.POST, pk=pk, school_id=school_id, request=self.request)
        else:
            if pk:
                instance = Meeting.objects.get(id=pk)

                return MeetingForm(instance=instance, school_id=school_id, pk=pk, request=self.request)
            return MeetingForm(school_id=school_id, pk=pk, request=self.request)

    def form_valid(self, form):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, school_id=school_id, instance=instance)
        return super(MeetingFormView, self).form_valid(form)


class CommunityInitiativeListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = CommunityInitiativeTable
    model = CommunityInitiative
    template_name = 'schools/community_initiative_list.html'
    table = BootstrapTable(CommunityInitiative.objects.all(), order_by='id')
    group_required = [u"CLM_Bridging"]

    def get_queryset(self):
        force_default_language(self.request)
        school_id = int(self.kwargs['school_id'])
        return CommunityInitiative.objects.filter(school_id=school_id).order_by('-id')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs['school_id'] = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(CommunityInitiativeListView, self).get_context_data(**kwargs)


class CommunityInitiativeFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'schools/community_initiative_form.html'
    form_class = CommunityInitiativeForm
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return '/schools/community-initiative-list/' + school_id

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['school_id']  = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(CommunityInitiativeFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return CommunityInitiativeForm(self.request.POST, pk=pk, school_id=school_id, request=self.request)
        else:
            if pk:
                instance = CommunityInitiative.objects.get(id=pk)

                return CommunityInitiativeForm(instance=instance, school_id=school_id, pk=pk, request=self.request)
            return CommunityInitiativeForm(school_id=school_id, pk=pk, request=self.request)

    def form_valid(self, form):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, school_id=school_id, instance=instance)
        return super(CommunityInitiativeFormView, self).form_valid(form)





class HealthVisitListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = HealthVisitTable
    model = HealthVisit
    template_name = 'schools/health_visit_list.html'
    table = BootstrapTable(HealthVisit.objects.all(), order_by='id')
    group_required = [u"CLM_Bridging"]

    def get_queryset(self):
        force_default_language(self.request)
        school_id = int(self.kwargs['school_id'])
        return HealthVisit.objects.filter(school_id=school_id).order_by('-id')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs['school_id'] = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(HealthVisitListView, self).get_context_data(**kwargs)


class HealthVisitFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'schools/health_visit_form.html'
    form_class = HealthVisitForm
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return '/schools/health-visit-list/' + school_id

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['school_id']  = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        return super(HealthVisitFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return HealthVisitForm(self.request.POST, pk=pk, school_id=school_id, request=self.request)
        else:
            if pk:
                instance = HealthVisit.objects.get(id=pk)

                return HealthVisitForm(instance=instance, school_id=school_id, pk=pk, request=self.request)
            return HealthVisitForm(school_id=school_id, pk=pk, request=self.request)

    def form_valid(self, form):
        school_id = self.kwargs['school_id'] if 'school_id' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, school_id=school_id, instance=instance)
        return super(HealthVisitFormView, self).form_valid(form)


def school_export_data(request):
    qs_school = School.objects.filter(is_first_shift='yes').order_by('-id')
    qs_school.order_by('-id')
    dataset = SchoolResource().export(qs_school)
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="school_data.xls"'
    return response



class school_export_data(LoginRequiredMixin, ListView):
    qs_school = School.objects.filter(is_first_shift='yes').order_by('-id')
    qs_club = Club.objects.all().order_by('-id')
    qs_meeting = Meeting.objects.all().order_by('-id')
    qs_community_initiative = CommunityInitiative.objects.all().order_by('-id')
    qs_health_visit = HealthVisit.objects.all().order_by('-id')


    def get(self, request, *args, **kwargs):
        return school_build_xls_extraction(self.qs_school, self.qs_club, self.qs_meeting, self.qs_community_initiative, self.qs_health_visit)


class SchoolAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return School.objects.none()

        qs = School.objects.all()

        if self.q:
            qs = School.objects.filter(
                Q(number__istartswith=self.q) | Q(name__istartswith=self.q)
            )

        return qs
