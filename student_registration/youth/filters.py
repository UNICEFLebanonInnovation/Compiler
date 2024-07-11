from django import forms
from django.utils.translation import ugettext as _
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    DateFromToRangeFilter,
    DateFilter
)

import datetime

from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
    EnrolledPrograms,
    MasterProgram,
    SubProgram,
    Donor,
    ProgramDocument,
    Partner,
    FundedBy,
    FocalPoint
)
from student_registration.youth.models import Adolescent
from student_registration.clm.models import Disability, EducationalLevel



class MainFilter(FilterSet):
    adolescent__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Nationality')

    adolescent__first_name = CharFilter(lookup_expr='icontains' )
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__number = CharFilter(lookup_expr='icontains')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]


class FullFilter(FilterSet):
    partner = ChoiceFilter(choices=Partner.objects.values_list('id', 'name').order_by('name').distinct(), empty_label='Partner')
    center__governorate = ChoiceFilter(choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name').order_by('name').distinct(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name').order_by('name').distinct(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name').order_by('name').distinct(), empty_label='Cadaster')

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__number = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name').order_by('name').distinct(), empty_label='Nationality')

    adolescent__disability = ChoiceFilter(choices=Disability.objects.values_list('id', 'name').order_by('name').distinct(), empty_label='Disability')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    master_program = ChoiceFilter(choices=MasterProgram.objects.values_list('id', 'name'), field_name='enrolled_programs__master_program', empty_label='Master Program', method='filter_by_master_program')
    sub_program = ChoiceFilter(choices=SubProgram.objects.values_list('id', 'name'), field_name='enrolled_programs__sub_program', empty_label='Sub Program', method='filter_by_sub_program')
    donor = ChoiceFilter(choices=Donor.objects.values_list('id', 'name'), field_name='enrolled_programs__donor', empty_label='Donor', method='filter_by_donor')
    program_document = ChoiceFilter(choices=ProgramDocument.objects.values_list('id', 'project_name'), field_name='enrolled_programs__program_document', empty_label='Program Document', method='filter_by_program_document')

    #
    start_date = DateFilter(field_name='enrolled_programs__completion_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='enrolled_programs__completion_date',
                          lookup_expr='lte', label='End Date')


    # start_date = DateFilter(field_name='enrolled_programs__completion_date', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Start Date'}), lookup_expr='gte', label='Start Date')
    # end_date = DateFilter(field_name='enrolled_programs__completion_date', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'End Date'}), lookup_expr='lte', label='End Date')

    class Meta:
        model = Registration
        fields = []

    def filter_by_master_program(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program=value)

    def filter_by_sub_program(self, queryset, name, value):
        return queryset.filter(enrolled_programs__sub_program=value)

    def filter_by_donor(self, queryset, name, value):
        return queryset.filter(enrolled_programs__donor=value)

    def filter_by_program_document(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program_document=value)


class PDFilter(FilterSet):
    partner__name = ChoiceFilter(choices=Partner.objects.values_list('id', 'short_name')
                                .order_by('short_name').distinct(), empty_label='Partner')
    funded_by__name = ChoiceFilter(choices=FundedBy.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Funded By')

    project_status = CharFilter(lookup_expr='icontains')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point__name = ChoiceFilter(choices=FocalPoint.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Focal Point')

    start_date = DateFilter(field_name='start_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='end_date',
                          lookup_expr='lte', label='End Date')

    class Meta:
        model = ProgramDocument
        fields = [
        ]

