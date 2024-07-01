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
    Program,
    SubProgram,
    Donor
)
from student_registration.child.models import Child
from student_registration.schools.models import PartnerOrganization
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

    partner = ChoiceFilter(choices=PartnerOrganization.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Partner')
    center__governorate = ChoiceFilter(choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name')
                                       .order_by('name').distinct(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name')
                                    .order_by('name').distinct(), empty_label='Cadaster')

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__number = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Nationality')

    adolescent__disability = ChoiceFilter(choices=Disability.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Disability')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')


    program = ChoiceFilter(choices=Program.objects.values_list('id', 'name'),
                                  field_name='enrolled_programs__program',
                                  empty_label='Program', method='filter_by_program')

    sub_program = ChoiceFilter(choices=SubProgram.objects.values_list('id', 'name'),
                                  field_name='enrolled_programs__sub_program',
                                  empty_label='Sub Program', method='filter_by_sub_program')

    donor = ChoiceFilter(choices=Donor.objects.values_list('id', 'name'),
                           field_name='enrolled_programs__donor',
                           empty_label='Donor', method='filter_by_donor')

    # completion_date = DateFromToRangeFilter(field_name='enrolled_programs__completion_date', label='Completion Date Range',
    #                                    widget=RangeWidget(attrs={'type': 'date'}))



    start_date = DateFilter(field_name='enrolled_programs__completion_date',
                            widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='enrolled_programs__completion_date',
                          widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                          lookup_expr='lte', label='End Date')

    class Meta:
        model = Registration
        fields = [
        ]

    def filter_by_program(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program=value)

    def filter_by_sub_program(self, queryset, name, value):
        return queryset.filter(enrolledprograms__sub_program=value)

    def filter_by_donor(self, queryset, name, value):
        return queryset.filter(enrolledprograms__donor=value)
