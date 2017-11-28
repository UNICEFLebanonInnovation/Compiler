# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from rest_framework import viewsets, mixins, permissions
import tablib
from rest_framework import status
from django.utils.translation import ugettext as _
from django.db.models import Q
from import_export.formats import base_formats
from braces.views import GroupRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from .models import Outreach, ALPRound
from .forms import RegistrationForm, PreTestGradingForm, PostTestGradingForm, OutreachForm, PreTestForm
from .serializers import OutreachSerializer, GradingSerializer, OutreachSmallSerializer
from .tables import BootstrapTable, OutreachTable, PreTestTable, PostTestTable, SchoolTable
from .filters import OutreachFilter, PreTestFilter, PostTestFilter, SchoolFilter
from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer
from student_registration.users.utils import force_default_language
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    Student,
)
from student_registration.alp.templatetags.util_tags import has_group
from student_registration.backends.tasks import export_alp


class OutreachViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Outreach
    queryset = Outreach.objects.all()
    serializer_class = OutreachSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        terms = self.request.GET.get('term', 0)
        school = int(self.request.GET.get('school', 0))
        if self.request.user.school_id and terms:
            self.serializer_class = StudentSerializer
            alp_round = ALPRound.objects.get(current_round=True)
            qs = Student.objects.filter(
                alp_enrollment__isnull=False,
                alp_enrollment__deleted=False,
                alp_enrollment__dropout_status=False,
            )
            if school:
                qs = qs.filter(
                    alp_enrollment__school_id=self.request.user.school_id,
                    alp_enrollment__alp_round__lt=alp_round.id,
                )
            elif school == 0:
                pre_test_round = ALPRound.objects.get(current_pre_test=True)
                qs = qs.filter(
                    alp_enrollment__alp_round=pre_test_round.id,
                    alp_enrollment__school__in=self.request.user.schools.all(),
                ).exclude(
                    alp_enrollment__school_id=self.request.user.school_id,
                )
            for term in terms.split():
                qs = qs.filter(
                    Q(first_name__contains=term) |
                    Q(father_name__contains=term) |
                    Q(last_name__contains=term) |
                    Q(id_number__contains=term)
                ).distinct()
            return qs
        if self.request.GET.get('id', 0):
            return self.queryset.filter(id=self.request.GET.get('id', 0))
        if self.request.user.school_id:
            alp_round = ALPRound.objects.get(current_round=True)
            return self.queryset.filter(school_id=self.request.user.school_id, alp_round=alp_round)

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def perform_update(self, serializer):
        if has_group(self.request.user, 'CERD') and self.request.method != "PATCH":
            self.serializer_class = OutreachSmallSerializer
        instance = serializer.save()
        instance.save()

    def create(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD'):
            self.serializer_class = OutreachSmallSerializer
        return super(OutreachViewSet, self).create(request)

    def update(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD') and request.method != "PATCH":
            self.serializer_class = OutreachSmallSerializer
        return super(OutreachViewSet, self).update(request)

    def partial_update(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD'):
            self.serializer_class = GradingSerializer
        return super(OutreachViewSet, self).partial_update(request)


class AddView(LoginRequiredMixin,
              GroupRequiredMixin,
              FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = RegistrationForm
    success_url = '/alp/list/'
    group_required = [u"ALP_SCHOOL", u"ALP_DIRECTOR"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/alp/add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
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
            instance = Outreach.objects.get(id=self.request.GET.get('enrollment_id'))
            data = OutreachSerializer(instance).data
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

    def form_valid(self, form):
        form.save(request=self.request)
        return super(AddView, self).form_valid(form)


class EditView(LoginRequiredMixin,
               GroupRequiredMixin,
               FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = RegistrationForm
    success_url = '/alp/list/'
    group_required = [u"ALP_SCHOOL", u"ALP_DIRECTOR"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/alp/add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return RegistrationForm(self.request.POST, instance=instance)
        else:
            data = OutreachSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
            if instance.owner != self.request.user:
                data['new_registry'] = 'yes'
                data['student_outreached'] = 'no'
                data['have_barcode'] = 'no'
            return RegistrationForm(data, instance=instance)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(EditView, self).form_valid(form)


class SchoolView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FilterView,
                 ExportMixin,
                 SingleTableView,
                 RequestConfig):

    group_required = [u"ALP_SCHOOL", u"ALP_DIRECTOR"]
    table_class = SchoolTable
    model = Outreach
    template_name = 'alp/list.html'
    table = BootstrapTable(Outreach.objects.all(), order_by='id')

    filterset_class = SchoolFilter

    def get_queryset(self):
        force_default_language(self.request)
        alp_round = ALPRound.objects.get(current_round=True)
        return Outreach.objects.filter(alp_round=alp_round, school=self.request.user.school_id)


class PreTestView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    group_required = [u"TEST_MANAGER", u"CERD"]
    table_class = PreTestTable
    model = Outreach
    template_name = 'alp/pre_test.html'
    table = BootstrapTable(Outreach.objects.all(), order_by='id')

    filterset_class = PreTestFilter

    def get_queryset(self):
        force_default_language(self.request)
        alp_round = ALPRound.objects.get(current_pre_test=True)
        return Outreach.objects.filter(alp_round=alp_round)


class PreTestAddView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = PreTestForm
    success_url = '/alp/pre-test/'
    group_required = [u"TEST_MANAGER", u"CERD"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/alp/pre-test-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(PreTestAddView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.save(request=self.request)
        return super(PreTestAddView, self).form_valid(form)


class PreTestEditView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = PreTestForm
    success_url = '/alp/pre-test/'
    group_required = [u"TEST_MANAGER", u"CERD"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(PreTestEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return PreTestForm(self.request.POST, instance=instance)
        else:
            data = OutreachSmallSerializer(instance).data
            return PreTestForm(data, instance=instance)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(PreTestEditView, self).form_valid(form)


class PreTestGradingView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         FormView):

    template_name = 'alp/test_grading.html'
    form_class = PreTestGradingForm
    success_url = '/alp/pre-test/'
    group_required = [u"TEST_MANAGER", u"CERD"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(PreTestGradingView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return PreTestGradingForm(self.request.POST, instance=instance)
        else:
            data = GradingSerializer(instance).data
            return PreTestGradingForm(data, instance=instance)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(PreTestGradingView, self).form_valid(form)


class PostTestView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    group_required = [u"TEST_MANAGER", u"CERD"]
    table_class = PostTestTable
    model = Outreach
    template_name = 'alp/post_test.html'
    table = BootstrapTable(Outreach.objects.all(), order_by='id')

    filterset_class = PostTestFilter

    def get_queryset(self):
        force_default_language(self.request)
        alp_round = ALPRound.objects.get(current_post_test=True)
        return Outreach.objects.filter(alp_round=alp_round, registered_in_level__isnull=False)


class PostTestGradingView(LoginRequiredMixin,
                          GroupRequiredMixin,
                          FormView):

    template_name = 'alp/test_grading.html'
    form_class = PostTestGradingForm
    success_url = '/alp/post-test/'
    group_required = [u"TEST_MANAGER", u"CERD"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(PostTestGradingView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return PostTestGradingForm(self.request.POST, instance=instance)
        else:
            data = GradingSerializer(instance).data
            return PostTestGradingForm(data, instance=instance)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(PostTestGradingView, self).form_valid(form)


class OutreachView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    group_required = [u"PARTNER"]
    table_class = OutreachTable
    model = Outreach
    template_name = 'alp/outreach.html'
    table = BootstrapTable(Outreach.objects.all(), order_by='id')

    filterset_class = OutreachFilter

    def get_queryset(self):
        force_default_language(self.request)
        alp_round = ALPRound.objects.get(current_pre_test=True)
        return Outreach.objects.filter(alp_round=alp_round, owner=self.request.user)


class OutreachAddView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = OutreachForm
    success_url = '/alp/outreach/'
    group_required = [u"PARTNER"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/alp/outreach-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(OutreachAddView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.save(request=self.request)
        return super(OutreachAddView, self).form_valid(form)


class OutreachEditView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = OutreachForm
    success_url = '/alp/outreach/'
    group_required = [u"PARTNER"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/alp/outreach-add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(OutreachEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return OutreachForm(self.request.POST, instance=instance)
        else:
            data = OutreachSmallSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
            return OutreachForm(data, instance=instance)

    def form_valid(self, form):
        instance = Outreach.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(OutreachEditView, self).form_valid(form)


class ExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        data = ''
        school = int(request.GET.get('school', 0))
        current_type = request.GET.get('current_type', 'current')

        if has_group(self.request.user, 'PARTNER'):
            data = export_alp({'pre_test': 'true'})
        if has_group(self.request.user, 'ALP_SCHOOL') and self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            data = export_alp({current_type: 'true', 'school': school}, return_data=True)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xlsx'
        return response


class ExportBySchoolView(LoginRequiredMixin, ListView):

    model = Outreach
    queryset = Outreach.objects.all()

    def get(self, request, *args, **kwargs):

        alp_round = ALPRound.objects.get(current_pre_test=True)

        schools = self.queryset.filter(alp_round=alp_round, registered_in_level__isnull=False).values_list(
                        'school', 'school__number', 'school__name', 'school__location__name',
                        'school__location__parent__name', 'school__number_students_alp',).distinct().order_by('school__number')

        data = tablib.Dataset()
        data.headers = [
            _('CERD'),
            _('School name'),
            _('# Students registered in the Compiler'),
            _('# Students reported by the Director'),
            _('District'),
            _('Governorate'),
        ]

        content = []
        for school in schools:
            nbr = self.model.objects.filter(school=school[0], alp_round=alp_round, registered_in_level__isnull=False).count()
            content = [
                school[1],
                school[2],
                nbr,
                school[5],
                school[3],
                school[4]
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=student_by_school.xls'
        return response
