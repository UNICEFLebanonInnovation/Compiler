# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import datetime
import tablib
import json

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from rest_framework import viewsets, mixins, permissions
from rest_framework.generics import ListAPIView
from rest_framework.decorators import detail_route, list_route
from datetime import datetime
from rest_framework import status

from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom
)
from .models import Attendance, Absentee
from .serializers import AttendanceSerializer, AbsenteeSerializer
from student_registration.attendances.tasks import set_app_attendances
from student_registration.enrollments.models import (
    Enrollment,
    EducationYear,
)


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
        if not self.request.user.is_superuser:
            if self.request.user.school:
                return self.queryset.filter(school_id=self.request.user.school.id)
            else:
                return []

        return self.queryset

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

    @list_route(methods=['get'], url_path='push-by-school/(?P<school>\d+)')
    def push_by_school(self, request, *args, **kwargs):
        school = School.objects.get(id=kwargs.get('school', False))
        set_app_attendances.delay(school_number=school.number)
        return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceReportViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):

    model = Attendance
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        school = request.GET.get("school", 0)

        queryset = self.queryset.filter(school_id=school)
        data = tablib.Dataset()
        data.headers = [
            _('Student number'), _('Student fullname'), _('Mother fullname'),
        ]

        content = []
        for line in queryset:
            content = [
                line.student.number,
                line.student.__unicode__(),
                line.student.mother_fullname,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        # response = HttpResponse(
        #     file_format.export_data(data),
        #     content_type='application/vnd.ms-excel',
        # )
        # response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return JsonResponse({'status': status.HTTP_200_OK})


class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendances/school.html'

    def get_context_data(self, **kwargs):
        level = 0
        section = 0
        school = 0
        location = 0
        location_parent = 0
        levels_by_sections = []
        students = []

        # if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'DIRECTOR'):
        if self.request.user.school:
            school = self.request.user.school
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        current_date = datetime.datetime.now().strftime('%d/%m/%Y')
        selected_date = self.request.GET.get('date', current_date)
        selected_date_view = datetime.datetime.strptime(selected_date, '%d/%m/%Y').strftime('%A %d/%m/%Y')

        attendances = Attendance.objects.filter(
            school_id=school,
            attendance_date=datetime.datetime.strptime(selected_date, '%d/%m/%Y')
        )

        if self.request.GET.get('level', 0):
            level = ClassRoom.objects.get(id=int(self.request.GET.get('level', 0)))
        if self.request.GET.get('section', 0):
            section = Section.objects.get(id=int(self.request.GET.get('section', 0)))

        education_year = EducationYear.objects.get(current_year=True)
        queryset = Enrollment.objects.filter(school_id=school, education_year=education_year)
        registrations = queryset.filter(
            classroom__isnull=False,
            section__isnull=False
        ).distinct().values(
            'classroom__name',
            'classroom_id',
            'section__name',
            'section_id'
        ).order_by('classroom_id')

        if level:
            students = queryset.filter(
                classroom_id=level.id,
                section_id=section.id
            ).order_by('student__first_name')

        for registry in registrations:
            attendances = attendances.filter(
                classroom_id=registry['classroom_id'],
                section_id=registry['section_id']
            )
            validation_date = ''
            validation = attendances.filter(validation_date__isnull=False)
            if validation.count():
                validation_date = validation[0]
            levels_by_sections.append({
                'level_name': registry['classroom__name'],
                'level': registry['classroom_id'],
                'section_name': registry['section__name'],
                'section': registry['section_id'],
                'total': queryset.filter(classroom_id=registry['classroom_id'], section_id=registry['section_id']).count(),
                'total_attend': attendances.filter(status=True).count(),
                'total_absent': attendances.filter(status=False).count(),
                'validation_date': validation_date
            })

        base = datetime.datetime.now()
        dates = []
        weekend = [5, 6]

        for x in range(0, 30):
            d = base - datetime.timedelta(days=x)
            if d.weekday() not in weekend:
                # dates.append(d.strftime('%A %D/%m/%Y'))
                dates.append({
                    'value': d.strftime('%d/%m/%Y'),
                    'label': d.strftime('%A %d/%m/%Y')
                })

        return {
            'total': queryset.count(),
            'total_students': students.count() if students else 0,
            'students': students,
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'level': level,
            'section': section,
            'dates': dates,
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'levels_by_sections': levels_by_sections,
            'selected_date': selected_date,
            'selected_date_view': selected_date_view,
        }


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Attendance

    def get(self, request, *args, **kwargs):

        school = request.GET.get("school")

        queryset = self.queryset
        data = tablib.Dataset()
        data.headers = [
            _('Student number'), _('Student fullname'), _('Mother fullname'),
        ]

        content = []
        for line in queryset:
            content = [
                line.student.number,
                line.student.__unicode__(),
                line.student.mother_fullname,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=registration_list.xls'
        return response


class AbsenteeView(ListAPIView):
    """
    API endpoint for validated absentees
    """
    queryset = Absentee.objects.filter(
        school__location=True
    )
    serializer_class = AbsenteeSerializer
    permission_classes = (permissions.IsAdminUser,)
