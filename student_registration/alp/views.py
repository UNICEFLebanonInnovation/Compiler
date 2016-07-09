# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from copy import deepcopy
import xlsxwriter
import StringIO
import json
from rest_framework import status
from django.utils.translation import ugettext as _

from .models import Outreach, ExtraColumn
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

        return {
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


class OutreachOnlineView(LoginRequiredMixin, ListView):
    model = Outreach
    template_name = 'alp/outreach.html'

    def get_context_data(self, **kwargs):

        return {
            'outreaches': Outreach.objects.all(),
            'columns': ExtraColumn.objects.all(),
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


class ExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
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

        for idx, title in enumerate(titles):
            worksheet.write(0, idx, _(title), format)

        for idx, line in enumerate(data):
            worksheet.write_string(idx+1, 0, line.partner.name)
            worksheet.write_string(idx+1, 1, '')
            worksheet.write_string(idx+1, 2, line.student.full_name)
            worksheet.write_string(idx+1, 3, line.student.mother_fullname)
            worksheet.write_string(idx+1, 4, line.student.nationality.name)
            worksheet.write_number(idx+1, 7, int(line.student.birthday_day))
            worksheet.write_number(idx+1, 6, int(line.student.birthday_month))
            worksheet.write_number(idx+1, 5, int(line.student.birthday_year))
            worksheet.write_string(idx+1, 8, _(line.student.sex))
            worksheet.write_string(idx+1, 9, line.student.id_number)
            worksheet.write_string(idx+1, 10, line.student.phone)
            worksheet.write_string(idx+1, 11, line.location.name if line.location else '')
            worksheet.write_string(idx+1, 12, line.student.address)
            worksheet.write_string(idx+1, 13, line.last_education_level.name)
            worksheet.write_string(idx+1, 14, line.last_education_year)
            worksheet.write_string(idx+1, 15, line.last_class_level.name)
            worksheet.write_string(idx+1, 16, line.preferred_language.name)
            worksheet.write_string(idx+1, 17, line.average_distance)
            worksheet.write_number(idx+1, 18, int(line.exam_day))
            worksheet.write_number(idx+1, 19, int(line.exam_month))
            worksheet.write_number(idx+1, 20, int(line.exam_year))
            worksheet.write_string(idx+1, 21, line.school.name)
            worksheet.write_string(idx+1, 22, line.school.number)

        workbook.close()

        filename = 'ExcelReport.xlsx'
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response
