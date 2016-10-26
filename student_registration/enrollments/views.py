# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from django.core.urlresolvers import reverse
from datetime import datetime
from student_registration.alp.templatetags.util_tags import has_group

from student_registration.students.models import (
    Person,
    Student,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Grade,
    Section,
    EducationLevel,
    ClassLevel,
)
from student_registration.students.serializers import StudentSerializer
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.locations.models import Location

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentStaffView(LoginRequiredMixin, TemplateView):
    """
    Provides the Enrollment page with lookup types in the context
    """
    model = Enrollment
    template_name = 'enrollments/list.html'

    def get_context_data(self, **kwargs):
        data = []
        schools = []

        if has_group(self.request.user, 'MEHE'):
            schools = School.objects.all()
        elif has_group(self.request.user, 'COORDINATOR'):
            schools = School.objects.filter(location_id__in=self.request.user.locations.all())
        elif has_group(self.request.user, 'PMU'):
            schools = School.objects.filter(location_id=self.request.user.location_id)

        school = self.request.GET.get("school", 0)
        if school:
            data = self.model.objects.filter(school=school).order_by('id')

        return {
            'enrollments': data,
            'schools': schools,
            'columns': Attribute.objects.filter(type=Enrollment.EAV_TYPE),
            'eav_type': Enrollment.EAV_TYPE,
            'selectedSchool': int(school),
        }


class EnrollmentView(LoginRequiredMixin, TemplateView):
    """
    Provides the enrollment page with lookup types in the context
    """
    model = Enrollment
    template_name = 'enrollments/index.html'

    def get_context_data(self, **kwargs):

        return {
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
            'columns': Attribute.objects.filter(type=Enrollment.EAV_TYPE),
            'eav_type': Enrollment.EAV_TYPE,
        }


####################### API VIEWS #############################


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
        if not self.request.user.is_staff:
            if self.request.user.school:
                return self.queryset.filter(school=self.request.user.school.id)
            else:
                return []

        return self.queryset

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        student = instance.student
        instance.delete()
        if student:
            student.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.save()


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Enrollment
    queryset = Enrollment.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(owner=self.request.user)
        return self.queryset

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        data = tablib.Dataset()
        data.headers = [
            _('Last education year'),
            _('Last education level'),
            _('Last year result'),
            _('Current Section'),
            _('Current Class'),
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
            _('Sex'),
            _('Student fullname'),
            _('Student number'),
            _('School'),
            _('School number'),
            _('District'),
            _('Governorate')
        ]

        content = []
        for line in queryset:
            if not line.student or not line.school:
                continue
            content = [
                line.last_education_year if line.last_education_year else '',
                line.last_education_level.name if line.last_education_level else '',
                line.last_year_result,
                line.section.name if line.section else '',
                line.classroom.name if line.classroom else '',
                line.student.phone,
                line.student.address,
                line.student.id_number,
                line.student.id_type.name if line.student.id_type else '',
                line.registered_in_unhcr,
                line.student.mother_nationality.name if line.student.mother_nationality else '',
                line.student.mother_fullname,
                line.student.nationality_name(),
                line.student.birthday,
                line.student.get_age(),
                _(line.student.sex),
                line.student.__unicode__(),
                line.student.number,
                line.school.name,
                line.school.number,
                line.school.location.name,
                line.school.location.parent.name,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return response
