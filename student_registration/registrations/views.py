# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django.views.generic import ListView, FormView
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
)
from student_registration.students.serializers import StudentSerializer
from student_registration.registrations.forms import (
    RegisteringAdultForm,
    RegisteringChildForm,
    WaitingListForm,
)
from student_registration.students.forms import StudentForm
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.locations.models import Location

from .models import Registration, RegisteringAdult, WaitingList
from .serializers import (
    RegistrationSerializer,
    RegisteringAdultSerializer,
    RegistrationChildSerializer,
    ClassAssignmentSerializer,
    WaitingListSerializer,
)
from .utils import get_unhcr_principal_applicant


class RegistrationView(LoginRequiredMixin, ListView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Registration
    template_name = 'registrations/list.html'

    def get_context_data(self, **kwargs):
        data = []
        school = self.request.GET.get("school", 0)
        if school:
            data = self.model.objects.filter(school=school).order_by('id')

        if not self.request.user.is_staff:
            data = self.model.objects.filter(owner=self.request.user)
            self.template_name = 'registrations/index.html'

        return {
            'registrations': data,
            'education_levels': ClassRoom.objects.all(),
            'last_year_result': Registration.RESULT,
            'classrooms': ClassRoom.objects.all(),
            'schools': School.objects.all(),
            'grades': Grade.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'genders': (u'Male', u'Female'),
            'months': Person.MONTHS,
            'idtypes': IDType.objects.all(),
            'columns': Attribute.objects.filter(type=Registration.EAV_TYPE),
            'eav_type': Registration.EAV_TYPE,
            'locations': Location.objects.filter(type_id=2),
            'selectedSchool': int(school),
        }


class ClassAssignmentView(LoginRequiredMixin, ListView):
    """
    Provides the registration page with lookup types in the context
    """
    model = Registration
    template_name = 'registration-pilot/class-assignment.html'

    def get_context_data(self, **kwargs):
        data = []
        school = self.request.GET.get("school", "0")
        if school:
            data = Registration.objects.filter(school=school).order_by('id')

        location = self.request.user.location_id
        locations = self.request.user.locations.all()
        if len(locations):
            schools = School.objects.filter(location_id__in=locations)
        else:
            schools = School.objects.filter(location_id=location)

        return {
            'registrations': data,
            'classrooms': ClassRoom.objects.all(),
            'schools': schools,
            'selectedSchool': int(school),
            'sections': Section.objects.all()
        }


class WaitingListView(LoginRequiredMixin, ListView):
    """
    Provides the registration page with lookup types in the context
    """
    model = WaitingList
    template_name = 'registration-pilot/waitinglist.html'

    def get_context_data(self, **kwargs):

        return {
            'form': WaitingListForm({'location': self.request.user.location_id,
                                     'locations': self.request.user.locations.all()}),
        }


####################### API VIEWS #############################


class RegistrationViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    Provides API operations around a registration record
    """
    model = Registration
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
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

    # def update(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return JsonResponse({'status': status.HTTP_200_OK, 'student_number': serializer.data['student_number']})


class RegisteringAdultViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):

    lookup_field = 'id_number'
    model = RegisteringAdult
    queryset = RegisteringAdult.objects.all()
    serializer_class = RegisteringAdultSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # def get_queryset(self):
    #     queryset = super(RegisteringAdultViewSet, self).get_queryset()
    #     id_number = self.kwargs.get('id_number')
    #     if id_number:
    #         return queryset.filter(id_number=id_number)
    #     return queryset

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return []

    def get_object(self):
        """
        Try to lookup the registering adult from the UNHCR registration database
        :return:
        """
        adult = []
        try:
            # first try and look up in our database
            adults = RegisteringAdult.objects.filter(id_number=self.kwargs.get('id_number')).order_by('id')
            if adults:
                return adults[0]

            raise Http404()
            # adult = super(RegisteringAdultViewSet, self).get_object()
            # return adult

        except Http404 as exp:
            # or look up in UNHCR
            if self.kwargs.get('id_number'):
                principal_applicant = get_unhcr_principal_applicant(self.kwargs.get('id_number'))
                if principal_applicant:
                    print principal_applicant[0]
                    adult = RegisteringAdult()
                    applicant = principal_applicant[len(principal_applicant)-1]
                    adult.id_number = applicant["CaseNo"]
                    adult.phone = applicant["CoAPhone"]
                    adult.first_name = applicant["GivenName"]
                    adult.last_name = applicant["FamilyName"]
                    adult.father_name = applicant["FatherName"]
                    dob = datetime.strptime(applicant["DOB"], '%Y-%m-%dT%H:%M:%S')
                    adult.birthday_day = dob.day
                    adult.birthday_month = dob.month
                    adult.birthday_year = dob.year
                    adult.sex = applicant["Sex"]
                    adult.address = ''
                    adult.primary_phone = ''
                    adult.primary_phone_answered = ''
                    adult.secondary_phone = ''
                    adult.secondary_phone_answered = ''
                    adult.wfp_case_number = ''
                    adult.csc_case_number = ''
                    adult.save()
                    return adult
            raise exp


class RegisteringChildViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):

    model = Registration
    queryset = Registration.objects.all()
    serializer_class = RegistrationChildSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return []


class RegisteringPilotView(LoginRequiredMixin, FormView):
    template_name = 'registration-pilot/registry.html'
    model = RegisteringAdult

    def get_context_data(self, **kwargs):

        return {
            'form': RegisteringAdultForm({'location': self.request.user.location_id,
                                          'locations': self.request.user.locations.all()}),
            'student_form': StudentForm
        }

    def get_success_url(self):
        return reverse('registrations:registering_pilot')


class ClassAssignmentViewSet(mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """
    Provides API operations around a class assignment record
    """
    model = Registration
    queryset = Registration.objects.all()
    serializer_class = ClassAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated,)


class WaitingListViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    Provides API operations around a registration record
    """
    model = WaitingList
    queryset = WaitingList.objects.all()
    serializer_class = WaitingListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return []

        return self.queryset


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Registration
    queryset = Registration.objects.all()

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
                line.last_education_year,
                line.last_education_level,
                line.last_year_result,
                line.section,
                line.classroom,
                line.student.phone,
                line.student.address,
                line.student.id_number,
                line.student.id_type,
                line.student.mother_nationality,
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
