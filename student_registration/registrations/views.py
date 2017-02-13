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
from student_registration.registrations.forms import (
    RegisteringAdultForm,
    RegisteringChildForm,
    WaitingListForm,
    SchoolModificationForm,
)
from student_registration.students.forms import StudentForm
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.locations.models import Location

from .models import (
    Registration,
    RegisteringAdult,
    WaitingList,
    BeneficiaryChangedReason,
    ComplaintCategory
)
from .serializers import (
    RegistrationSerializer,
    RegisteringAdultSerializer,
    RegistrationChildSerializer,
    ClassAssignmentSerializer,
    WaitingListSerializer,
)
from .utils import get_unhcr_principal_applicant


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
                adults[0].signature= ''
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
                    adult.card_last_four_digits = ''
                    adult.save()
                    return adult
            raise exp

class RegisteringAdultIDViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):

    lookup_field = 'id'
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
        adults = RegisteringAdult.objects.filter(id=self.kwargs.get('id')).order_by('id')
        if adults:
            adults[0].signature = ''
            return adults[0]


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

class RegisteringAdultListSearchView(LoginRequiredMixin, TemplateView):
        """
        Provides the Household update  page with lookup types in the context
        """
        model = RegisteringAdult
        template_name = 'registration-pilot/registry-search.html'

        def get_context_data(self, **kwargs):
            data = []
            schools = []

            locations = Location.objects.all().filter(pilot_in_use=True).order_by('name')
            PAYMENTComplaintTypes = \
<<<<<<< HEAD
                ComplaintCategory.objects.all().filter(complaint_type__exact='PAYMENT').order_by('name')
=======
                ComplaintCategory.objects.all().filter(complaint_type='PAYMENT').order_by('name')
>>>>>>> develop
            CARDDISTRIBUTIONComplaintTypes = \
                ComplaintCategory.objects.all().filter(complaint_type='CARD DISTRIBUTION').order_by('name')
            CARDComplaintTypes = \
                ComplaintCategory.objects.all().filter(complaint_type='CARD').order_by('name')
            SCHOOLComplaintTypes = \
                ComplaintCategory.objects.all().filter(complaint_type='SCHOOL-RELATED').order_by('name')
            OTHERComplaintTypes = \
                ComplaintCategory.objects.all().filter(complaint_type='OTHER').order_by('name')
<<<<<<< HEAD

            # birthday_day =
            # birthday_month =
            # birthday_year =


=======
>>>>>>> develop
            location = self.request.GET.get("location", 0)
            phoneAnsweredby = RegisteringAdult.PHONE_ANSWEREDBY
            relationToHouseholdHead = RegisteringAdult.RELATION_TYPE
            beneficiaryChangedReason = BeneficiaryChangedReason.objects.all()

            addressSearchText = self.request.GET.get("addressSearchText", '')
            repSearchText = self.request.GET.get("repSearchText", '')
            idSearchText = self.request.GET.get("idSearchText", '')
            primarySearchText = self.request.GET.get("primarySearchText", '')
            secondarySearchText = self.request.GET.get("secondarySearchText", '')
            if location:
                schools = School.objects.filter(location_id=location)
                data = self.model.objects.filter(school__location_id=location,
                                                 address__icontains=addressSearchText,
                                                 first_name__icontains=repSearchText,
                                                 id_number__icontains=idSearchText,
                                                 primary_phone__icontains=primarySearchText,
                                                 secondary_phone__icontains=secondarySearchText,
                                                 ).order_by('id')[:10]

            return {
                'adults': data,
                'locations': locations,
                'selectedLocation': int(location),
                'schools': schools,
                'phoneAnsweredby': phoneAnsweredby,
                'relationToHouseholdHead': relationToHouseholdHead,
                'beneficiaryChangedReason': beneficiaryChangedReason,
                'addressSearchText': addressSearchText,
                'repSearchText': repSearchText,
                'idSearchText': idSearchText,
                'primarySearchText': primarySearchText,
                'secondarySearchText':secondarySearchText,
                'PAYMENTComplaintTypes': PAYMENTComplaintTypes,
                'CARDDISTRIBUTIONComplaintTypes': CARDDISTRIBUTIONComplaintTypes,
                'CARDComplaintTypes': CARDComplaintTypes,
                'SCHOOLComplaintTypes': SCHOOLComplaintTypes,
                'OTHERComplaintTypes': OTHERComplaintTypes,
            }


class SchoolApprovalListView(LoginRequiredMixin, TemplateView):

    model = Registration
    template_name = 'registration-pilot/list_school_modification.html'

    def get_context_data(self, **kwargs):
        data = []
        locations = Location.objects.all().filter(pilot_in_use=True).order_by('name')
        location = self.request.GET.get("location", 0)
        if location:
            data = self.model.objects.filter(school__location_id=location,school_changed_to_verify__isnull=False).order_by('id')

        return {
            'registrations': data,
            'locations': locations,
            'selectedLocation': int(location),
            'Modification_form': SchoolModificationForm
        }


class AdultChangelListView(LoginRequiredMixin, TemplateView):
    """
    Provides the adult change page with lookup types in the context
    """
    model = RegisteringAdult
    template_name = 'registration-pilot/household-change.html'

    def get_context_data(self, **kwargs):
        data = []

        locations = Location.objects.all().filter(pilot_in_use=True).order_by('name')
        location = self.request.GET.get("location", 0)

        if location:
            data = self.model.objects.filter(school__location_id=location,beneficiary_changed_verify=True).order_by('id')

        return {
            'adults': data,
            'locations': locations,
            'selectedLocation': int(location)
        }
