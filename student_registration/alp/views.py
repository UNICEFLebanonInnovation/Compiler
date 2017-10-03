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

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(AddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(AddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', '0'),
            'student_outreached': self.request.GET.get('student_outreached', '1'),
            'have_barcode': self.request.GET.get('have_barcode', '1')
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
        queryset = self.model.objects.all()
        school = int(request.GET.get('school', 0))
        location = int(request.GET.get('location', 0))
        alp_round = ALPRound.objects.get(current_round=True)

        if has_group(self.request.user, 'PARTNER'):
            alp_round = ALPRound.objects.get(current_pre_test=True)
            queryset = queryset.filter(owner=self.request.user, alp_round=alp_round)
        if has_group(self.request.user, 'ALP_SCHOOL') and self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            queryset = queryset.filter(school_id=school, alp_round=alp_round).order_by('id')
        if location:
            queryset = queryset.filter(school__location_id=location, alp_round=alp_round).order_by('id')

        data = tablib.Dataset()

        data.headers = [
            _('ALP result'),
            _('ALP round'),
            _('ALP level'),
            _('Is the child participated in an ALP program'),

            _('Education year'),
            _('Last education level'),

            _('Phone prefix'),
            _('Phone number'),
            _('Student living address'),

            _('Student ID Number'),
            _('Student ID Type'),
            _('Registered in UNHCR'),

            _('Mother nationality'),
            _('Mother fullname'),

            _('Current Section'),
            _('Current Level'),

            _('Post-test result'),
            _('Assigned to level'),
            _('Pre-test result'),

            _('Student nationality'),
            _('Student age'),
            _('Student birthday'),
            _('Sex'),
            _('Student fullname'),

            _('School'),
            _('School number'),
            _('District'),
            _('Governorate'),
        ]

        content = []
        for line in queryset:
            if not line.student or not line.school:
                continue
            content = [
                line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
                line.last_informal_edu_round.name if line.last_informal_edu_round else '',
                line.last_informal_edu_level.name if line.last_informal_edu_level else '',
                _(line.participated_in_alp) if line.participated_in_alp else '',

                line.last_education_year,
                line.last_education_level.name if line.last_education_level else '',

                line.student.phone_prefix,
                line.student.phone,
                line.student.address,

                line.student.id_number,
                line.student.id_type.name if line.student.id_type else '',
                _(line.registered_in_unhcr) if line.registered_in_unhcr else '',

                line.student.mother_nationality.name if line.student.mother_nationality else '',
                line.student.mother_fullname,

                line.section.name if line.section else '',
                line.registered_in_level.name if line.registered_in_level else '',

                line.post_exam_total,
                line.assigned_to_level.name if line.assigned_to_level else '',
                line.exam_total,

                line.student.nationality_name(),
                line.student.age,
                line.student.birthday,
                _(line.student.sex),
                line.student.__unicode__(),

                line.school.name,
                line.school.number,
                line.school.location.name,
                line.school.location.parent.name,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=outreach_list.xls'
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
