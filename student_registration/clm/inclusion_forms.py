from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset
from dal import autocomplete

from student_registration.students.models import (
    Student,
    Person,
    Nationality,
    IDType,
)

from student_registration.locations.models import Location
from .models import Disability, Inclusion, CLMRound
from .inclusion_serializers import InclusionSerializer


YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 29, Person.CURRENT_YEAR)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))

MONTHS = (
            ('', '----------'),
            ('1', _('January')),
            ('2', _('February')),
            ('3', _('March')),
            ('4', _('April')),
            ('5', _('May')),
            ('6', _('June')),
            ('7', _('July')),
            ('8', _('August')),
            ('9', _('September')),
            ('10', _('October')),
            ('11', _('November')),
            ('12', _('December')),
        )

PARTICIPATION = (
    ('', '----------'),
    ('less_than_5days', _('Less than 5 absence days')),
    ('5_10_days', _('5 to 10 absence days')),
    ('10_15_days', _('10 to 15 absence days')),
    ('more_than_15days', _('More than 15 absence days')),
    ('no_absence', _('No Absence'))
)

LEARNING_RESULT = (
    ('', '----------'),
    ('repeat_level', _('Repeat level')),
    ('graduated_next_level', _('Referred to the next level')),
    ('graduated_to_formal_kg', _('Referred to formal education - KG')),
    ('graduated_to_formal_level1', _('Referred to formal education - Level 1')),
    ('referred_to_another_program', _('Referred to another program')),
    ('dropout', _('Dropout, referral not possible'))
)


class InclusionForm(forms.ModelForm):
    YEARS_CT = list(((str(x), x) for x in range(1940, Person.CURRENT_YEAR - 18)))
    YEARS_CT.insert(0, ('', '---------'))

    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_inclusion=True), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(type=2), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(type=3), widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    location = forms.CharField(
        label=_("Location"),
        widget=forms.TextInput, required=True
    )
    student_first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput, required=True
    )
    student_father_name = forms.CharField(
        label=_("Father name"),
        widget=forms.TextInput, required=True
    )
    student_last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput, required=True
    )
    student_sex = forms.ChoiceField(
        label=_("Sex"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    student_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=MONTHS
    )
    student_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    student_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    disability = forms.ModelChoiceField(
        queryset=Disability.objects.filter(active=True), widget=forms.Select,
        label=_('Does the child have any disability or special need?'),
        required=True, to_field_name='id',
        initial=1
    )
    main_caregiver = forms.ChoiceField(
        label=_("Main Caregiver"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        widget=forms.TextInput(attrs={'autocomplete': 'false'}),
        required=False
    )
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
    )
    student_number_children = forms.CharField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )
    have_labour = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=False,
        choices=Inclusion.HAVE_LABOUR,
        initial='no'
    )
    labour_type = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=Inclusion.LABOURS
    )
    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    other_nationality = forms.CharField(
        label=_('Specify the nationality'),
        widget=forms.TextInput, required=False
    )

    phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number')
    )
    phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number confirm')
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number')
    )
    second_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number confirm')
    )
    id_type = forms.ChoiceField(
        label=_("ID type of the caretaker"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=True,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
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
        label=_('Confirm Individual ID of the Child from the certificate '
                '(Optional, in case not listed in the certificate)')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe))-[0-9]{2}[C-](?:\d{5}|\d{6})$|^LB-\d{3}-\d{6}|\d{7}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX or LB-XXX-XXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe))-[0-9]{2}[C-](?:\d{5}|\d{6})$|^LB-\d{3}-\d{6}|\d{7}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX or LB-XXX-XXXXXX'}),
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
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the caretaker (Mandatory)')
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
    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    source_of_identification = forms.ChoiceField(
        label=_("Disability Source of identification of the child"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('from abln', _('FROM ABLN')),
            ('from bln', _('FROM BLN')),
            ('from cbece', _('FROM CBECE')),
            ('ocha', _('OCHA')),
            ('non unicef', _('Non - UNICEF')),
            ('RIMS', _('RIMS'))
        ),
        initial=''
    )
    rims_case_number = forms.CharField(
        required=False,
        label=_('RIMS Case Number')
    )
    caretaker_birthday_year = forms.ChoiceField(
        label=_("Caretaker birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_CT,
    )
    caretaker_birthday_month = forms.ChoiceField(
        label=_("Caretaker birthday month"),
        widget=forms.Select, required=True,
        choices=MONTHS
    )
    caretaker_birthday_day = forms.ChoiceField(
        label=_("Caretaker birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )

    search_clm_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    partner_name = forms.CharField(widget=forms.HiddenInput, required=False)
    new_registry = forms.ChoiceField(
        label=_("First time registered Inclusion?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(InclusionForm, self).__init__(*args, **kwargs)
        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:inclusion_add')
        self.fields['clm_type'].initial = 'Inclusion'
        self.fields['new_registry'].initial = 'yes'

        if instance:
            form_action = reverse('clm:inclusion_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    'clm_type',
                    'student_id',
                    'enrollment_id',
                    'partner_name',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default"></span>'),
                    Div('search_clm_student', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('round', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('governorate', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('location', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge-pill" id="span_other_nationality"></span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('student_p_code', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('disability', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    # HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('first_attendance_date', css_class='col-md-3 d-none'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_rims_case_number">14</span>'),
                    Div('rims_case_number', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-2'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('second_phone_owner', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill" id="span_other_caregiver_relationship"></span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('caretaker_first_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('caretaker_middle_name', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('caretaker_last_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('caretaker_mother_name', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('caretaker_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('caretaker_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('caretaker_birthday_day', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('id_type', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">18</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">19</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">21</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">22</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">23</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">24</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">25</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">26</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">27</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">28</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">29</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">30</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">31</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">32</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">33</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">34</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">35</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">36</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">37</span>'),
                    Div('parent_other_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">38</span>'),
                    Div('parent_other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6 card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">39</span>'),
                    Div('other_number', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">40</span>'),
                    Div('other_number_confirm', css_class='col-md-4'),
                    css_class='row child_id child_id6 card-body',
                ),
                css_id='step-3'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('have_labour', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('labour_type', css_class='col-md-3', css_id='labours'),
                    css_class='row card-body'
                ),
                css_id="step-4"
            ),
            Div(
                Div(
                    # HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('additional_comments', css_class='col-md-12'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                style='display: none;',
                css_id='step-5'
            )
        )

    def clean(self):
        cleaned_data = super(InclusionForm, self).clean()

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        case_number = cleaned_data.get("case_number")
        case_number_confirm = cleaned_data.get("case_number_confirm")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")
        parent_individual_case_number = cleaned_data.get("parent_individual_case_number")
        parent_individual_case_number_confirm = cleaned_data.get("parent_individual_case_number_confirm")
        parent_national_number = cleaned_data.get("parent_national_number")
        parent_national_number_confirm = cleaned_data.get("parent_national_number_confirm")
        sop_parent_national_number = cleaned_data.get("parent_sop_national_number")
        sop_parent_national_number_confirm = cleaned_data.get("parent_sop_national_number_confirm")
        parent_syrian_national_number = cleaned_data.get("parent_syrian_national_number")
        parent_syrian_national_number_confirm = cleaned_data.get("parent_syrian_national_number_confirm")
        parent_other_number = cleaned_data.get("parent_other_number")
        parent_other_number_confirm = cleaned_data.get("parent_other_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        # education_status = cleaned_data.get("education_status")
        # miss_school_date = cleaned_data.get("miss_school_date")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        # have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        # labours_single_selection = cleaned_data.get("labours_single_selection")
        # labour_hours = cleaned_data.get("labour_hours")
        # labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")
        source_of_identification = cleaned_data.get("source_of_identification")
        rims_case_number = cleaned_data.get("rims_case_number")

        if source_of_identification == 'RIMS':
            if not rims_case_number:
                self.add_error('rims_case_number', 'This field is required')


        # if education_status != 'out of school':
        #     if not miss_school_date:
        #         self.add_error('miss_school_date', 'This field is required')
        if student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        # if student_have_children:
        #     if not student_number_children:
        #         self.add_error('student_number_children', 'This field is required')
        # if have_labour_single_selection != 'no':
        #     if not labours_single_selection:
        #         self.add_error('labours_single_selection', 'This field is required')
        #     if not labour_hours:
        #         self.add_error('labour_hours', 'This field is required')
        #     if not labour_weekly_income:
        #         self.add_error('labour_weekly_income', 'This field is required')


        if phone_number != phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('phone_number_confirm', msg)

        if second_phone_number != second_phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('second_phone_number_confirm', msg)

        if id_type == 'UNHCR Registered':
            if not case_number:
                self.add_error('case_number', 'This field is required')

            if case_number != case_number_confirm:
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

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':

            if not parent_syrian_national_number:
                self.add_error('parent_syrian_national_number', 'This field is required')

            if not parent_syrian_national_number_confirm:
                self.add_error('parent_syrian_national_number_confirm', 'This field is required')

            if parent_syrian_national_number_confirm and not len(parent_syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if parent_syrian_national_number and not len(parent_syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('parent_syrian_national_number', msg)

            if parent_syrian_national_number != parent_syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('parent_syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not parent_national_number:
                self.add_error('parent_national_number', 'This field is required')

            if not parent_national_number_confirm:
                self.add_error('parent_national_number_confirm', 'This field is required')

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
            serializer = InclusionSerializer(instance, data=request.POST)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = InclusionSerializer(data=request.POST)
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
        model = Inclusion
        fields = (
            'round',
            'first_attendance_date',
            'governorate',
            'district',
            'cadaster',
            'location',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'student_birthday_month',
            'student_birthday_day',
            'student_birthday_year',
            'student_nationality',
            'student_mother_fullname',
            'student_p_code',
            'internal_number',
            'disability',
            'student_id',
            'enrollment_id',
            'main_caregiver',
            'main_caregiver_nationality',
            'other_caregiver_relationship',
            'have_labour',
            'labour_type',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'other_nationality',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'additional_comments',
            'caretaker_birthday_year',
            'caretaker_birthday_month',
            'caretaker_birthday_day',
        )

    class Media:
        js = ()


class InclusionFollowupForm(forms.ModelForm):
    child_dropout = forms.ChoiceField(
        label=_("Has the child dropped out of the program?"),
        widget=forms.Select, required=True,
        choices=Inclusion.YES_NO,
        initial='no'
    )
    child_dropout_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    caregiver_trained_parental_engagement = forms.ChoiceField(
        label=_('Have the Caregivers been trained on the Parental Engagement Curriculum? '),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Mother Only', _('Mother Only')),
            ('Father Only', _('Father Only')),
            ('Both Mother and Father', _('Both Mother and Father')),
            ('None', _('None')),
            ('Not begun yet', _('Not begun yet')),
        ),
        initial=''
    )
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(InclusionFollowupForm, self).__init__(*args, **kwargs)
        # post_test = ''
        # post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'Inclusion'
        display_assessment = ''
        form_action = reverse('clm:inclusion_followup', kwargs={'pk': instance.id})
        # if instance.post_test:
        #     post_test_button = ' btn-outline-success '
        #     post_test = instance.assessment_form(
        #         stage='followup',
        #         assessment_slug='inclusion_followup',
        #         callback=self.request.build_absolute_uri(
        #             reverse('clm:inclusion_followup', kwargs={'pk': instance.id}))
        #     )
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('clm_type', css_class='col-md-3 d-none'),
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('child_dropout', css_class='col-md-6'),
                    HTML('<span class="badge-form badge-pill" id="span_child_dropout_specify">2</span>'),
                    Div('child_dropout_specify', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('caregiver_trained_parental_engagement', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                )
            )
        )

    def clean(self):
        cleaned_data = super(InclusionFollowupForm, self).clean()
        child_dropout = cleaned_data.get("child_dropout")
        child_dropout_specify = cleaned_data.get("child_dropout_specify")
        if child_dropout == 'yes':
            if not child_dropout_specify:
                self.add_error('child_dropout_specify', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(InclusionFollowupForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Inclusion
        fields = (
            'child_dropout',
            'child_dropout_specify',
            'caregiver_trained_parental_engagement'
        )


class InclusionAssessmentForm(forms.ModelForm):

    participation = forms.ChoiceField(
        label=_('How was the level of child participation in the program?'),
        widget=forms.Select, required=True,
        choices=(
                ('', '----------'),
                ('no_absence', _('No Absence')),
                ('less_than_3days', _('Less than 3 absence days')),
                ('3_7_days', _('3 to 7 absence days')),
                ('7_12_days', _('7 to 12 absence days')),
                ('more_than_12days', _('More than 12 absence days')),

            ),
        initial=''
    )
    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
            ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
            ('referred_to_bln', _('Referred to BLN')),
            ('referred_to_ybln', _('Referred to YBLN')),
            # ('referred_to_alp', _('Referred to ALP')),
            ('referred_to_cbt', _('Referred to CBT')),
        ),
        initial=''
    )

    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme? (Select more than one if applicable)'),
        choices=Inclusion.BARRIERS,
        widget=forms.Select,
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(InclusionAssessmentForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance'] if 'instance' in kwargs else ''

        form_action = reverse('clm:inclusion_assessment', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('participation', css_class='col-md-4'),
                    Div('barriers', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            )
        )

    def save(self, instance=None, request=None):
        instance = super(InclusionAssessmentForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Inclusion
        fields = (
            'participation',
            'learning_result',
            'barriers',
        )


class InclusionAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(InclusionAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Inclusion
        fields = '__all__'


class InclusionReferralForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InclusionReferralForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('clm:inclusion_referral', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('referral_programme_type_1', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('referral_partner_1', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('referral_date_1', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('confirmation_date_1', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('referral_programme_type_2', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('referral_partner_2', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('referral_date_2', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('confirmation_date_2', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-2'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('referral_programme_type_3', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('referral_partner_3', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('referral_date_3', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('confirmation_date_3', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-3'
            )
        )

    def save(self, instance=None, request=None):
        instance = super(InclusionReferralForm, self).save()
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Inclusion
        fields = (
            'referral_programme_type_1',
            'referral_partner_1',
            'referral_date_1',
            'confirmation_date_1',
            'referral_programme_type_2',
            'referral_partner_2',
            'referral_date_2',
            'confirmation_date_2',
            'referral_programme_type_3',
            'referral_partner_3',
            'referral_date_3',
            'confirmation_date_3',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )



