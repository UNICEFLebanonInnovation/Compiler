from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from django.core.urlresolvers import reverse
from .models import Enrollment, LoggingStudentMove
from student_registration.students.models import Student

from model_utils import Choices
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from bootstrap3_datetime.widgets import DateTimePicker
from student_registration.students.models import (
    IDType,
    Nationality,
)
from student_registration.schools.models import (
    School
)

YES_NO_CHOICE = ((False, _('No')), (True, _('Yes')))


class EnrollmentAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(EnrollmentAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = '__all__'


class EnrollmentForm(forms.ModelForm):

    old_or_new = forms.TypedChoiceField(
        label="First time registered?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=True,
    )
    student_outreached = forms.TypedChoiceField(
        label="Student outreached?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    have_barcode = forms.TypedChoiceField(
        label="Have barcode with him?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False,
    )
    search_barcode = forms.CharField(widget=forms.TextInput, required=True)
    search_student = forms.CharField(widget=forms.TextInput, required=True)
    # school = forms.ModelChoiceField(
    #     queryset=School.objects.all(), widget=forms.Select(attrs=({'placeholder': _('Schools')})),
    #     required=False, to_field_name='id',
    # )

    registration_date = forms.DateField(
        # widget=DateTimePicker(
        #     options={
        #         "viewMode": "years",
        #         "format": "mm/dd/yyyy",
        #         "pickTime": False,
        #         "stepping": 0,
        #         "showClear": True,
        #         "showClose": True,
        #         "disabledHours": True,
        #     }),
        required=True
    )

    first_name = forms.CharField(widget=forms.TextInput, required=True)
    father_name = forms.CharField(widget=forms.TextInput, required=True)
    last_name = forms.CharField(widget=forms.TextInput, required=True)
    sex = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Gender')),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    birthday_year = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=((str(x), x) for x in range(1930, 2051))
    )
    birthday_month = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Birthday Month')),
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
    )
    birthday_day = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=((str(x), x) for x in range(1, 32))
    )

    nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select(attrs=({'placeholder': _('Nationality')})),
        required=True, to_field_name='id',
    )

    mother_fullname = forms.CharField(widget=forms.TextInput, required=True)
    mother_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select(attrs=({'placeholder': _('Mother Nationality')})),
        required=True, to_field_name='id',
    )
    # registered_in_unhcr = forms.TypedChoiceField(
    #     choices = ((1, "Yes"), (0, "No")),
    #     coerce = lambda x: bool(int(x)),
    #     widget = forms.RadioSelect,
    #     initial = '1',
    #     required = True,
    # )
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    id_number = forms.CharField(widget=forms.TextInput, required=True)

    phone_prefix = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 2})), required=True)
    phone = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 6})), required=True)
    address = forms.CharField(widget=forms.TextInput, required=True)

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['id_type'].empty_label = _('Student ID Type')
        self.fields['sex'].empty_label = _('Gender')
        self.fields['nationality'].empty_label = _('Student nationality')
        self.fields['mother_nationality'].empty_label = _('Mather nationality')
        self.fields['classroom'].empty_label = _('Current Class')
        self.fields['section'].empty_label = _('Current Section')

        self.fields['last_education_level'].empty_label = _('Last education level')
        self.fields['last_school_type'].empty_label = _('School type')
        self.fields['last_school_shift'].empty_label = _('School shift')
        self.fields['last_school'].empty_label = _('School')
        self.fields['last_education_year'].empty_label = _('Education year')
        self.fields['last_year_result'].empty_label = _('Result')
        self.fields['last_informal_edu_level'].empty_label = _('ALP level')
        self.fields['last_informal_edu_round'].empty_label = _('ALP round')
        self.fields['last_informal_edu_final_result'].empty_label = _('ALP result')
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_action = reverse('enrollments:add')
        self.helper.layout = Layout(
            Fieldset(
                _('Registry'),
                Div(
                    Div(InlineRadios('old_or_new'), css_class='col-md-4'),
                    Div(InlineRadios('student_outreached'), css_class='col-md-4'),
                    Div(InlineRadios('have_barcode'), css_class='col-md-4'),
                    css_class='row',
                ),
                # Div(
                #     Div(PrependedText('outreach_barcode', _('Outreach Barcode')), css_class='col-md-4'),
                #     css_class='row',
                # ),
                # Div(css_id='search_results', css_class='row',),
                # css_id='registry',
            ),
            Fieldset(
                _('Register by Barcode'),
                Div(
                    Div(PrependedText('search_barcode', _('Search child by barcode')), css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Search old student (fullname Or ID number)'),
                Div(
                    Div('school', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('search_student', _('Search old student')), css_class='col-md-6'),
                    css_class='row',
                ),
                css_id='search_options',
            ),
            Fieldset(
                _('Basic Data'),
                Div(
                    Div(PrependedText('registration_date', _('Registration date')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('first_name', _('First Name')), css_class='col-md-4'),
                    Div(PrependedText('father_name', _('Father Name')), css_class='col-md-4'),
                    Div(PrependedText('last_name', _('Last Name')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('sex', css_class='col-md-3'),
                    Div('birthday_year', css_class='col-md-2'),
                    Div('birthday_month', css_class='col-md-2'),
                    Div('birthday_day', css_class='col-md-2'),
                    Div('nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('mother_fullname', _('Mother Full name')), css_class='col-md-4'),
                    Div('mother_nationality', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    # Div(InlineRadios('registered_in_unhcr', _('Registered in UNHCR')), css_class='col-md-4'),
                    Div('registered_in_unhcr', css_class='col-md-4'),
                    Div('id_type', css_class='col-md-4'),
                    Div(PrependedText('id_number', _('Student ID Number')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('phone_prefix', _('Prefix (2 digits)')), css_class='col-md-4'),
                    Div(PrependedText('phone', _('Number (6 digits)')), css_class='col-md-4'),
                    Div(PrependedText('address', _('Address')), css_class='col-md-4'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Current situation'),
                Div(
                    Div('classroom', css_class='col-md-6'),
                    Div('section', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Last student formal education'),
                Div(
                    Div('last_education_level', css_class='col-md-6'),
                    Div('last_school_type', css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div('last_school_shift', css_class='col-md-6'),
                    Div('last_school', css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div('last_education_year', css_class='col-md-6'),
                    Div('last_year_result', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Last student informal education'),
                Div(
                    Div('participated_in_alp', css_class='col-md-6'),
                    Div('last_informal_edu_level', css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div('last_informal_edu_round', css_class='col-md-6'),
                    Div('last_informal_edu_final_result', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel'))
            )
        )

    def clean(self):
        super(EnrollmentForm, self).clean()
        # print self.cleaned_data.get('student')
        # cc_myself = self.cleaned_data.get("cc_myself")

    def save(self, user=None):
        print self.fields
        print 'ok'
        return True
        # user_profile = super(EnrollmentForm, self).save(commit=False)
        # if user:
        #     user_profile.user = user
        # user_profile.save()
        # return user_profile

    class Meta:
        model = Enrollment
        fields = '__all__'
        # exclude = ('user', 'full_name', 'mother_fullname',)
        # widgets = {
            # 'employment_status': forms.RadioSelect(),
            # 'sports_group': forms.RadioSelect(),
            # 'student': autocomplete.ModelSelect2(url='student_autocomplete')
        # }

    class Media:
        js = ('js/validator.js', 'js/registrations.js')


class LoggingStudentMoveForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(LoggingStudentMoveForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LoggingStudentMove
        fields = (
            'student',
            'school_from',
            'school_to',
        )
