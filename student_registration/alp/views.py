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

from .models import Outreach
from .serializers import OutreachSerializer
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

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

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


class OutreachView(LoginRequiredMixin, TemplateView):
    model = Outreach
    template_name = 'alp/index.html'

    def get_context_data(self, **kwargs):

        return {
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
            'education_final_results': EducationLevel.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'columns': Attribute.objects.filter(type=Outreach.EAV_TYPE),
            'eav_type': Outreach.EAV_TYPE
        }


class OutreachStaffView(LoginRequiredMixin, TemplateView):
    model = Outreach
    template_name = 'alp/list.html'

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
            'outreaches': data,
            'schools': schools,
            'columns': Attribute.objects.filter(type=Outreach.EAV_TYPE),
            'eav_type': Outreach.EAV_TYPE,
            'selectedSchool': int(school),
        }


class OutreachExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        queryset = Outreach.objects.all()
        columns = Attribute.objects.filter(type=Outreach.EAV_TYPE)

        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
            columns = columns.filter(owner=self.request.user)

        data = tablib.Dataset()

        headers = [
                    _('Partner'), _('Student number'), _('Student fullname'), _('Mother fullname'), _('Nationality'),
                    _('Day of birth'), _('Month of birth'), _('Year of birth'), _('Sex'), _('ID Type'),
                    _('ID Number tooltip'), _('Phone number'), _('Governorate'), _('Student living address'),
                    _('Last education level'), _('Last education year'), _('Last training level'), _('Preferred language'),
                    _('Average distance'), _('Outreach exam - day'), _('Outreach exam - month'), _('Outreach exam - year'),
                    _('School name'), _('School name number')
        ]

        for idx, col in enumerate(columns):
            headers = [col.name] + headers

        data.headers = headers

        content = []
        for line in queryset:
            if not line.student:
                continue
            content = [
                line.partner.name,
                line.student.number,
                line.student.full_name,
                line.student.mother_fullname,
                line.student.nationality.name,
                int(line.student.birthday_day),
                int(line.student.birthday_month),
                int(line.student.birthday_year),
                _(line.student.sex),
                line.student.id_type.name,
                line.student.id_number,
                line.student.phone,
                line.location.name if line.location else '',
                line.student.address,
                line.last_education_level.name,
                line.last_education_year,
                line.last_class_level.name,
                line.preferred_language.name,
                line.average_distance,
                int(line.exam_day),
                int(line.exam_month),
                int(line.exam_year),
                line.school.name,
                line.school.number
            ]

            extra_fields = Value.objects.filter(entity_id=line.id, entity_ct=17)
            for field in extra_fields:
                content = [field.value_text] + content

            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=outreach_list.xls'
        return response
