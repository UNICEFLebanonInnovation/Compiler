# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from copy import deepcopy
from datetime import datetime
import xlsxwriter
import StringIO
import json
from rest_framework import status
from django.utils.translation import ugettext as _

from .models import Outreach, ExtraColumn, Registration, Attendance
from .serializers import OutreachSerializer, ExtraColumnSerializer
from .forms import OutreachForm, OutreachFormSet
from student_registration.students.models import (
    Student,
    School,
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
        instance = Outreach.objects.get(id=kwargs['pk'])
        student = instance.student
        instance.delete()
        if student:
            student.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = Outreach.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})

    def partial_update(self, request, *args, **kwargs):
        extra_fields = json.dumps(request.data)
        instance = Outreach.objects.get(id=kwargs['pk'])
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


class OutreachView(LoginRequiredMixin, ListView):
    model = Outreach
    template_name = 'alp/outreach_list.html'

    def get_context_data(self, **kwargs):
        data = []
        if self.request.user.is_superuser:
            data = Outreach.objects.all()
            self.template_name = 'alp/outreach.html'

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
    template_name = 'alp/registration.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            self.template_name = 'alp/registration_list.html'

        return {

        }


class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'alp/attendance.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            self.template_name = 'alp/attendance_list.html'

        print self.template_name

        return {

        }


class ExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        current_date = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Page 1')

        data = Outreach.objects.all()
        columns = ExtraColumn.objects.all()

        if not self.request.user.is_superuser:
            data = data.filter(owner=self.request.user)
            columns = columns.filter(owner=self.request.user)

        format = workbook.add_format({'bold': True, 'font_color': '#383D3F', 'bg_color': '#92CEFB', 'font_size': 16})

        titles = ['Partner', 'Student number', 'Student fullname', 'Mother fullname', 'Nationality',
                  'Day of birth', 'Month of birth', 'Year of birth',
                  'Sex', 'ID Number tooltip',
                  'Phone number', 'Governorate', 'Student living address', 'Last education level',
                  'Last education year', 'Last training level', 'Preferred language', 'Average distance',
                  'Outreach exam - day', 'Outreach exam - month', 'Outreach exam - year',
                  'School name', 'School name number'
                  ]

        for idx, col in enumerate(columns):
            worksheet.write(0, idx, col.label, format)

        for idx, title in enumerate(titles):
            worksheet.write(0, idx+len(columns), _(title), format)

        for idx, line in enumerate(data):
            worksheet.write_string(idx+1, 0+len(columns), line.partner.name)
            worksheet.write_string(idx+1, 1+len(columns), '')
            worksheet.write_string(idx+1, 2+len(columns), line.student.full_name)
            worksheet.write_string(idx+1, 3+len(columns), line.student.mother_fullname)
            worksheet.write_string(idx+1, 4+len(columns), line.student.nationality.name)
            worksheet.write_number(idx+1, 7+len(columns), int(line.student.birthday_day))
            worksheet.write_number(idx+1, 6+len(columns), int(line.student.birthday_month))
            worksheet.write_number(idx+1, 5+len(columns), int(line.student.birthday_year))
            worksheet.write_string(idx+1, 8+len(columns), _(line.student.sex))
            worksheet.write_string(idx+1, 9+len(columns), line.student.id_number)
            worksheet.write_string(idx+1, 10+len(columns), line.student.phone)
            worksheet.write_string(idx+1, 11+len(columns), line.location.name if line.location else '')
            worksheet.write_string(idx+1, 12+len(columns), line.student.address)
            worksheet.write_string(idx+1, 13+len(columns), line.last_education_level.name)
            worksheet.write_string(idx+1, 14+len(columns), line.last_education_year)
            worksheet.write_string(idx+1, 15+len(columns), line.last_class_level.name)
            worksheet.write_string(idx+1, 16+len(columns), line.preferred_language.name)
            worksheet.write_string(idx+1, 17+len(columns), line.average_distance)
            worksheet.write_number(idx+1, 18+len(columns), int(line.exam_day))
            worksheet.write_number(idx+1, 19+len(columns), int(line.exam_month))
            worksheet.write_number(idx+1, 20+len(columns), int(line.exam_year))
            worksheet.write_string(idx+1, 21+len(columns), line.school.name)
            worksheet.write_string(idx+1, 22+len(columns), line.school.number)

            extra_fields = json.loads(line.extra_fields)
            for cidx, col in enumerate(columns):
                field_name = col.name.replace('column', 'field')+'-'+str(line.id)
                field_value = '';
                if field_name in extra_fields:
                    field_value = extra_fields[field_name]
                worksheet.write(idx+1, cidx, field_value)

        workbook.close()

        filename = 'outreach_report_'+current_date+'.xlsx'
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
