from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete

from student_registration.students.models import (
    Student,
    Person,
    Nationality,
    IDType,
)

from student_registration.locations.models import Location
from .models import Disability, Inclusion
from .inclusion_serializers import InclusionSerializer


YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-20, Person.CURRENT_YEAR-2)))
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
        widget=forms.TextInput, required=False
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
        queryset=Nationality.objects.all(), widget=forms.Select,
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
    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)

    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        widget=forms.TextInput(attrs={'autocomplete': 'false'}),
        required=True
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
        label=_('Phone number (own or closest relative)')
    )
    phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number confirm')
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number (own or closest relative)')
    )
    second_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number confirm')
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
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(LEB)|(leb))-[0-9][0-9][C]\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )
    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        required=False,
        label=_('Lebanese ID number of the child (Optional)')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
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
        required=False,
        label=_('Lebanese ID number of the caretaker (Mandatory)')
    )
    parent_national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
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

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child"),
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
            ('List database', _('List database'))
        ),
        initial=''
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(InclusionForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:inclusion_add')

        if instance:
            form_action = reverse('clm:inclusion_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    'student_id',
                    'enrollment_id',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('General Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('district', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('location', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data A_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>B</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Child Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('other_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_p_code', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('disability', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('internal_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('first_attendance_date', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('source_of_identification', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data B_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>C</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Parent/Caregiver Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.1</span>'),
                    Div('phone_number_confirm', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3.2</span>'),
                    Div('phone_owner', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('second_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4.1</span>'),
                    Div('second_phone_number_confirm', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('main_caregiver', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5.1</span>'),
                    Div('main_caregiver_nationality', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5.2</span>'),
                    Div('other_caregiver_relationship', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('caretaker_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('caretaker_middle_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('caretaker_last_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('caretaker_mother_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('id_type', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('parent_individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('individual_case_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('individual_case_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id1',
                ),
                Div(
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('recorded_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">18</span>'),
                    Div('recorded_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id2',
                ),
                Div(
                    HTML('<span class="badge badge-default">19</span>'),
                    Div('parent_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">20</span>'),
                    Div('parent_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">21</span>'),
                    Div('national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">22</span>'),
                    Div('national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/lebanese_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id3',
                ),
                Div(
                    HTML('<span class="badge badge-default">23</span>'),
                    Div('parent_syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">24</span>'),
                    Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/syrian_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">25</span>'),
                    Div('syrian_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">26</span>'),
                    Div('syrian_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/syrian_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id4',
                ),
                Div(
                    HTML('<span class="badge badge-default">27</span>'),
                    Div('parent_sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">28</span>'),
                    Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/sop_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                Div(
                    HTML('<span class="badge badge-default">29</span>'),
                    Div('sop_national_number', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">30</span>'),
                    Div('sop_national_number_confirm', css_class='col-md-4'),
                    HTML('<span style="padding-top: 37px;">' +
                         '<a href="/static/images/sop_nationalID.png" target="_blank">' +
                         '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    css_class='row child_id child_id5',
                ),
                css_class='bd-callout bd-callout-warning child_data C_right_border'
            ),
            Fieldset(
                None,
                Div(HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Family Status') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_labour', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('labour_type', css_class='col-md-3', css_id='labours'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data D_right_border d-none'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span>D</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Comments') + '</h4>')
                ),
                Div(
                    # HTML('<span class="badge badge-default">1</span>'),
                    Div('additional_comments', css_class='col-md-12'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data E_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                Submit('save_add_another', _('Save and add another'), css_class='col-md-2 child_data'),
                HTML('<a class="btn btn-info cancel-button col-md-2" href="/clm/inclusion-list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
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
            'no_child_id_confirmation',
            'source_of_identification',
            'other_nationality',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'additional_comments'
        )

    class Media:
        js = ()


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
            Fieldset(
                None,
                Div(
                    HTML('<span>A</span>'), css_class='block_tag'),
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School evaluation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participation', css_class='col-md-4'),
                    Div('barriers', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('learning_result', css_class='col-md-4'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info cancel-button col-md-2" href="/clm/inclusion-list/" translation="' +
                     _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
                css_class='button-group'
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
            Fieldset(
                None,
                Div(css_class='block_tag'),
                Div(
                    Div(HTML('<span>1</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 1') + '</h4>'),
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_1', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning A_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>2</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 2') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_2', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_2', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning B_right_border'
            ),
            Fieldset(
                None,
                Div(
                    Div(HTML('<span>3</span>'), css_class='block_tag'),
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Referral 3') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('referral_programme_type_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('referral_partner_3', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('referral_date_3', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('confirmation_date_3', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning C_right_border'
            ),
            FormActions(
                Submit('save', _('Save'), css_class='col-md-2'),
                HTML('<a class="btn btn-info col-md-2" href="/clm/inclusion-list/">' + _('Back to list') + '</a>'),
                css_class='button-group'
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



