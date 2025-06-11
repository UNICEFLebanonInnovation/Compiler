from django import forms
from django.utils.translation import gettext as _
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    DateFromToRangeFilter,
    DateFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter
)
from django.db.models import Q
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
    ProjectStatus,
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
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]


class FullFilter(FilterSet):
    partner = ChoiceFilter(
        choices=Partner.objects.values_list('id', 'name').order_by('name').distinct(),
        empty_label='Partner'
    )
    adolescent__governorate = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name').order_by('name').distinct(),
        empty_label='Governorate'
    )
    adolescent__caza = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name').order_by('name').distinct(),
        empty_label='Caza'
    )
    adolescent__cadaster = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name').order_by('name').distinct(),
        empty_label='Cadaster'
    )

    adolescent__first_name = CharFilter(lookup_expr='icontains')
    adolescent__father_name = CharFilter(lookup_expr='icontains')
    adolescent__last_name = CharFilter(lookup_expr='icontains')
    adolescent__number = CharFilter(lookup_expr='icontains')
    adolescent__unicef_id = CharFilter(lookup_expr='icontains')
    adolescent__gender = ChoiceFilter(choices=Adolescent.GENDER, empty_label='Gender')
    adolescent__nationality = ChoiceFilter(
        choices=Nationality.objects.values_list('id', 'name').order_by('name').distinct(),
        empty_label='Nationality'
    )

    adolescent__disability = ChoiceFilter(
        choices=Disability.objects.values_list('id', 'name').order_by('name').distinct(),
        empty_label='Disability'
    )
    adolescent__first_phone_number = CharFilter(lookup_expr='icontains')

    master_program = MultipleChoiceFilter(
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))
            for mp in MasterProgram.objects.filter(active=True
                                                   # , created__year=datetime.datetime.now().year
                                                   )
        ],
        field_name='enrolled_programs__master_program',
        label='Master Program',
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'wide-dropdown'})
    )

    sub_program = MultipleChoiceFilter(
        choices=lambda: [
            (sp.id, "{} - {}".format(sp.number, sp.name))
            for sp in SubProgram.objects.filter(master_program__active=True
                                                # ,created__year=datetime.datetime.now().year
                                                )
        ],
        field_name='enrolled_programs__sub_program',
        label='Sub Program',
        method='filter_by_sub_program',
        widget=forms.SelectMultiple(attrs={'class': 'wide-dropdown'})
    )

    # sub_program = MultipleChoiceFilter(
    #     choices=lambda: [
    #         (sp.id, "{} - {}".format(sp.number, sp.name))
    #         for sp in SubProgram.objects.filter(created__year=datetime.datetime.now().year)
    #     ],
    #     field_name='enrolled_programs__sub_program',
    #     label='Sub Program',
    #     method='filter_by_sub_program',
    #     widget=forms.CheckboxSelectMultiple(attrs={'class': 'wide-checkbox'})
    # )

    donor = ChoiceFilter(
        field_name='enrolled_programs__donor',
        choices=Donor.objects.values_list('id', 'name'),
        empty_label='Donor',
        method='filter_by_donor'
    )
    program_document = ChoiceFilter(
        field_name='enrolled_programs__program_document',
        choices=ProgramDocument.objects.values_list('id', 'project_name'),
        empty_label='Program Document',
        method='filter_by_program_document'
    )

    start_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='gte', label='Start Date'
    )
    end_date = DateFilter(
        field_name='enrolled_programs__completion_date',
        lookup_expr='lte', label='End Date'
    )

    class Meta:
        model = Registration
        fields = []

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__master_program__in=value)
        return queryset

    def filter_by_sub_program(self, queryset, name, value):
        if value:
            return queryset.filter(enrolled_programs__sub_program__in=value)
        return queryset

    def filter_by_donor(self, queryset, name, value):
        return queryset.filter(enrolled_programs__donor=value)

    def filter_by_program_document(self, queryset, name, value):
        return queryset.filter(enrolled_programs__program_document=value)


class PDFilter(FilterSet):
    current_year = datetime.datetime.now().year
    partner = ChoiceFilter(choices=Partner.objects.filter(active=True).values_list('id', 'short_name')
                                .order_by('short_name').distinct(), empty_label='Partner')
    funded_by = ChoiceFilter(choices=FundedBy.objects.filter(active=True).values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=ProjectStatus.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=FocalPoint.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Focal Point')

    start_date = DateFilter(field_name='start_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='end_date',
                          lookup_expr='lte', label='End Date')
    donors = ModelChoiceFilter(
        queryset=Donor.objects.filter(active=True).all(),
        label='Donors',
        required=False,
        empty_label='Select a Donor'
    )
    master_program = MultipleChoiceFilter(
        choices=lambda: [
            (mp.id, "{} - {}".format(mp.number, mp.name))  # Format as "number - name"
            for mp in MasterProgram.objects.filter(
                active=True
                # , created__year=datetime.datetime.now().year
            )
        ],
        label='Master Program',
        required=False,
        method='filter_by_master_program',
        widget=forms.SelectMultiple(attrs={'class': 'wide-checkbox'})
    )

    class Meta:
        model = ProgramDocument
        fields = [
        ]

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(master_program1__in=value) |
                Q(master_program2__in=value) |
                Q(master_program3__in=value)
            )
        return queryset


class PDPartnerFilter(FilterSet):
    current_year = datetime.datetime.now().year
    partner = ChoiceFilter(choices=Partner.objects.filter(active=True).values_list('id', 'short_name')
                                .order_by('short_name').distinct(), empty_label='Partner')
    funded_by = ChoiceFilter(choices=FundedBy.objects.filter(active=True).values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Funded By')
    project_status = ChoiceFilter(choices=ProjectStatus.objects.values_list('id', 'name')
                                  .order_by('name').distinct(), empty_label='Status')
    project_code = CharFilter(lookup_expr='icontains')
    project_name = CharFilter(lookup_expr='icontains')
    implementing_partners = CharFilter(lookup_expr='icontains')
    focal_point = ChoiceFilter(choices=FocalPoint.objects.values_list('id', 'name')
                                 .order_by('name').distinct(), empty_label='Focal Point')

    start_date = DateFilter(field_name='start_date',
                            lookup_expr='gte', label='Start Date')
    end_date = DateFilter(field_name='end_date',
                          lookup_expr='lte', label='End Date')

    master_program = MultipleChoiceFilter(
        choices=lambda: [(mp.id, mp.name) for mp in MasterProgram.objects.filter(
            active=True
            # ,created__year=datetime.datetime.now().year
        )],
        label='Master Program',
        required=False,
        method='filter_by_master_program'
    )

    class Meta:
        model = ProgramDocument
        fields = [
        ]

    def filter_by_master_program(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(master_program1__in=value) |
                Q(master_program2__in=value) |
                Q(master_program3__in=value)
            )
        return queryset
