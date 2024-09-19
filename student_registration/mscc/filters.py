from django.utils.translation import ugettext as _

from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter
)

from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
    EducationService,
    Round,
    PACKAGE_TYPES
)
from student_registration.child.models import Child
from student_registration.schools.models import PartnerOrganization


class MainFilter(FilterSet):
    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    child__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Nationality')

    child__first_name = CharFilter(lookup_expr='icontains' )
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    round = ChoiceFilter(choices=Round.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Round')
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')
    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)


class FullFilter(FilterSet):

    type = ChoiceFilter(choices=PACKAGE_TYPES, empty_label='Package type')
    partner = ChoiceFilter(choices=PartnerOrganization.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Partner')
    round = ChoiceFilter(choices=Round.objects.filter(current_year=True).values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Cycle')
    center = ChoiceFilter(choices=Center.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Center')
    center__governorate = ChoiceFilter(choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name')
                                       .order_by('name').distinct(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name')
                                    .order_by('name').distinct(), empty_label='Cadaster')

    child__first_name = CharFilter(lookup_expr='icontains')
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Nationality')
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')

    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')




    class Meta:
        model = Registration
        fields = [
        ]

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)
