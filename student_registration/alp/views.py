# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from datetime import datetime
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats

from .models import Outreach, ALPRound
from .serializers import OutreachSerializer, OutreachExamSerializer, OutreachSmallSerializer
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    Person,
    Student,
    Language,
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
    PartnerOrganization
)
from student_registration.locations.models import Location
from student_registration.eav.models import (
    Attribute,
    Value,
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

    # def get_queryset(self):
    #     if has_group(self.request.user, 'CERD'):
    #         return self.queryset
    #     if has_group(self.request.user, 'ALP_SCHOOL'):
    #         return self.queryset.filter(school_id=self.request.user.school_id)
    #     return self.queryset.filter(owner=self.request.user)

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
        self.serializer_class = OutreachExamSerializer
        return super(OutreachViewSet, self).partial_update(request)


class OutreachView(LoginRequiredMixin, TemplateView):
    model = Outreach
    template_name = 'alp/index.html'

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        school_id = int(self.request.GET.get("school", 0))
        if has_group(self.request.user, 'CERD'):
            data = Outreach.objects.exclude(owner__partner_id=None)
            data = data.filter(school_id=school_id)
        if has_group(self.request.user, 'ALP_SCHOOL'):
            data = Outreach.objects.filter(school_id=self.request.user.school_id)
            data = data.exclude(owner_id=self.request.user.id)
            school_id = self.request.user.school_id
        if school_id:
            school = School.objects.get(id=school_id)
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'data': data,
            'schools': School.objects.all(),
            'languages': Language.objects.all(),
            'locations': Location.objects.filter(type_id=2),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km',),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'columns': Attribute.objects.filter(type=Outreach.EAV_TYPE),
            'eav_type': Outreach.EAV_TYPE,
            'selectedSchool': school_id,
            'school': school,
            'location': location,
            'location_parent': location_parent,
        }


class OutreachStaffView(LoginRequiredMixin, TemplateView):
    model = Outreach
    template_name = 'alp/list.html'

    def get_context_data(self, **kwargs):
        data = []
        schools = School.objects.all()

        try:
            school = int(self.request.GET.get("school", 0))
        except Exception as ex:
            school = 0
        try:
            location = int(self.request.GET.get("location", 0))
        except Exception as ex:
            location = 0
        if school:
            data = self.model.objects.filter(school=school).order_by('id')

        return {
            'outreaches': data,
            'locations': Location.objects.filter(type_id=2),
            'schools': schools,
            'selectedSchool': school,
            'selectedLocation': location,
        }


class OutreachExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.exclude(not_enrolled_in_this_school=True)
        # queryset = self.model.objects.exclude(deleted=True, not_enrolled_in_this_school=True)
        school = int(request.GET.get('school', 0))
        location = int(request.GET.get('location', 0))

        if has_group(self.request.user, 'PARTNER'):
            queryset = queryset.filter(owner=self.request.user)
        if has_group(self.request.user, 'ALP_SCHOOL') and self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            queryset = queryset.filter(school_id=school).order_by('id')
        if location:
            queryset = queryset.filter(school__location_id=location).order_by('id')

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

            _('Science corrector'),
            _('Math corrector'),
            _('Foreign language corrector'),
            _('Arabic language corrector'),

            _('Assigned to level'),
            _('Total'),
            _('Science'),
            _('Math'),
            _('Foreign language'),
            _('Arabic language'),
            _('Registered in level'),

            _('Student nationality'),
            _('Student age'),
            _('Student birthday'),
            _('Sex'),
            _('Student fullname'),

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

                line.exam_corrector_science,
                line.exam_corrector_math,
                line.exam_corrector_language,
                line.exam_corrector_arabic,

                line.assigned_to_level.name if line.assigned_to_level else '',
                line.exam_total,
                line.exam_result_science,
                line.exam_result_math,
                line.exam_result_language,
                line.exam_result_arabic,
                line.level.name if line.level else '',

                line.student.nationality_name(),
                line.student.birthday,
                line.student.calc_age,
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
