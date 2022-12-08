from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete

from student_registration.students.models import (
    Nationality,
    IDType,
)

from student_registration.locations.models import Center
from student_registration.clm.models import Disability, EducationalLevel
from student_registration.child.models import Child
from .models import (
    Registration,
    EducationAssessment
)
from .serializers import MainSerializer

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))


class MainForm(forms.ModelForm):
    YEARS = list(((str(x), x) for x in range(Child.CURRENT_YEAR - 20, Child.CURRENT_YEAR - 3)))
    YEARS.insert(0, ('', '---------'))

    center = forms.ModelChoiceField(
        queryset=Center.objects.all(), widget=forms.Select,
        label=_('Center'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    child_first_name = forms.CharField(
        label=_("Child\'s First Name"),
        widget=forms.TextInput, required=True
    )
    child_father_name = forms.CharField(
        label=_("Child\'s Father Name"),
        widget=forms.TextInput, required=True
    )
    child_last_name = forms.CharField(
        label=_("Child\'s Family Name"),
        widget=forms.TextInput, required=True
    )
    child_mother_fullname = forms.CharField(
        label=_("Child\'s Mother Full Name"),
        widget=forms.TextInput, required=True
    )
    child_gender = forms.ChoiceField(
        label=_("Child\'s Gender"),
        widget=forms.Select, required=True,
        choices=Child.GENDER
    )
    child_nationality = forms.ModelChoiceField(
        label=_("Child\'s Nationality"),
        queryset=Nationality.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    child_nationality_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
    )
    child_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=Child.MONTHS
    )
    child_birthday_day = forms.ChoiceField(
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
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    child_p_code = forms.CharField(
        label=_('Insert Pcode if the child lives in Internal Settlement/Camp'),
        widget=forms.TextInput, required=False
    )
    child_address = forms.CharField(
        label=_("Registered child Home Address (Village, Street, Building/Camp, Cadaster)"),
        widget=forms.TextInput, required=True
    )
    child_disability = forms.ModelChoiceField(
        label=_("Does the child have any disability or special need?"),
        queryset=Disability.objects.all(), widget=forms.Select,
        required=False, to_field_name='id',
    )
    child_marital_status = forms.ChoiceField(
        label=_('Child\'s Marital Status '),
        widget=forms.Select, required=True,
        choices=Child.MARITAL_STATUS,
        initial='Single'
    )
    child_have_children = forms.ChoiceField(
        label=_("Does the child have children?"),
        widget=forms.Select, required=True,
        choices=Child.YES_NO
    )
    child_number_children = forms.IntegerField(
        label=_('How many?'),
        widget=forms.TextInput, required=False
    )
    source_of_identification = forms.ChoiceField(
        label=_("Source of referral of the child to MSCC"),
        widget=forms.Select,
        required=True,
        choices=Registration.IDENTIFICATION_SOURCE,
        initial=''
    )
    source_of_identification_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    cash_support_programmes = forms.MultipleChoiceField(
        label=_('Cash support programmes that the child is already benefitting from.'),
        choices=Registration.CASH_SUPPORT_PROGRAMMES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    father_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        label=_('What is the father\'s educational level?'),
        required=True, to_field_name='id',
    )
    mother_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(), widget=forms.Select,
        label=_('What is the mother\'s educational level?'),
        required=True, to_field_name='id',
    )
    first_phone_owner = forms.ChoiceField(
        label=_("Who will be answering the phone?"),
        widget=forms.Select,
        required=True,
        choices=Child.PHONE_OWNER,
        initial=''
    )
    first_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Primary phone number')
    )
    first_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Confirm primary phone number')
    )
    second_phone_owner = forms.ChoiceField(
        label=_("Who will be answering the phone?"),
        widget=forms.Select,
        required=False,
        choices=Child.PHONE_OWNER,
        initial=''
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Primary phone number')
    )
    second_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Confirm primary phone number')
    )
    main_caregiver = forms.ChoiceField(
        label=_("Who is the Child\'s primary caregiver?"),
        widget=forms.Select, required=True,
        choices=Child.MAIN_CAREGIVER
    )
    main_caregiver_other = forms.CharField(
        label=_('Please specify'),
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
        label=_("Caretaker Mother\'s Full Name"),
        widget=forms.TextInput, required=True
    )
    have_labour = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=Registration.HAVE_LABOUR,
        initial='no'
    )
    labour_type = forms.ChoiceField(
        label=_('What is the type of work?'),
        widget=forms.Select, required=False,
        choices=Registration.LABOURS
    )
    labour_type_specify = forms.CharField(
        label=_('Please specify (hotel, restaurant, transport, '
                'personal services such as cleaning, hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )
    labour_hours = forms.IntegerField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=0
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('How much does the child get paid per week?'),
        widget=forms.Select,
        choices=Registration.LABOUR_INCOME,
        initial='',
        required=False
    )
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(), widget=forms.Select,
        label=_('ID type of the caregiver'),
        required=True, to_field_name='id'
    )
    case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Case Number')
    )
    case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Case Number')
    )
    parent_individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    parent_individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Caretaker Individual ID from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Confirm Individual ID of the Child from the certificate (Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb)|(LB2)|(lb2)|(LBE)|(lbe))-[0-9][0-9]([C]\d{5})|(-[0-9][0-9][0-9][0-9][0-9])$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb)|(LB2)|(lb2)|(LBE)|(lbe))-[0-9][0-9]([C]\d{5})|(-[0-9][0-9][0-9][0-9][0-9])$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )
    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child (Optional)')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child (Optional)')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child (Optional)')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child (optional)')
    )
    parent_national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the caretaker')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker')
    )
    parent_syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the Caretaker (Mandatory)')
    )
    parent_syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Palestinian ID number of the Caretaker (Mandatory)')
    )
    parent_sop_national_number_confirm = forms.CharField(
        # regex=r'^\d{11}$',
        required=False,
        label=_('Confirm Palestinian ID number of the Caretaker (Mandatory)')
    )

    parent_other_number = forms.CharField(
        required=False,
        label=_('ID number of the Caretaker (Mandatory)')
    )
    parent_other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the Caretaker (Mandatory)')
    )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child (Optional)')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child (optional)')
    )
    child_id = forms.CharField(widget=forms.HiddenInput, required=False)
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    partner_name = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MainForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('mscc:add_child')
        if instance:
            display_registry = ' d-none'
            form_action = reverse('mscc:edit_child', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('center', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('child_first_name', css_class='col-md-3'),
                    Div('child_father_name', css_class='col-md-3'),
                    Div('child_last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_mother_fullname', css_class='col-md-3'),
                    Div('child_gender', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_nationality', css_class='col-md-3'),
                    Div('child_nationality_other', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_birthday_year', css_class='col-md-2'),
                    Div('child_birthday_month', css_class='col-md-2'),
                    Div('child_birthday_day', css_class='col-md-2'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_p_code', css_class='col-md-3'),
                    Div('child_address', css_class='col-md-3'),
                    Div('child_disability', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('child_marital_status', css_class='col-md-4'),
                    Div('child_have_children', css_class='col-md-3', css_id='child_have_children'),
                    Div('child_number_children', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('source_of_identification', css_class='col-md-4'),
                    Div('source_of_identification_specify', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('cash_support_programmes', css_class='col-md-6 multiple-choice'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            Div(
                Div(
                    Div('father_educational_level', css_class='col-md-4'),
                    Div('mother_educational_level', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('first_phone_number', css_class='col-md-3'),
                    Div('first_phone_number_confirm', css_class='col-md-3'),
                    Div('first_phone_owner', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('second_phone_number', css_class='col-md-3'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('main_caregiver', css_class='col-md-3'),
                    Div('main_caregiver_other', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('caregiver_first_name', css_class='col-md-3'),
                    Div('caregiver_middle_name', css_class='col-md-3'),
                    Div('caregiver_last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('caregiver_mother_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    Div('main_caregiver_nationality_other', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('id_type', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('case_number', css_class='col-md-4'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id1',
                ),
                Div(
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id1',
                ),
                Div(
                    Div('individual_case_number', css_class='col-md-4'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id1',
                ),
                Div(
                    Div('recorded_number', css_class='col-md-4'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id2',
                ),
                Div(
                    Div('parent_national_number', css_class='col-md-4'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id3',
                ),
                Div(
                    Div('national_number', css_class='col-md-4'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id3',
                ),
                Div(
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id4',
                ),
                Div(
                    Div('syrian_national_number', css_class='col-md-4'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id4',
                ),
                Div(
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id5',
                ),
                Div(
                    Div('sop_national_number', css_class='col-md-4'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id5',
                ),
                Div(
                    Div('parent_other_number', css_class='col-md-4'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id6',
                ),
                Div(
                    Div('other_number', css_class='col-md-4'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row card-body child_id6',
                ),
                css_id='step-3',
            ),
            Div(
                Div(
                    Div('have_labour', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('labour_type', css_class='col-md-4', css_id='labours'),
                    Div('labour_type_specify', css_class='col-md-4'),
                    css_class='row card-body',
                    id='labour_details_1'
                ),
                Div(
                    Div('labour_hours', css_class='col-md-4', css_id='labour_hours'),
                    Div('labour_weekly_income', css_class='col-md-4'),
                    css_class='row card-body',
                    id='labour_details_2'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Submit('save_add_another', 'Save & add another',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Submit('save_add_another', 'Save & go to Education',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-info'),
                    # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' + _(
                    #     'Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                    # css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn'
                ),
                css_id='step-4',
            ),
        )
        # partner_id = 0
        # if instance:
        #     if instance.owner.partner:
        #         partner_id = instance.owner.partner.id
        # else:
        #     if self.request.user.partner:
        #         partner_id = self.request.user.partner.id
        # if partner_id > 0:
        #     queryset = Center.objects.filter(partner_id=partner_id)
        #     self.fields['center'] = forms.ModelChoiceField(
        #         queryset=queryset, widget=forms.Select,
        #         label=_('Site / Center'),
        #         empty_label='-------',
        #         required=True, to_field_name='id',
        #     )

    def clean(self):
        cleaned_data = super(MainForm, self).clean()

        child_nationality = cleaned_data.get("child_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        if child_nationality and child_nationality.id == 6 and not other_nationality:
            self.add_error('other_nationality', 'This field is required')

        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        if main_caregiver_nationality and main_caregiver_nationality.id == 6 and not main_caregiver_nationality_other:
            self.add_error('main_caregiver_nationality_other', 'This field is required')

        child_have_children = cleaned_data.get("child_have_children")
        child_number_children = cleaned_data.get("child_number_children")
        if child_have_children and not child_number_children:
            self.add_error('child_number_children', 'This field is required')

        have_labour = cleaned_data.get("have_labour")
        labour_type = cleaned_data.get("labour_type")
        labour_type_specify = cleaned_data.get("labour_type_specify")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        if have_labour != 'No':
            if not labour_type:
                self.add_error('labour_type', 'This field is required')
            elif labour_type == 'other_many_other' and not labour_type_specify:
                self.add_error('labour_type_specify', 'This field is required')
            if not labour_hours:
                self.add_error('labour_hours', 'This field is required')
            if not labour_weekly_income:
                self.add_error('labour_weekly_income', 'This field is required')

        source_of_identification = cleaned_data.get("source_of_identification")
        source_of_identification_specify = cleaned_data.get("source_of_identification_specify")
        if source_of_identification == 'Other Sources' and not source_of_identification_specify:
            self.add_error('source_of_identification_specify', 'This field is required')

        first_phone_number = cleaned_data.get("first_phone_number")
        first_phone_number_confirm = cleaned_data.get("first_phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        if first_phone_number != first_phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('first_phone_number_confirm', msg)
        if second_phone_number != second_phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('second_phone_number_confirm', msg)

        main_caregiver = cleaned_data.get("main_caregiver")
        main_caregiver_other = cleaned_data.get("main_caregiver_other")
        if main_caregiver == 'other' and not main_caregiver_other:
            self.add_error('main_caregiver_other', 'This field is required')

        id_type = cleaned_data.get("id_type")
        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')
            elif case_number != case_number_confirm:
                msg = "The case numbers are not matched"
                self.add_error('case_number_confirm', msg)

            if parent_individual_case_number != parent_individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('parent_individual_case_number_confirm', msg)

            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')
            elif recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':
            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')
            elif parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')
            elif parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if parent_national_number and not len(parent_national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number', msg)

            if parent_national_number_confirm and not len(parent_national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('parent_national_number_confirm', msg)

            if parent_national_number != parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_parent_national_number:
                self.add_error('parent_sop_national_number', 'This field is required')

            if not sop_parent_national_number_confirm:
                self.add_error('parent_sop_national_number_confirm', 'This field is required')

            if sop_parent_national_number != sop_parent_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_sop_national_number_confirm', msg)

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not parent_other_number:
                self.add_error('parent_other_number', 'This field is required')

            if not parent_other_number_confirm:
                self.add_error('parent_other_number_confirm', 'This field is required')

            if parent_other_number != parent_other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('parent_other_number_confirm', msg)

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

    def save(self, request=None, instance=None):
        if instance:
            serializer = MainSerializer(instance, data=request.POST)
            if serializer.is_valid():
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
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        return instance

    class Meta:
        model = Registration
        fields = (
            'center',
            'child_first_name',
            'child_father_name',
            'child_last_name',
            'child_mother_fullname',
            'child_gender',
            'child_nationality',
            'child_nationality_other',
            'child_birthday_year',
            'child_birthday_month',
            'child_birthday_day',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'child_p_code',
            'child_address',
            'child_disability',
            'child_marital_status',
            'child_have_children',
            'child_number_children',
            'source_of_identification',
            'source_of_identification_specify',
            'cash_support_programmes',
            'father_educational_level',
            'mother_educational_level',
            'first_phone_owner',
            'first_phone_number',
            'first_phone_number_confirm',
            'second_phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'main_caregiver',
            'main_caregiver_other',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'have_labour',
            'labour_type',
            'labour_type_specify',
            'labour_hours',
            'labour_weekly_income',
            'id_type',
            'case_number',
            'case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'national_number',
            'national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
        )


# @todo to be changed
class EducationSituationForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('out of school', _('No Registered in any school before')),
            ('Was registered in formal school but didnt continue',
             _('Was registered in formal school but didnt continue')),
            ('Was registered in non formal program and was referred to MSCC',
             _('Was registered in non formal program and was referred to MSCC')),
            ('Was registered in non formal program but did not continue',
             _('Was registered in non formal program but did not continue')),
            ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programse'))
        ),
        initial=''
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )
    dropout_program = forms.ChoiceField(
        label=_('Please specify programme'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
            ('other	please specify	Was registered in BLN program',
             _('other please specify	Was registered in BLN program')),
            ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue')),
            ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ),
        initial=''
    )
    education_program = forms.ChoiceField(
        label=_('Please specify education programme in MSCC'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('BLN Level 1', _('BLN Level 1')),
            ('BLN Level 2', _('BLN Level 2')),
            ('YBLN', _('YBLN')),
            ('YFNL', _('YFNL')),
            ('CBECE Level 3', _('CBECE Level 3')),
            ('Retention Support', _('Retention Support')),
        ),
        initial=''
    )
    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=True
    )
    volunteering_experience = forms.ChoiceField(
        label=_("Does the adolescent have any volunteering experience?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    previous_community_initiative = forms.ChoiceField(
        label=_("Was the adolescent part of any previous community based initiative?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    enrollment_reason = forms.CharField(
        label=_('What is the reason for the adolescent enrollement in the programme?'),
        widget=forms.TextInput, required=False
    )
    pre_tests_administered = forms.ChoiceField(
        label=_("Were pre-tests administered to assess adolescents level?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )

    # clm_type = forms.CharField(widget=forms.HiddenInput, required=False)
    child_age = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EducationSituationForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        # self.fields['clm_type'].initial = 'MSCC'
        self.fields['child_age'].initial = instance.child_age

        form_action = reverse('clm:education_situation', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    # 'clm_type',
                    'child_age',
                    css_class='d-none',
                ),
                Div(
                    Div('education_status', css_class='col-md-3'),
                    Div('miss_school_date', css_class='col-md-3'),
                    Div('dropout_program', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('first_attendance_date', css_class='col-md-4'),
                    Div('education_program', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                css_id='step-1',
            ),
            Div(
                Div(
                    Div('volunteering_experience', css_class='col-md-4'),
                    Div('previous_community_initiative', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('enrollment_reason', css_class='col-md-4'),
                    Div('pre_tests_administered', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            )
        )

    def clean(self):
        cleaned_data = super(EducationSituationForm, self).clean()

        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        if education_status != 'out of school':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(EducationSituationForm, self).save()
        # instance = super(MSCCEducationSituationForm, self).save(request=request, instance=instance, serializer=MSCCSerializer)

        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
            'education_status',
            'miss_school_date',
            'dropout_program',
            'first_attendance_date',
            'education_program',
            'volunteering_experience',
            'previous_community_initiative',
            'enrollment_reason',
            'pre_tests_administered'
        )


# @todo to be changed
class DiagnosticAssessmentForm(forms.ModelForm):
    attended_arabic = forms.ChoiceField(
        label=_("Attended Arabic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    modality_arabic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    arabic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_foreign_language = forms.ChoiceField(
        label=_("Attended Foreign Language test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_foreign_language = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    foreign_language = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_math = forms.ChoiceField(
        label=_("Attended Math test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_math = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    math = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DiagnosticAssessmentForm, self).__init__(*args, **kwargs)
        pre_test = ''
        pre_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'MSCC'

        display_assessment = ''
        form_action = reverse('clm:diagnostic_assessment', kwargs={'pk': instance.id})

        if instance.pre_test:
            print('-------------------------------------------------')
            print(instance.pre_test)
            print('-------------------------------------------------')
            pre_test_button = ' btn-outline-success '
            pre_test = instance.assessment_form(
                stage='pre_test',
                assessment_slug='pre_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:diagnostic_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('attended_arabic', css_class='col-md-3'),
                    Div('modality_arabic', css_class='col-md-4 multiple-choice'),
                    Div('arabic', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_foreign_language', css_class='col-md-3'),
                    Div('modality_foreign_language', css_class='col-md-4 multiple-choice'),
                    Div('foreign_language', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_math', css_class='col-md-3'),
                    Div('modality_math', css_class='col-md-4 multiple-choice'),
                    Div('math', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-1',
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' +
                #      _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(DiagnosticAssessmentForm, self).clean()

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_foreign_language = cleaned_data.get("attended_foreign_language")
        modality_foreign_language = cleaned_data.get("modality_foreign_language")
        foreign_language = cleaned_data.get("foreign_language")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        if attended_arabic == 'yes':
            if not modality_arabic:
                self.add_error('modality_arabic', 'This field is required')
            if arabic is None:
                self.add_error('arabic', 'This field is required')

        if attended_foreign_language == 'yes':
            if not modality_foreign_language:
                self.add_error('modality_foreign_language', 'This field is required')
            if foreign_language is None:
                self.add_error('foreign_language', 'This field is required')

        if attended_math == 'yes':
            if not modality_math:
                self.add_error('modality_math', 'This field is required')
            if math is None:
                self.add_error('math', 'This field is required')

            # # grades Max Value validation
            # registration_level = cleaned_data.get("registration_level")
            #
            # if registration_level == 'level_one':
            #     if arabic > 46:
            #         self.add_error('arabic', 'This value is greater that 46')
            #     # if foreign_language > 36:
            #     #     self.add_error('foreign_language', 'This value is greater that 36')
            #     if math > 20:
            #         self.add_error('math', 'This value is greater that 20')
            # else:
            #     if arabic > 56:
            #         self.add_error('arabic', 'This value is greater that 56')
            #     # if foreign_language > 56:
            #     #     self.add_error('foreign_language', 'This value is greater that 56')
            #     if math > 34:
            #         self.add_error('math', 'This value is greater that 34')

    def save(self, instance=None, request=None):
        instance = super(DiagnosticAssessmentForm, self).save()

        instance.modified_by = request.user

        instance.pre_test = {
            "Diagnostic_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "Diagnostic_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "Diagnostic_ASSESSMENT/arabic": request.POST.get('arabic'),

            "Diagnostic_ASSESSMENT/attended_foreign_language": request.POST.get('attended_foreign_language'),
            "Diagnostic_ASSESSMENT/modality_foreign_language": request.POST.getlist('modality_foreign_language'),
            "Diagnostic_ASSESSMENT/foreign_language": request.POST.get('foreign_language'),

            "Diagnostic_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "Diagnostic_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "Diagnostic_ASSESSMENT/math": request.POST.get('math'),
        }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
        )


# @todo to be changed
class EducationAssessmentForm(forms.ModelForm):
    # REGISTRATION_LEVEL = (
    #     ('', '----------'),
    #     ('level_one', _('Level one')),
    #     ('level_two', _('Level two')),
    #     # ('level_three', _('Level three'))
    # )
    participation = forms.ChoiceField(
        label=_('How was the level of child participation in the program?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('no_absence', _('No Absence')),
            ('less_than_5days', _('Less than 5 absence days')),
            ('5_10_days', _('5 to 10 absence days')),
            ('10_15_days', _('10 to 15 absence days')),
            ('15_25_days', _('15 to 25 absence days')),
            ('more_than_25days', _('More than 25 absence days')),

        ),
        initial=''
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices=EducationAssessment.BARRIERS,
        widget=forms.Select,
        required=False
    )
    barriers_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    test_done = forms.ChoiceField(
        label=_("Post test has been done"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    round_complete = forms.ChoiceField(
        label=_("Round complete"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    attended_arabic = forms.ChoiceField(
        label=_("Attended Arabic test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )

    modality_arabic = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    arabic = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_foreign_language = forms.ChoiceField(
        label=_("Attended Foreign Language test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_foreign_language = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    foreign_language = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    attended_math = forms.ChoiceField(
        label=_("Attended Math test"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    modality_math = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    math = forms.FloatField(
        label=_('Results'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        # choices=EducationAssessment.LEARNING_RESULT,
        initial=''
    )

    test_diagnostic_done = forms.ChoiceField(
        label=_("Did the adolescent undertake any Post Diagnostic tests?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    receive_passing_grade = forms.ChoiceField(
        label=_("Did the adolescent receive a passing grade for the tests?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    life_skills_completed = forms.ChoiceField(
        label=_("Did the adolescent complete the life skills package?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    participate_volunteering = forms.ChoiceField(
        label=_("Did the adolescent participate in any volunteering opportunity during the course of the program?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    volunteering_specify = forms.ChoiceField(
        label=_('Please specify the volunteering opportunity'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Outreach', _('Outreach')),
            ('Data entry', _('Data entry')),
            ('Admin work', _('Admin work')),
            ('Awareness raising sessions', _('Awareness raising sessions')),
            ('Empowerment and leadership', _('Empowerment and leadership')),
            ('Other', _('Other')),
        ),
        initial=''
    )

    social_course = forms.ChoiceField(
        label=_("Did the adolescent benefit from any social innovation/entrepreneurship course?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    yfs_course_completed = forms.ChoiceField(
        label=_("Did the adolescent complete the YFS course?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )
    training_material = forms.ChoiceField(
        label=_('What training material was provided?'),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Printed workbook', _('Printed workbook')),
            ('Tablets', _('Tablets')),
            ('Access to digital content (learning Passport) ', _('Access to digital content (learning Passport) ')),
            ('Other', _('Other')),
        ),
        initial=''
    )
    participate_community_initiatives = forms.ChoiceField(
        label=_("Did the adolescent participate/come up in community based initiatives?"),
        widget=forms.Select, required=False,
        choices=Registration.YES_NO,
        initial='yes'
    )

    community_initiatives_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    adolescent_attendance = forms.ChoiceField(
        label=_('What training material was provided?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Full attendance', _('Full attendance')),
            ('Absence for less than 5 days', _('Absence for less than 5 days')),
            ('Absence for more than 5 days', _('Absence for more than 5 days')),
            ('Dropout', _('Dropout')),
        ),
        initial=''
    )
    adolescent_dropout_reason = forms.CharField(
        label=_('Reason for dropout'),
        widget=forms.TextInput, required=False
    )

    adolescent_dropout_date = forms.DateField(
        label=_("Dropout Date"),
        required=False
    )
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EducationAssessmentForm, self).__init__(*args, **kwargs)
        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'MSCC'

        display_assessment = ''
        form_action = reverse('clm:education_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:education_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('participation', css_class='col-md-4'),
                    Div('barriers_single', css_class='col-md-4'),
                    Div('barriers_other', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('test_done', css_class='col-md-4'),
                    Div('round_complete', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    Div('attended_arabic', css_class='col-md-2'),
                    Div('modality_arabic', css_class='col-md-2  multiple-choice'),
                    Div('arabic', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),

                Div(
                    Div('attended_foreign_language', css_class='col-md-2'),
                    Div('modality_foreign_language', css_class='col-md-2  multiple-choice'),
                    Div('foreign_language', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),
                Div(
                    Div('attended_math', css_class='col-md-2'),
                    Div('modality_math', css_class='col-md-2  multiple-choice'),
                    Div('math', css_class='col-md-2'),
                    css_class='row grades card-body',
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('test_diagnostic_done', css_class='col-md-3'),
                    Div('receive_passing_grade', css_class='col-md-3'),
                    Div('life_skills_completed', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('participate_volunteering', css_class='col-md-3'),
                    Div('volunteering_specify', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('social_course', css_class='col-md-3'),
                    Div('yfs_course_completed', css_class='col-md-3'),
                    Div('training_material', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('learning_result', css_class='col-md-3'),
                    Div('participate_community_initiatives', css_class='col-md-3'),
                    Div('community_initiatives_specify', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    Div('adolescent_attendance', css_class='col-md-3'),
                    Div('adolescent_dropout_reason', css_class='col-md-3'),
                    Div('adolescent_dropout_date', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-2',
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                # HTML('<a class="btn btn-info cancel-button" href="/clm/mscc-list/" translation="' +
                #      _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        cleaned_data = super(EducationAssessmentForm, self).clean()
        participation = cleaned_data.get("participation")
        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")
        if participation != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        attended_arabic = cleaned_data.get("attended_arabic")
        modality_arabic = cleaned_data.get("modality_arabic")
        arabic = cleaned_data.get("arabic")

        attended_foreign_language = cleaned_data.get("attended_foreign_language")
        modality_foreign_language = cleaned_data.get("modality_foreign_language")
        foreign_language = cleaned_data.get("foreign_language")

        attended_math = cleaned_data.get("attended_math")
        modality_math = cleaned_data.get("modality_math")
        math = cleaned_data.get("math")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

            if attended_arabic == 'yes':
                if not modality_arabic:
                    self.add_error('modality_arabic', 'This field is required')
                if arabic is None:
                    self.add_error('arabic', 'This field is required')

            if attended_foreign_language == 'yes':
                if not modality_foreign_language:
                    self.add_error('modality_foreign_language', 'This field is required')
                if foreign_language is None:
                    self.add_error('foreign_language', 'This field is required')

            if attended_math == 'yes':
                if not modality_math:
                    self.add_error('modality_math', 'This field is required')
                if math is None:
                    self.add_error('math', 'This field is required')

            # # grades Max Value validation
            # registration_level = cleaned_data.get("registration_level")
            #
            # if registration_level == 'level_one':
            #     if arabic > 46:
            #         self.add_error('arabic', 'This value is greater that 46')
            #     # if foreign_language > 36:
            #     #     self.add_error('foreign_language', 'This value is greater that 36')
            #     if math > 20:
            #         self.add_error('math', 'This value is greater that 20')
            # else:
            #     if arabic > 56:
            #         self.add_error('arabic', 'This value is greater that 56')
            #     # if foreign_language > 56:
            #     #     self.add_error('foreign_language', 'This value is greater that 56')
            #     if math > 34:
            #         self.add_error('math', 'This value is greater that 34')

        test_diagnostic_done = cleaned_data.get("test_diagnostic_done")
        receive_passing_grade = cleaned_data.get("receive_passing_grade")
        if test_diagnostic_done == 'yes':
            if not receive_passing_grade:
                self.add_error('receive_passing_grade', 'This field is required')

        participate_volunteering = cleaned_data.get("participate_volunteering")
        volunteering_specify = cleaned_data.get("volunteering_specify")
        if participate_volunteering == 'yes':
            if not volunteering_specify:
                self.add_error('volunteering_specify', 'This field is required')

        yfs_course_completed = cleaned_data.get("yfs_course_completed")
        training_material = cleaned_data.get("training_material")
        if yfs_course_completed == 'yes':
            if not training_material:
                self.add_error('training_material', 'This field is required')

        participate_community_initiatives = cleaned_data.get("participate_community_initiatives")
        community_initiatives_specify = cleaned_data.get("community_initiatives_specify")
        if participate_community_initiatives == 'yes':
            if not community_initiatives_specify:
                self.add_error('community_initiatives_specify', 'This field is required')

        adolescent_attendance = cleaned_data.get("adolescent_attendance")
        adolescent_dropout_reason = cleaned_data.get("adolescent_dropout_reason")
        adolescent_dropout_date = cleaned_data.get("adolescent_dropout_date")
        if adolescent_attendance == 'Dropout':
            if not adolescent_dropout_reason:
                self.add_error('adolescent_dropout_reason', 'This field is required')
            if not adolescent_dropout_date:
                self.add_error('adolescent_dropout_date', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(EducationAssessmentForm, self).save()
        instance.post_test = {
            "Education_ASSESSMENT/attended_arabic": request.POST.get('attended_arabic'),
            "Education_ASSESSMENT/modality_arabic": request.POST.getlist('modality_arabic'),
            "Education_ASSESSMENT/arabic": request.POST.get('arabic'),

            "Education_ASSESSMENT/attended_foreign_language": request.POST.get('attended_foreign_language'),
            "Education_ASSESSMENT/modality_foreign_language": request.POST.getlist('modality_foreign_language'),
            "Education_ASSESSMENT/foreign_language": request.POST.get('foreign_language'),

            "Education_ASSESSMENT/attended_math": request.POST.get('attended_math'),
            "Education_ASSESSMENT/modality_math": request.POST.getlist('modality_math'),
            "Education_ASSESSMENT/math": request.POST.get('math'),
        }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Registration
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'test_diagnostic_done',
            'receive_passing_grade',
            'life_skills_completed',
            'participate_volunteering',
            'volunteering_specify',
            'social_course',
            'yfs_course_completed',
            'training_material',
            'participate_community_initiatives',
            'community_initiatives_specify',
            'adolescent_attendance',
            'adolescent_dropout_reason',
            'adolescent_dropout_date',
            'learning_result',
        )
