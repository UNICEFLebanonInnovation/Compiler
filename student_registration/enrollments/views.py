# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import tablib

from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.db.models import Q

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from import_export.formats import base_formats

from student_registration.alp.templatetags.util_tags import has_group

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
    EnrollmentGrading,
    LoggingStudentMove,
    EducationYear,
    LoggingProgramMove,
)
from .forms import (
    EnrollmentForm,
    GradingTermForm,
    GradingIncompleteForm,
    StudentMovedForm,
    EditOldDataForm
)
from .serializers import (
    EnrollmentSerializer,
    EnrollmentImportSerializer,
    LoggingStudentMoveSerializer,
    LoggingProgramMoveSerializer
)
from student_registration.users.utils import force_default_language
from student_registration.backends.tasks import export_2ndshift, export_2ndshift_gradings


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
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return EnrollmentForm(self.request.POST, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
            return EnrollmentForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(EditView, self).form_valid(form)


class EditOldDataView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = EditOldDataForm
    success_url = '/enrollments/list-old-data/'
    group_required = [u"ENROL_EDIT_OLD"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EditOldDataView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return EditOldDataForm(self.request.POST, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            return EditOldDataForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
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
        force_default_language(self.request)
        education_year = EducationYear.objects.get(current_year=True)
        return Enrollment.objects.exclude(moved=True).filter(
            education_year__id__lt=education_year.id,
            school=self.request.user.school_id
        )


class MovedView(LoginRequiredMixin,
                GroupRequiredMixin,
                FormView):

    template_name = 'enrollments/moved.html'
    form_class = StudentMovedForm
    success_url = '/enrollments/list/'
    group_required = [u"SCHOOL"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MovedView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return StudentMovedForm(self.request.POST, instance=instance, moved=self.kwargs['moved'])
        else:
            return StudentMovedForm(instance=instance, moved=self.kwargs['moved'])

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        moved = LoggingStudentMove.objects.get(id=self.kwargs['moved'])
        moved.school_to = self.request.user.school
        moved.save()
        form.save(request=self.request, instance=instance)
        return super(MovedView, self).form_valid(form)


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
        force_default_language(self.request)
        education_year = EducationYear.objects.get(current_year=True)
        return Enrollment.objects.exclude(moved=True).filter(
            education_year=education_year,
            school=self.request.user.school_id
        )


class GradingView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):

    template_name = 'enrollments/grading.html'
    form_class = GradingTermForm
    success_url = '/enrollments/list/'
    group_required = [u"ENROL_GRADING"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(GradingView, self).get_context_data(**kwargs)

    def get_form_class(self):
        if int(self.kwargs['term']) == 4:
            return GradingIncompleteForm
        return GradingTermForm

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = EnrollmentGrading.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = EnrollmentGrading.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(GradingView, self).form_valid(form)


####################### API VIEWS #############################


class LoggingProgramMoveViewSet(mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                viewsets.GenericViewSet):

    model = LoggingProgramMove
    queryset = LoggingProgramMove.objects.all()
    serializer_class = LoggingProgramMoveSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LoggingStudentMoveViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):

    model = LoggingStudentMove
    queryset = LoggingStudentMove.objects.all()
    serializer_class = LoggingStudentMoveSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        terms = self.request.GET.get('term', 0)
        current_year = EducationYear.objects.get(current_year=True)
        if terms:
            qs = self.queryset.filter(
                school_to__isnull=True,
                education_year=current_year
            ).exclude(enrolment__dropout_status=True)
            for term in terms.split():
                qs = qs.filter(
                    Q(student__first_name__contains=term) |
                    Q(student__father_name__contains=term) |
                    Q(student__last_name__contains=term) |
                    Q(student__id_number__contains=term)
                )
            return qs
        return self.queryset

    def post(self, request, *args, **kwargs):
        if request.POST.get('moved', 0):
            enrollment = Enrollment.objects.get(id=request.POST.get('moved', 0))
            moved_date = request.POST.get('moved_date', 0)
            current_year = EducationYear.objects.get(current_year=True)
            enrollment.moved = True
            enrollment.last_moved_date = moved_date
            enrollment.save()
            LoggingStudentMove.objects.get_or_create(
                enrolment_id=enrollment.id,
                student_id=enrollment.student_id,
                school_from_id=enrollment.school_id,
                education_year=current_year,
                moved_date=moved_date
            )
        return JsonResponse({'status': status.HTTP_200_OK})


class EnrollmentViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    Provides API operations around a Enrollment record
    """
    model = Enrollment
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.GET.get('moved', 0):
            return self.queryset
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        if self.request.user.school_id:
            return self.queryset.filter(school_id=self.request.user.school_id).order_by('classroom_id', 'section_id')

        return self.queryset

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        if request.POST.get('moved', 0):
            moved = LoggingStudentMove.objects.get(id=request.POST.get('moved', 0))
            moved.school_to_id = request.POST.get('school')
            moved.save()
            enrollment = moved.enrolment
            enrollment.moved = False
            enrollment.save()
        self.serializer_class = EnrollmentSerializer
        return super(EnrollmentViewSet, self).partial_update(request)


class EnrollmentImportViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet,
                              SuperuserRequiredMixin):
    """
    Provides API importation Enrollment records
    """
    model = Enrollment
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentImportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        max_raw = int(self.request.GET.get('max', 500))
        if self.request.GET.get('year', 0):
            queryset = queryset.filter(education_year=int(self.request.GET.get('year', 0)))
        if self.request.GET.get('offset', 0):
            offset = int(self.request.GET.get('offset', 0))
            limit = offset + max_raw
            return queryset[offset:limit]
        return []


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(owner=self.request.user)
        return self.queryset

    def get(self, request, *args, **kwargs):
        data = ''
        school = request.GET.get('school', 0)
        classroom = request.GET.get('classroom', 0)
        section = request.GET.get('section', 0)

        if self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            data = export_2ndshift({
                'current': 'true',
                'school': school,
                'classroom': classroom,
                'section': section
            }, return_data=True)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xlsx'
        return response


class ExportGradingViewSet(LoginRequiredMixin, ListView):

    model = EnrollmentGrading
    queryset = EnrollmentGrading.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(owner=self.request.user)
        return self.queryset

    def get(self, request, *args, **kwargs):
        data= ''
        school = request.GET.get('school', 0)
        classroom = request.GET.get('classroom', 0)
        section = request.GET.get('section', 0)
        term = request.GET.get('term', 0)

        if self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            data = export_2ndshift_gradings({
                'current': 'true',
                'school': school,
                'classroom': classroom,
                'section': section,
                'term': term
            }, return_data=True)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xlsx'
        return response


class ExportBySchoolView(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.all()

    def get(self, request, *args, **kwargs):

        schools = self.queryset.values_list(
                        'school', 'school__number', 'school__name', 'school__location__name',
                        'school__location__parent__name', 'school__number_students_2nd_shift', ).distinct().order_by('school__number')

        data = tablib.Dataset()
        data.headers = [
            _('CERD'),
            _('School name'),
            _('# Students registered in the Compiler'),
            _('# Students reported by the Director'),
            _('District'),
            _('Governorate'),
        ]

        queryset = self.queryset.filter(education_year__current_year=True)

        content = []
        for school in schools:
            nbr = queryset.filter(school=school[0]).count()
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


class ExportByCycleView(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.all()

    def get(self, request, *args, **kwargs):

        classrooms = ClassRoom.objects.all()
        schools = self.queryset.values_list(
                        'school', 'school__number', 'school__name', 'school__location__name',
                        'school__location__parent__name', ).distinct().order_by('school__number')

        data = tablib.Dataset()
        data.headers = [
            _('CERD'),
            _('School name'),
            _('# Students registered in the Compiler'),
            'Class name',
            '# Students registered in class',
            _('District'),
            _('Governorate'),
        ]

        queryset = self.queryset.filter(education_year__current_year=True)

        content = []
        for school in schools:
            enrollments = queryset.filter(school=school[0])
            nbr = enrollments.count()
            for cls in classrooms:
                nbr_cls = enrollments.filter(classroom=cls).count()
                if not nbr_cls:
                    pass

                content = [
                    school[1],
                    school[2],
                    nbr,
                    cls.name,
                    nbr_cls,
                    school[3],
                    school[4]
                ]
                data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=student_by_cycle.xls'
        return response
