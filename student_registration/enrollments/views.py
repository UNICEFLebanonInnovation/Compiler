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

from student_registration.students.models import (
    Person,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Section,
    EducationLevel,
    ClassLevel,
)
from student_registration.alp.models import ALPRound
from student_registration.outreach.models import Child
from student_registration.outreach.serializers import ChildSerializer
from .models import Enrollment, LoggingStudentMove, EducationYear
from .forms import EnrollmentForm, GradingTerm1Form, GradingTerm2Form
from .serializers import EnrollmentSerializer, LoggingStudentMoveSerializer


class EnrollmentView(LoginRequiredMixin,
                     # GroupRequiredMixin,
                     FormView):

    template_name = 'enrollments/new.html'
    form_class = EnrollmentForm
    success_url = '/enrollments/list/'

    def get_context_data(self, **kwargs):
        # force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EnrollmentView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(EnrollmentView, self).get_initial()
        data = []
        if self.request.GET.get('enrollment_id'):
            instance = Enrollment.objects.get(id=self.request.GET.get('enrollment_id'))
            data = EnrollmentSerializer(instance).data
        if self.request.GET.get('student_outreach_child'):
            instance = Child.objects.get(id=int(self.request.GET.get('student_outreach_child')))
            data = ChildSerializer(instance).data
        initial = data

        return initial

    # def get_form(self, form_class=None):
    #     form = super(EnrollmentView, self).get_form(form_class)
    #     # override the queryset
    #     form.fields['offered_player'].queryset = self.petitioner.players
    #     return form
    #
    # def get(self, request, *args, **kwargs):
    #     # only perform 1 query to get 'petitioner'
    #     self.petitioner = get_object_or_404(Team, user=self.request.user.profile, league=self.kwargs['pk'])
    #     return super(LeagueTransferView, self).get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)
    #
    def form_valid(self, form):
        form.save(self.request)
        return super(EnrollmentView, self).form_valid(form)


class EnrollmentEditView(LoginRequiredMixin,
                         # GroupRequiredMixin,
                         FormView):

    template_name = 'enrollments/edit.html'
    form_class = EnrollmentForm
    success_url = '/enrollments/list/'

    def get_context_data(self, **kwargs):
        # force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(EnrollmentEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            EnrollmentForm(self.request.POST, instance=instance)
        else:
            data = EnrollmentSerializer(instance).data
            return EnrollmentForm(data, instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(EnrollmentEditView, self).form_valid(form)


class EnrollmentListView(LoginRequiredMixin,
                         FilterView,
                         ExportMixin,
                         SingleTableView,
                         RequestConfig):
    table_class = EnrollmentTable
    model = Enrollment
    template_name = 'enrollments/list.html'
    table = BootstrapTable(Enrollment.objects.all(), order_by='id')

    filterset_class = EnrollmentFilter

    def get_queryset(self):
        education_year = EducationYear.objects.get(current_year=True)
        # return Enrollment.objects.filter(education_year=education_year, school=self.request.user.school_id)
        return Enrollment.objects.filter(school=self.request.user.school_id)

    # def get_context_data(self, **kwargs):
    #     return {
    #         'table': self.table
    #     }


class GradingView(LoginRequiredMixin,
                         # GroupRequiredMixin,
                         FormView):

    template_name = 'enrollments/grading.html'
    form_class = GradingTerm1Form
    success_url = '/enrollments/list/'

    def get_context_data(self, **kwargs):
        # force_default_language(self.request)
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
            form_class(self.request.POST, instance=instance)
        else:
            return form_class(instance=instance)

    def form_valid(self, form):
        instance = Enrollment.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(GradingView, self).form_valid(form)


# class EnrollmentEditView(LoginRequiredMixin,
#                          GroupRequiredMixin,
#                          TemplateView):
#     """
#     Provides the enrollment page with lookup types in the context
#     """
#     model = Enrollment
#     template_name = 'enrollments/edit.html'
#
#     group_required = [u"ENROL_EDIT"]
#
#     def get_context_data(self, **kwargs):
#
#         school_id = 0
#         school = 0
#         location = 0
#         location_parent = 0
#         total = 0
#         if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'DIRECTOR'):
#             school_id = self.request.user.school_id
#         if school_id:
#             school = School.objects.get(id=school_id)
#             total = self.model.objects.filter(school_id=school_id).count()
#         if school and school.location:
#             location = school.location
#         if location and location.parent:
#             location_parent = location.parent
#
#         return {
#             'total': total,
#             'schools': School.objects.all(),
#             'school_shifts': Enrollment.SCHOOL_SHIFT,
#             'school_types': Enrollment.SCHOOL_TYPE,
#             'education_levels': ClassRoom.objects.all(),
#             'education_results': Enrollment.RESULT,
#             'informal_educations': EducationLevel.objects.all(),
#             'education_final_results': ClassLevel.objects.all(),
#             'alp_rounds': ALPRound.objects.all(),
#             'classrooms': ClassRoom.objects.all(),
#             'sections': Section.objects.all(),
#             'nationalities': Nationality.objects.exclude(id=5),
#             'nationalities2': Nationality.objects.all(),
#             'genders': Person.GENDER,
#             'months': Person.MONTHS,
#             'idtypes': IDType.objects.all(),
#             'school': school,
#             'location': location,
#             'location_parent': location_parent
#         }


class EnrollmentPatchView(LoginRequiredMixin, TemplateView):
    """
    Provides the enrollment page with lookup types in the context
    """
    model = Enrollment
    template_name = 'enrollments/patch.html'

    def get_context_data(self, **kwargs):

        school_id = 0
        school = 0
        location = 0
        location_parent = 0
        total = 0
        if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'DIRECTOR'):
            school_id = self.request.user.school_id
        if school_id:
            school = School.objects.get(id=school_id)
            total = self.model.objects.filter(school_id=school_id).count()
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'total': total,
            'schools': School.objects.all(),
            'school_shifts': Enrollment.SCHOOL_SHIFT,
            'school_types': Enrollment.SCHOOL_TYPE,
            'education_levels': ClassRoom.objects.all(),
            'education_results': Enrollment.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'genders': Person.GENDER,
            'months': Person.MONTHS,
            'idtypes': IDType.objects.all(),
            'school': school,
            'location': location,
            'location_parent': location_parent
        }


class EnrollmentGradingView(LoginRequiredMixin, TemplateView):

        model = Enrollment
        template_name = 'enrollments/grading.html'

        def get_context_data(self, **kwargs):

            school_id = 0
            school = 0
            location = 0
            location_parent = 0
            total = 0
            level = int(self.request.GET.get('level', 0))
            section = int(self.request.GET.get('section', 0))
            queryset = []
            if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'DIRECTOR'):
                school_id = self.request.user.school_id
            if school_id:
                school = School.objects.get(id=school_id)
                total = self.model.objects.filter(school_id=school_id).count()
            if school and school.location:
                location = school.location
            if location and location.parent:
                location_parent = location.parent
            if school_id and level:
                queryset = self.model.objects.filter(school=school_id, classroom=level).order_by('student__first_name')
                if section:
                    queryset = queryset.filter(section=section)

            return {
                'data': queryset,
                'level': level,
                'section': section,
                'total': total,
                'school': school,
                'location': location,
                'results': self.model.EXAM_RESULT,
                'location_parent': location_parent,
                'classrooms': ClassRoom.objects.all(),
                'sections': Section.objects.all(),
            }


####################### API VIEWS #############################


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
        if terms:
            qs = self.queryset
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
            enrollment.moved = True
            enrollment.save()
            LoggingStudentMove.objects.get_or_create(
                enrolment_id=enrollment.id,
                student_id=enrollment.student_id,
                school_from_id=enrollment.school_id
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


class ExportDuplicatesView(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.order_by('-id')

    def get(self, request, *args, **kwargs):

        students = {}
        students2 = {}
        schools = {}
        duplicates = []
        queryset = self.queryset

        for registry in queryset:
            student = registry.student
            if student.number not in students:
                students[student.number] = registry
            else:
                duplicates.append(registry)
                schools[registry.school_id] = registry.school.name

            if student.number_part1 not in students2:
                students2[student.number_part1] = registry
            else:
                duplicates.append(registry)

            # if not student.id_number in students2:
            #     students2[student.id_number] = registry
            # else:
            #     duplicates.append(registry)
            #     duplicates.append(students2[student.id_number])

        data = tablib.Dataset()
        data.headers = [
            'ID',
            'Student ID',
            'Fullname',
            'Number',
            'Number part1',
            'ID number',
            'School',
        ]

        content = []
        for registry in duplicates:
            student = registry.student
            content = [
                registry.id,
                student.id,
                student.__unicode__(),
                student.number,
                student.number_part1,
                student.id_number,
                registry.school.name,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=duplications.xls'
        return response
