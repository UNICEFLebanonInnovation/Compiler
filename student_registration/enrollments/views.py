# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.db.models import Q

import tablib
from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from import_export.formats import base_formats

from student_registration.alp.templatetags.util_tags import has_group

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from .filters import EnrollmentFilter
from .tables import BootstrapTable, EnrollmentTable

from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer
from student_registration.schools.models import ClassRoom
from .models import Enrollment, LoggingStudentMove, EducationYear, LoggingProgramMove
from .forms import EnrollmentForm, GradingTerm1Form, GradingTerm2Form, StudentMovedForm
from .serializers import EnrollmentSerializer, LoggingStudentMoveSerializer, LoggingProgramMoveSerializer
from student_registration.users.utils import force_default_language


class AddView(LoginRequiredMixin,
              GroupRequiredMixin,
              FormView):

    template_name = 'bootstrap4/common_form.html'
    form_class = EnrollmentForm
    success_url = '/enrollments/list/'
    group_required = [u"ENROL_CREATE"]

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
            instance = Enrollment.objects.get(id=self.request.GET.get('enrollment_id'))
            data = EnrollmentSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            data['student_mother_nationality'] = data['student_mother_nationality_id']
            data['student_id_type'] = data['student_id_type_id']
        if self.request.GET.get('child_id'):
            instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
            data = ChildSerializer(instance).data
            # data['student_nationality'] = data['student_nationality_id']
            # data['student_mother_nationality'] = data['student_mother_nationality_id']
            # data['student_id_type'] = data['student_id_type_id']
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
    form_class = GradingTerm1Form
    success_url = '/enrollments/list/'
    group_required = [u"ENROL_GRADING"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(GradingView, self).get_context_data(**kwargs)

    def get_form_class(self):
        if int(self.kwargs['term']) == 2:
            return GradingTerm2Form
        return GradingTerm1Form

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
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
            current_year = EducationYear.objects.get(current_year=True)
            enrollment.moved = True
            enrollment.save()
            LoggingStudentMove.objects.get_or_create(
                enrolment_id=enrollment.id,
                student_id=enrollment.student_id,
                school_from_id=enrollment.school_id,
                education_year=current_year
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


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(owner=self.request.user)
        return self.queryset

    def get(self, request, *args, **kwargs):
        queryset = self.queryset
        school = request.GET.get('school', 0)
        gov = request.GET.get('gov', 0)

        if self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            queryset = queryset.filter(school_id=school)
        elif gov:
            queryset = queryset.filter(school__location__parent__id=gov)
        else:
            queryset = []

        data = tablib.Dataset()
        data.headers = [
            _('Student status'),
            _('Final Grade'),

            _('Linguistic field/Arabic'),
            _('Sociology field'),
            _('Physical field'),
            _('Artistic field'),
            _('Linguistic field/Foreign language'),
            _('Scientific domain/Mathematics'),
            _('Scientific domain/Sciences'),

            _('Biology'),
            _('Chemistry'),
            _('Physic'),
            _('Science'),
            _('Math'),
            _('History'),
            _('Geography'),
            _('Education'),
            _('Foreign language'),
            _('Arabic'),

            _('ALP result'),
            _('ALP round'),
            _('ALP level'),
            _('Is the child participated in an ALP/2016-2 program'),
            _('Result'),
            _('Education year'),
            _('School type'),
            _('School shift'),
            _('School'),
            _('Last education level'),
            _('Current Section'),
            _('Current Class'),
            _('Phone prefix'),
            _('Phone number'),
            _('Student living address'),
            _('Student ID Number'),
            _('Student ID Type'),
            _('Registered in UNHCR'),
            _('Mother nationality'),
            _('Mother fullname'),
            _('Student nationality'),
            _('Student age'),
            _('Student birthday'),
            _('year'),
            _('month'),
            _('day'),
            _('Sex'),
            _('Student fullname'),
            _('School'),
            _('School number'),
            _('District'),
            _('Governorate'),
            'id'
        ]

        content = []
        for line in queryset:
            if not line.student or not line.school:
                continue
            content = [

                line.exam_result,
                line.exam_total,

                line.exam_result_linguistic_ar,
                line.exam_result_sociology,
                line.exam_result_physical,
                line.exam_result_artistic,
                line.exam_result_linguistic_en,
                line.exam_result_mathematics,
                line.exam_result_sciences,

                line.exam_result_bio,
                line.exam_result_chemistry,
                line.exam_result_physic,
                line.exam_result_science,
                line.exam_result_math,
                line.exam_result_history,
                line.exam_result_geo,
                line.exam_result_education,
                line.exam_result_language,
                line.exam_result_arabic,

                line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
                line.last_informal_edu_round.name if line.last_informal_edu_round else '',
                line.last_informal_edu_level.name if line.last_informal_edu_level else '',
                _(line.participated_in_alp) if line.participated_in_alp else '',

                _(line.last_year_result) if line.last_year_result else '',
                line.last_education_year if line.last_education_year else '',
                line.last_school.name if line.last_school else '',
                _(line.last_school_shift) if line.last_school_shift else '',
                _(line.last_school_type) if line.last_school_type else '',
                line.last_education_level.name if line.last_education_level else '',

                line.section.name if line.section else '',
                line.classroom.name if line.classroom else '',

                line.student.phone_prefix,
                line.student.phone,
                line.student.address,

                line.student.id_number,
                line.student.id_type.name if line.student.id_type else '',
                line.registered_in_unhcr,

                line.student.mother_nationality.name if line.student.mother_nationality else '',
                line.student.mother_fullname,
                line.student.nationality_name(),

                line.student.calc_age,
                line.student.birthday,
                line.student.birthday_year,
                line.student.birthday_month,
                line.student.birthday_day,
                _(line.student.sex) if line.student.sex else '',
                line.student.__unicode__(),

                line.school.name,
                line.school.number,
                line.school.location.name,
                line.school.location.parent.name,
                line.id
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
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

        content = []
        for school in schools:
            nbr = self.model.objects.filter(school=school[0]).count()
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

        content = []
        for school in schools:
            enrollments = self.model.objects.filter(school=school[0])
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
