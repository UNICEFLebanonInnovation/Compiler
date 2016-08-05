# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
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

from .models import Outreach, ExtraColumn, Registration, Attendance
from .serializers import OutreachSerializer, ExtraColumnSerializer, RegistrationSerializer, AttendanceSerializer
from student_registration.students.models import (
    Student,
    School,
    ClassRoom,
    Grade,
    Section,
    Language,
    EducationLevel,
    ClassLevel,
    Location,
    Nationality,
    PartnerOrganization
)
from student_registration.students.serializers import StudentSerializer


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

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        student = instance.student
        instance.delete()
        if student:
            student.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})

    def partial_update(self, request, *args, **kwargs):
        extra_fields = json.dumps(request.data)
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.extra_fields = extra_fields
        instance.save()
        return JsonResponse({'status': status.HTTP_200_OK})


class ExtraColumnViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = ExtraColumn
    queryset = ExtraColumn.objects.all()
    serializer_class = ExtraColumnSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})


class RegistrationViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Registration
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset
        # return self.queryset.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        student = instance.student
        instance.delete()
        if student:
            student.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Attendance
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset
        # return self.queryset.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})


class OutreachView(LoginRequiredMixin, ListView):
    model = Outreach
    template_name = 'alp/outreach.html'

    def get_context_data(self, **kwargs):

        data = self.model.objects.all()
        if not self.request.user.is_superuser:
            data = data.filter(owner=self.request.user)
            self.template_name = 'alp/outreach_list.html'

        return {
            'outreaches': data,
            'schools': School.objects.all(),
            'languages': Language.objects.all(),
            'education_levels': EducationLevel.objects.all(),
            'levels': ClassLevel.objects.all(),
            'locations': Location.objects.all(),
            'nationalities': Nationality.objects.all(),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km'),
            'genders': (u'Male', u'Female'),
        }


class RegistrationView(LoginRequiredMixin, ListView):
    model = Registration
    template_name = 'alp/registration_list.html'

    def get_context_data(self, **kwargs):
        data = self.model.objects.all()
        if not self.request.user.is_superuser:
            data = data.filter(owner=self.request.user)
            self.template_name = 'alp/registration.html'

        return {
            'registrations': data,
            'classrooms': ClassRoom.objects.all(),
            'schools': School.objects.all(),
            'grades': Grade.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.all(),
            'genders': (u'Male', u'Female'),
        }


class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'alp/attendance_list.html'

    def get_context_data(self, **kwargs):
        data = self.model.objects.all()

        return {
            'attendances': data,
            'locations': Location.objects.all(),
            'schools': School.objects.all(),
            'grades': Grade.objects.all(),
            'sections': Section.objects.all()
        }


class OutreachExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        queryset = Outreach.objects.all()
        columns = ExtraColumn.objects.all()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
            columns = columns.filter(owner=self.request.user)

        data = tablib.Dataset()

        headers = [
                    _('Partner'), _('Student number'), _('Student fullname'), _('Mother fullname'), _('Nationality'),
                    _('Day of birth'), _('Month of birth'), _('Year of birth'), _('Sex'),
                    _('ID Number tooltip'), _('Phone number'), _('Governorate'), _('Student living address'),
                    _('Last education level'), _('Last education year'), _('Last training level'), _('Preferred language'),
                    _('Average distance'), _('Outreach exam - day'), _('Outreach exam - month'), _('Outreach exam - year'),
                    _('School name'), _('School name number')
        ]

        for idx, col in enumerate(columns):
            headers = [col.label] + headers

        data.headers = headers

        content = []
        for line in queryset:
            if not line.student:
                continue
            content = [
                line.partner.name,
                '',
                line.student.full_name,
                line.student.mother_fullname,
                line.student.nationality.name,
                int(line.student.birthday_day),
                int(line.student.birthday_month),
                int(line.student.birthday_year),
                _(line.student.sex),
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

            try:
                extra_fields = json.loads(line.extra_fields)
            except TypeError:
                extra_fields = []
            for cidx, col in enumerate(columns):
                field_name = col.name.replace('column', 'field')+'-'+str(line.id)
                field_value = ''
                if field_name in extra_fields:
                    field_value = extra_fields[field_name]
                content = [field_value] + content

            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=outreach_list.xls'
        return response


class RegistrationExportViewSet(LoginRequiredMixin, ListView):
    model = Registration

    def get(self, request, *args, **kwargs):

        queryset = self.model.objects.all()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)

        data = tablib.Dataset()
        data.headers = [
                    _('Student number'), _('Student fullname'), _('Mother fullname'), _('Nationality'),
                    _('Day of birth'), _('Month of birth'), _('Year of birth'), _('Sex'),
                    _('ID Number tooltip'), _('Phone number'), _('Student living address'),
                    # _('Section'), _('Grade'),
                    _('Class room'),
                    _('School'), _('School number')
        ]

        content = []
        for line in queryset:
            # if not line.student or not line.grade or not line.section or not line.school:
            if not line.student or not line.classroom or not line.school:
                continue
            content = [
                '',
                line.student.full_name,
                line.student.mother_fullname,
                line.student.nationality.name,
                int(line.student.birthday_day),
                int(line.student.birthday_month),
                int(line.student.birthday_year),
                _(line.student.sex),
                line.student.id_number,
                line.student.phone,
                line.student.address,
                line.classroom.name,
                # line.section.name,
                # line.grade.name,
                line.school.name,
                line.school.number
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return response
