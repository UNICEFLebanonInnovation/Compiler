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
)
from student_registration.students.forms import StudentForm
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.locations.models import Location

from .models import Registration, RegisteringAdult
from .serializers import (
    RegistrationSerializer,
    RegisteringAdultSerializer,
    RegistrationChildSerializer,
    ClassAssignmentSerializer
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
        school = self.request.GET.get("school", "0")
        if school:
            data = self.model.objects.filter(school=school).order_by('id')

        if not self.request.user.is_staff:
            data = data.filter(owner=self.request.user)
            self.template_name = 'registrations/index.html'

        return {
            'registrations': data,
            'classrooms': ClassRoom.objects.all(),
            'schools': School.objects.all(),
            'grades': Grade.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.all(),
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
            adult = super(RegisteringAdultViewSet, self).get_object()
            return adult
            #raise Http404()

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
                    adult.first_name =applicant["GivenName"]
                    adult.last_name = applicant["FamilyName"]
                    adult.father_name = applicant["FatherName"]
                    from datetime import datetime
                    dob = datetime.strptime(applicant["DOB"], '%Y-%m-%dT%H:%M:%S')
                    adult.birthday_day = dob.day
                    adult.birthday_month = dob.month
                    adult.birthday_year = dob.year
                    adult.sex = applicant["Sex"]
                    # adult.save()
                    return adult
            raise exp
        else:
            return adult


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


class ExportViewSet(LoginRequiredMixin, ListView):

    model = Registration
    queryset = Registration.objects.all()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(owner=self.request.user)
        return self.queryset

    def get(self, request, *args, **kwargs):

        queryset = self.queryset
        data = tablib.Dataset()
        data.headers = [
            _('Student number'), _('Student fullname'), _('Mother fullname'), _('Nationality'),
            _('Birthday'),
            # _('Day of birth'), _('Month of birth'), _('Year of birth'),
            _('Sex'),
            _('ID Type'),
            _('ID Number tooltip'), _('Phone number'), _('Student living address'),
            _('Section'),
            # , _('Grade'),
            _('Class room'),
            _('School'), _('School number'),
            _('District'), _('Governorate')
        ]

        content = []
        for line in queryset:
            if not line.student or not line.section or not line.school:
            # if not line.student or not line.classroom or not line.school:
                continue
            content = [
                line.student.number,
                line.student.__unicode__(),
                line.student.mother_fullname,
                line.student.nationality.name,
                line.student.birthday,
                # int(line.student.birthday_day),
                # int(line.student.birthday_month),
                # int(line.student.birthday_year),
                _(line.student.sex),
                line.student.id_type.name,
                line.student.id_number,
                line.student.phone,
                line.student.address,
                line.classroom.name,
                line.section.name,
                # line.grade.name,
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
