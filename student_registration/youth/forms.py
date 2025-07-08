from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset

from student_registration.students.models import (
    Nationality,
    IDType,
)

from student_registration.clm.models import Disability, EducationalLevel
from student_registration.adolescent.models import Adolescent
from .models import (
    Registration,
)

from student_registration.locations.models import Location

from .serializers import MainSerializer
import datetime

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))


class MainForm(forms.ModelForm):
    # YEARS = list(((str(x), x) for x in range(Adolescent.CURRENT_YEAR - 20, Adolescent.CURRENT_YEAR + 1)))
    YEARS = list(((str(x), x) for x in range(1990, Adolescent.CURRENT_YEAR + 1)))
    YEARS.insert(0, ('', '---------'))

    # center = forms.ModelChoiceField(
    #     queryset=Center.objects.all(), widget=forms.Select,
    #     label=_('Center'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    adolescent_first_name = forms.CharField(
        label=_("Youth\'s First Name"),
        widget=forms.TextInput, required=True
    )
    adolescent_father_name = forms.CharField(
        label=_("Youth\'s Father Name"),
        widget=forms.TextInput, required=True
    )
    adolescent_last_name = forms.CharField(
        label=_("Youth\'s Family Name"),
        widget=forms.TextInput, required=True
    )
    adolescent_mother_fullname = forms.CharField(
        label=_("Mother Full Name"),
        widget=forms.TextInput, required=True
    )
    adolescent_gender = forms.ChoiceField(
        label=_("Youth\'s Gender"),
        widget=forms.Select, required=True,
        choices=Adolescent.GENDER
    )
    adolescent_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select,
        label=_('Youth\'s Nationality'),
        required=True, to_field_name='id',
    )
    adolescent_nationality_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    adolescent_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
    )
    adolescent_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=Adolescent.MONTHS
    )
    adolescent_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    main_caregiver_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select,
        label=_('Caregiver Nationality'),
        required=True, to_field_name='id',
    )
    main_caregiver_nationality_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    adolescent_governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    adolescent_district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    adolescent_cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    adolescent_address = forms.CharField(
        label=_("Registered youth Home Address (Village, Street, Building/Camp, Cadaster)"),
        widget=forms.TextInput, required=False
    )
    adolescent_disability = forms.ModelChoiceField(
        label=_("Does the youth have any disability or special need?"),
        queryset=Disability.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=1
    )
    father_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        label=_('What is the father\'s educational level?'),
        required=False, to_field_name='id',
    )
    mother_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        label=_('What is the mother\'s educational level?'),
        required=False, to_field_name='id',
    )
    first_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81)|(86))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Primary phone number')
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81)|(86))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Secondary phone number')
    )
    main_caregiver = forms.ChoiceField(
        label=_("Who is the youth\'s primary caregiver?"),
        widget=forms.Select, required=True,
        choices=Adolescent.MAIN_CAREGIVER
    )
    main_caregiver_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    caregiver_first_name = forms.CharField(
        label=_("Caregiver First Name"),
        widget=forms.TextInput, required=True
    )
    caregiver_middle_name = forms.CharField(
        label=_("Caregiver Middle Name"),
        widget=forms.TextInput, required=True
    )
    caregiver_last_name = forms.CharField(
        label=_("Caregiver Last Name"),
        widget=forms.TextInput, required=True
    )
    caregiver_mother_name = forms.CharField(
        label=_("Caregiver Mother Full Name"),
        widget=forms.TextInput, required=False
    )
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.filter(active=True),
        initial=13,
        widget=forms.Select,
        label=_('ID type of the caregiver'),
        required=True, to_field_name='id',

    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a))-[0-9]{2}[C-](?:\d{5}|\d{6})$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX or XXX-XX-XXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Cargiver Individual ID from the certificate')
    )

    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the youth from the certificate')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a))-[0-9]{2}[C-](?:\d{5}|\d{6})$|^LB-\d{3}-\d{6}|\d{7}$|^86A-\d{2}-\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX or LB-XXX-XXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the youth')
    )
    parent_extract_record = forms.CharField(
        label=_('Lebanese Extract of Record'),
        widget=forms.TextInput, required=False
    )

    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the youth')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the youth')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the Cargiver')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Cargiver')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Cargiver')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Cargiver')
    )
    other_number = forms.CharField(
        required=False,
        label=_('ID number of the youth')
    )
    unrwa_number = forms.CharField(
        required=False,
        label=_('UNRWA Case number')
    )
    adolescent_id = forms.CharField(widget=forms.HiddenInput, required=False)
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    adolescent_outreach = forms.IntegerField(widget=forms.HiddenInput, required=False)
    student_old = forms.IntegerField(widget=forms.HiddenInput, required=False)
    partner_name = forms.CharField(widget=forms.HiddenInput, required=False)
    type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MainForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('youth:child_add')
        if instance:
            display_registry = ' d-none'
            form_action = reverse('youth:child_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('adolescent_first_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('adolescent_father_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('adolescent_last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('adolescent_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('adolescent_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('adolescent_birthday_day', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('adolescent_gender', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('adolescent_mother_fullname', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('adolescent_nationality', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('adolescent_nationality_other', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('adolescent_governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('adolescent_district', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('adolescent_cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('adolescent_address', css_class='col-md-6'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('adolescent_disability', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                css_id='step-1',
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('father_educational_level', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('mother_educational_level', css_class='col-md-6'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('first_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">5</span>'),
                    Div('main_caregiver', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('main_caregiver_other', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">6</span>'),
                    Div('caregiver_first_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">7</span>'),
                    Div('caregiver_middle_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">8</span>'),
                    Div('caregiver_last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">9</span>'),
                    Div('caregiver_mother_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('main_caregiver_nationality_other', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('id_type', css_class='col-md-6'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('case_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_individual_case_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('individual_case_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('recorded_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_syrian_national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('syrian_national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_sop_national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('sop_national_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_other_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('other_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id6',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('parent_extract_record', css_class='col-md-5'),
                    css_class='row card-body child_id child_id7',
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('unrwa_number', css_class='col-md-5'),
                    css_class='row card-body child_id child_id8',
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),

                ),
                css_id='step-2',
            )
        )

    def clean(self):
        cleaned_data = super(MainForm, self).clean()

        # check if date is valid
        year = 0
        month = 0
        day = 0
        if cleaned_data.get("adolescent_birthday_year"):
            year = int(cleaned_data.get("adolescent_birthday_year"))
        if cleaned_data.get("adolescent_birthday_month"):
            month = int(cleaned_data.get("adolescent_birthday_month"))
        if cleaned_data.get("adolescent_birthday_day"):
            day = int(cleaned_data.get("adolescent_birthday_day"))

        try:
            datetime.datetime(year, month, day)
        except ValueError:
            self.add_error('adolescent_birthday_year', 'The date is not valid.')

        adolescent_nationality = cleaned_data.get("adolescent_nationality")
        adolescent_nationality_other = cleaned_data.get("adolescent_nationality_other")
        if adolescent_nationality and adolescent_nationality.id == 6 and not adolescent_nationality_other:
            self.add_error('adolescent_nationality_other', 'This field is required')

        main_caregiver = cleaned_data.get("main_caregiver")
        main_caregiver_other = cleaned_data.get("main_caregiver_other")
        if main_caregiver == 'Other' and not main_caregiver_other:
            self.add_error('main_caregiver_other', 'This field is required')

        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        if main_caregiver_nationality and main_caregiver_nationality.id == 6 and not main_caregiver_nationality_other:
            self.add_error('main_caregiver_nationality_other', 'This field is required')

    def save(self, request=None, instance=None):

        from student_registration.students.utils import generate_one_unique_id

        if instance:
            serializer = MainSerializer(instance, data=request.POST)
            if serializer.is_valid():
                old_dob_year = instance.adolescent.birthday_year
                old_dob_month = instance.adolescent.birthday_month
                old_dob_age = instance.adolescent
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = MainSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.modified_by = request.user
                instance.partner = request.user.partner
                instance.center = request.user.center
                # if request.POST.get("adolescent_outreach"):
                #     instance.adolescent_outreach = request.POST.get("adolescent_outreach")
                # if request.POST.get("adolescent_old"):
                #     instance.student_old = request.POST.get("adolescent_old")
                instance.save()
                request.session['instance_id'] = instance.id

                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        if instance:
            instance.adolescent.unicef_id = generate_one_unique_id(
                str(instance.adolescent.pk),
                instance.adolescent.first_name,
                instance.adolescent.father_name,
                instance.adolescent.last_name,
                instance.adolescent.mother_fullname,
                instance.adolescent.birthdate,
                instance.adolescent.nationality_name_en,
                instance.adolescent.gender
            )
            instance.adolescent.save()

        return instance

    class Meta:
        model = Registration
        fields = (
            'adolescent_outreach',
            'student_old',
            'adolescent_first_name',
            'adolescent_father_name',
            'adolescent_last_name',
            'adolescent_mother_fullname',
            'adolescent_gender',
            'adolescent_nationality',
            'adolescent_nationality_other',
            'adolescent_birthday_year',
            'adolescent_birthday_month',
            'adolescent_birthday_day',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'adolescent_governorate',
            'adolescent_district',
            'adolescent_cadaster',
            'adolescent_address',
            'adolescent_disability',
            'father_educational_level',
            'mother_educational_level',
            'first_phone_number',
            'second_phone_number',
            'main_caregiver',
            'main_caregiver_other',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'id_type',
            'case_number',
            'parent_individual_case_number',
            'individual_case_number',
            'parent_extract_record',
            'recorded_number',
            'parent_national_number',
            'national_number',
            'parent_syrian_national_number',
            'syrian_national_number',
            'parent_sop_national_number',
            'sop_national_number',
            'parent_other_number',
            'other_number',
            'unrwa_number'
        )
