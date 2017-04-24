# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.http import Http404
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Value as V
from django.db.models import Q
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from datetime import datetime
from django.utils import formats
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
    ComplaintCategory,
    Complaint,
    HouseholdNotFound,
    NotEligibleReason,
    MissingChild
)
from .serializers import (
    RegistrationSerializer,
    RegisteringAdultSerializer,
    RegistrationChildSerializer,
    ClassAssignmentSerializer,
    WaitingListSerializer,
    ComplaintSerializer,
    HouseholdNotFoundSerializer,
    ComplaintCategorySerializer,
    MissingChildSerializer
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


class RegisteringComplaintViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):

    model = Complaint
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = (permissions.IsAuthenticated,)


    def put(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RegisteringComplaintCategoryViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):

    model = ComplaintCategory
    queryset = ComplaintCategory.objects.all()
    serializer_class = ComplaintCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class RegisteringNotFoundViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    model = HouseholdNotFound
    queryset = HouseholdNotFound.objects.all()
    serializer_class = HouseholdNotFoundSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MissingChildViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    model = MissingChild
    queryset = MissingChild.objects.all()
    serializer_class = MissingChildSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
            payment_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Payment').order_by('name')
            card_distribution_cmplaint_types= \
                ComplaintCategory.objects.all().filter(complaint_type='Card Distribution').order_by('name')
            card_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Card').order_by('name')
            school_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='School Related').order_by('name')
            other_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Other').order_by('name')
            bank_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Bank').order_by('name')
            reinstate_beneficiary_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Reinstate Beneficiary').order_by('name')
            not_found_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Not Found').order_by('name')
            missingChild_complaint_types = \
                ComplaintCategory.objects.all().filter(complaint_type='Missing Student').order_by('name')
            months = Person.MONTHS
            location = self.request.GET.get("location", 0)
            phoneAnsweredby = RegisteringAdult.PHONE_ANSWEREDBY
            relationToHouseholdHead = RegisteringAdult.RELATION_TYPE
            complaint_status = Complaint.STATUS
            gender = RegisteringAdult.GENDER
            beneficiaryChangedReason = BeneficiaryChangedReason.objects.all()
            not_eligible_reason = NotEligibleReason.objects.all()
            addressSearchText = self.request.GET.get("addressSearchText", '')
            repSearchText = self.request.GET.get("repSearchText", '')
            idSearchText = self.request.GET.get("idSearchText", '')
            primarySearchText = self.request.GET.get("primarySearchText", '')
            secondarySearchText = self.request.GET.get("secondarySearchText", '')
            idType = IDType.objects.all().filter(inuse=True).order_by('name')

            schools = School.objects.all().order_by('name')

            if location > 0:
                data = self.model.objects.annotate(
                    name=Concat('first_name', V(' '), 'father_name', V(' '), 'last_name'),
                ).filter(school__location_id=location,
                         address__icontains=addressSearchText,
                         name__icontains=repSearchText,
                         id_number__icontains=idSearchText,
                         primary_phone__icontains=primarySearchText,
                         secondary_phone__icontains=secondarySearchText,
                         ).order_by('id')[:200]
            else:
                data = self.model.objects.annotate(
                    name=Concat('first_name', V(' '), 'father_name', V(' '), 'last_name'),
                ).filter(address__icontains=addressSearchText,
                         name__icontains=repSearchText,
                         id_number__icontains=idSearchText,
                         primary_phone__icontains=primarySearchText,
                         secondary_phone__icontains=secondarySearchText,
                         ).order_by('id')[:200]


            return {
                'adults': data,
                'locations': locations,
                'selectedLocation': int(location),
                'schools': schools,
                'phoneAnsweredby': phoneAnsweredby,
                'idType': idType,
                'relationToHouseholdHead': relationToHouseholdHead,
                'gender': gender,
                'beneficiaryChangedReason': beneficiaryChangedReason,
                'addressSearchText': addressSearchText,
                'repSearchText': repSearchText,
                'idSearchText': idSearchText,
                'primarySearchText': primarySearchText,
                'secondarySearchText':secondarySearchText,
                'payment_complaint_types': payment_complaint_types,
                'card_distribution_cmplaint_types': card_distribution_cmplaint_types,
                'card_complaint_types': card_complaint_types,
                'school_complaint_types': school_complaint_types,
                'other_complaint_types': other_complaint_types,
                'months': months,
                'complaint_status': complaint_status,
                'bank_complaint_types': bank_complaint_types,
                'reinstate_beneficiary_complaint_types': reinstate_beneficiary_complaint_types,
                'not_found_complaint_types': not_found_complaint_types,
                'missingChild_complaint_types': missingChild_complaint_types,
                'not_eligible_reason': not_eligible_reason
            }

class ComplaintCategoryListSearchView(LoginRequiredMixin, TemplateView):

    model = ComplaintCategory
    template_name = 'registration-pilot/compalints-search.html'

    def get_context_data(self, **kwargs):

        data = []

        data = self.model.objects.order_by('complaint_type')
        complaintStatistics = []
        complaintStatisticsTotal = ComplaintStatistics()
        complaintStatisticsTotal.Name = 'TOTAL'
        complaintStatisticsTotal.Statistics = 0
        complaintStatisticsTotal.statistics_urgent = 0


        for record in data:
            complaintStatisticsRecord = ComplaintStatistics()
            complaintStatisticsRecord.ID = record.id
            complaintStatisticsRecord.Name = record.name
            complaintStatisticsRecord.complaint_type = record.complaint_type
            complaintStatisticsRecord.Statistics = record.complaint_count(self.request.user)
            complaintStatisticsRecord.statistics_urgent = record.complaint_urgent_count(self.request.user)

            complaintStatistics.append(complaintStatisticsRecord)
            complaintStatisticsTotal.Statistics += complaintStatisticsRecord.Statistics
            complaintStatisticsTotal.statistics_urgent += complaintStatisticsRecord.statistics_urgent

        students=[]
        school_changed_to_verify = []

        school_changed_to_verify = ComplaintStatistics()
        school_changed_to_verify.complaint_type = 'Update'
        school_changed_to_verify.Name = 'Change of school'
        school_changed_to_verify.Statistics = 0

        students = Registration.objects
        if not self.request.user.is_superuser:
            students = students.filter(school__location__parent_id=self.request.user.governante_id)

        students = students.filter(school_changed_to_verify__isnull=False).order_by('id')
        for student in students:
            school_changed_to_verify.Statistics += 1
        complaintStatisticsTotal.Statistics += school_changed_to_verify.Statistics

        beneficiaries=[]
        beneficiary_changed_verify = []

        beneficiary_changed_verify = ComplaintStatistics()
        beneficiary_changed_verify.complaint_type = 'Update'
        beneficiary_changed_verify.Name = 'Change of benefeciary'
        beneficiary_changed_verify.Statistics = 0

        beneficiaries = RegisteringAdult.objects
        if not self.request.user.is_superuser:
            beneficiaries = beneficiaries.filter(school__location__parent_id=self.request.user.governante_id)
        # beneficiaries = beneficiaries.filter(beneficiary_changed_verify=True).order_by('id')
        beneficiaries = beneficiaries.filter(beneficiary_changed_father_name__isnull= False).order_by('id')

        for beneficiary in beneficiaries:
            beneficiary_changed_verify.Statistics += 1
        complaintStatisticsTotal.Statistics += beneficiary_changed_verify.Statistics

        cards = []
        cards_duplicate = []

        cards_duplicate = ComplaintStatistics()
        cards_duplicate.complaint_type = 'Update'
        cards_duplicate.Name = 'Two Cards'
        cards_duplicate.Statistics = 0

        cards = RegisteringAdult.objects
        if not self.request.user.is_superuser:
            cards = cards.filter(school__location__parent_id=self.request.user.governante_id)
        cards = cards.filter(duplicate_card_first_card_case_number__isnull=False).order_by('id')

        for card in cards:
            cards_duplicate.Statistics += 1
        complaintStatisticsTotal.Statistics += cards_duplicate.Statistics

        return {
            'complaints': complaintStatistics,
            'school_changed_to_verify': school_changed_to_verify,
            'beneficiary_changed_verify': beneficiary_changed_verify,
            'cards_duplicate':cards_duplicate,
            'total': complaintStatisticsTotal
        }

class ComplaintStatistics:

    def __init__(self, *args, **kwargs):

        self.ID = None
        self.Name = ''
        self.complaint_type = ''
        self.Statistics = 0
        self.statistics_urgent = 0


class ComplaintsGridView(LoginRequiredMixin, TemplateView):

    model = Complaint
    template_name = 'registration-pilot/compalints-grid.html'

    def get_context_data(self, **kwargs):

        CategoryID = self.request.GET.get('CategoryID', 0)
        ComplaintType = self.request.GET.get('ComplaintType', '')
        ComplaintSubType = self.request.GET.get('ComplaintSubType', '')

        complaint_records = Complaint.objects

        if not self.request.user.is_superuser:
            complaint_records = complaint_records.filter(complaint_adult__school__location__parent_id=self.request.user.governante_id)

        complaint_records = complaint_records.filter(complaint_category=CategoryID, complaint_category__name=ComplaintSubType)

        return {
            'complaints': complaint_records,
            'ComplaintType': ComplaintType,
            'ComplaintSubType': ComplaintSubType
        }


class ChangeBeneficiaryGridView(LoginRequiredMixin, TemplateView):

    template_name = 'registration-pilot/changebeneficiary-grid.html'

    def get_context_data(self, **kwargs):

        # beneficiarRecords = RegisteringAdult.objects.filter(beneficiary_changed_verify=True)

        beneficiarRecords = RegisteringAdult.objects.filter(beneficiary_changed_father_name__isnull= False).order_by('id')

        if not self.request.user.is_superuser:
            beneficiarRecords = beneficiarRecords.filter(school__location__parent_id=self.request.user.governante_id)

        return {
            'beneficiaries': beneficiarRecords,
        }

class ChangeTwoCardsGridView(LoginRequiredMixin, TemplateView):

    template_name = 'registration-pilot/twocards-grid.html'

    def get_context_data(self, **kwargs):

        beneficiaryRecords = RegisteringAdult.objects.filter(duplicate_card_first_card_case_number__isnull= False).order_by('id')

        if not self.request.user.is_superuser:
            beneficiaryRecords = beneficiaryRecords.filter(school__location__parent_id=self.request.user.governante_id)

        return {
            'beneficiaries': beneficiaryRecords,
        }



class SchoolApprovalListView(LoginRequiredMixin, TemplateView):

    template_name = 'registration-pilot/students-grid.html'

    def get_context_data(self, **kwargs):
        student_records = Registration.objects.filter(school_changed_to_verify__isnull=False)

        if not self.request.user.is_superuser:
            student_records = student_records.filter(school__location__parent_id=self.request.user.governante_id)
        return {
            'students': student_records,
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


class ComplaintsExportViewSet(LoginRequiredMixin, ListView):
    model = Complaint

    def get(self, request, *args, **kwargs):

        CategoryID = self.request.GET.get('CategoryID', 0)
        ComplaintType = self.request.GET.get('ComplaintType', '')
        ComplaintSubType = self.request.GET.get('ComplaintSubType', '')

        queryset = self.model.objects.all()
        queryset = queryset.order_by('id')

        data = tablib.Dataset()

        headerFields = []

        headerFields.append(_('ID'))
        headerFields.append(_('ID  Case'))
        headerFields.append(_('HH Rep Name'))

        if ComplaintSubType == 'Other Card Issues':
            headerFields.append(_('Other-Specify'))

        if ComplaintType == 'School Related':
            headerFields.append(_('Student'))

        headerFields.append(_('Date of Complaint'))

        if ComplaintType != 'Not Found':
            headerFields.append(_(' Phone #'))

        if ComplaintType == 'Bank':
            headerFields.append(_(' Date/Time of incident'))
            headerFields.append(_(' Phone number from which call was placed'))
            headerFields.append(_('Service requested'))

        if ComplaintType != 'Card':
                headerFields.append(_('Complaint Comment'))

        if ComplaintType == 'Missing Student':
            headerFields.append(_('Student'))

        if ComplaintType == 'Payment':
            headerFields.append(_('Enumerator '))

        headerFields.append(_(' Solution Comments'))

        data.headers = headerFields


        complaint_records = Complaint.objects.filter(complaint_status='rejected')

        # if not self.request.user.is_superuser:
        #     complaint_records = complaint_records.filter(complaint_adult__school__location__parent_id=self.request.user.governante_id)

        complaint_records = complaint_records.filter(complaint_category=CategoryID, complaint_category__name=ComplaintSubType)


        content = []
        for line in complaint_records:
            # if not line.student or not line.school:
            # continue
            content = []

            content.append(line.id)

            if ComplaintType != 'Not Found':
                content.append(line.complaint_adult.id_number)
                content.append(
                    line.complaint_adult.first_name
                    + ' '
                    + line.complaint_adult.father_name
                    + ' '
                    + line.complaint_adult.last_name
                )
            else:
                content.append(line.household_not_found.id_number)
                content.append(
                    line.household_not_found.first_name
                    + ' '
                    + line.household_not_found.father_name
                    + ' '
                    + line.household_not_found.last_name
                )

            date_created = line.created
            formatted_datetime_created = formats.date_format(date_created, "SHORT_DATETIME_FORMAT")
            content.append(formatted_datetime_created)

            if ComplaintSubType == 'Other Card Issues':
                content.append(line.complaint_Other_type_specify)

            if ComplaintType == 'School Related':
                content.append(
                    line.complaint_student_refused_entrance.first_name
                    + ' '
                    + line.complaint_student_refused_entrance.father_name
                    + ' '
                    + line.complaint_student_refused_entrance.last_name
                )

            if ComplaintType != 'Not Found':
                content.append(line.complaint_adult.primary_phone)

            if ComplaintType == 'Bank':
                date_bank = line.complaint_bank_date_of_incident
                formatted_datetime_bank = formats.date_format(date_bank, "SHORT_DATETIME_FORMAT")
                content.append(formatted_datetime_bank)
                content.append(line.complaint_bank_phone_used)
                content.append(line.complaint_bank_service_requested)

            if ComplaintType != 'Card':
                content.append(line.complaint_note)

            if ComplaintType == 'Missing Student':
                content.append(line.missing_child.first_name
                               + ' ' + line.missing_child.father_name
                               + ' ' + line.missing_child.last_name)

            if ComplaintType == 'Payment':
                content.append(line.owner.first_name
                               + ' ' + line.owner.father_name)

            content.append(line.complaint_solution)
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=complaint_list.xls'
        return response
