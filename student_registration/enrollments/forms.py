from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from .models import Enrollment, LoggingStudentMove
from student_registration.students.models import Student

from model_utils import Choices
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from bootstrap3_datetime.widgets import DateTimePicker
from student_registration.students.models import (
    IDType,
    Nationality,
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
        widget=forms.TextInput, required=True,
        choices=((str(x), x) for x in range(1930, 2051))
    )
    birthday_month = forms.ChoiceField(
        widget=forms.TextInput, required=True,
        choices=(
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
        widget=forms.TextInput, required=True,
        choices=((str(x), x) for x in range(1, 32))
    )
    phone = forms.CharField(widget=forms.TextInput, required=True)
    phone_prefix = forms.CharField(widget=forms.TextInput, required=True)
    nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select(attrs=({'placeholder': _('Nationality')})),
        required=True, to_field_name='id',
    )

    mother_fullname = forms.CharField(widget=forms.TextInput, required=True)
    mother_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select(attrs=({'placeholder': _('Mother Nationality')})),
        required=True, to_field_name='id',
    )
    registered_in_unhcr = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=YES_NO_CHOICE,
        widget=forms.RadioSelect
    )
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(), widget=forms.Select(attrs=({'placeholder': _('ID Type')})),
        required=True, to_field_name='id',
    )
    id_number = forms.CharField(widget=forms.TextInput, required=True)

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['id_type'].empty_label = _('ID Type')
        self.fields['id_number'].empty_label = _('ID Number')
        self.fields['sex'].empty_label = _('Gender')
        self.fields['nationality'].empty_label = _('Nationality')
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
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
                    Div(PrependedText('sex', _('Gender')), css_class='col-md-4'),
                    Div('nationality', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('birthday_year', css_class='col-md-4'),
                    Div('birthday_Month', css_class='col-md-4'),
                    Div('birthday_day', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('mother_fullname', _('Mother Full name')), css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div('id_type', css_class='col-md-6',),
                    Div(PrependedText('id_number', _('ID Number')), css_class='col-md-6', ),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('disability', _('Disability')), css_class='col-md-4', ),
                    Div('sex', css_class='col-md-4', ),
                    Div(PrependedText('birthdate', _('Birthdate')), css_class='col-md-4', ),
                    css_class='row',
                ),
                Div(
                    Div('nationality', css_class='col-md-4', ),
                    Div(PrependedText('phone', _('Phone Number')), css_class='col-md-4', ),
                    Div(PrependedText('parents_phone_number', _('Parents Phone Number')), css_class='col-md-4', ),
                    css_class='row',
                ),
                Div(
                    Div('location', css_class='col-md-6', ),
                    Div('partner_organization', css_class='col-md-6', ),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Educational Information'),
                Div(
                    Div(
                        HTML(_('1. Have you ever attended school or other training programs?')),
                        'education_status', css_class='col-md-4',
                    ),
                    Div(
                        HTML(_('1.a What type of education are/were you enrolled in?')),
                        'education_type', css_class='col-md-4',
                    ),
                    Div(
                        HTML(_('1.b What is the level of education you have successfully completed?')),
                        'education_level', css_class='col-md-4',
                    ),
                    css_class='row',
                ),
                HTML(_('2. What were your reason(s) for stopping studying? Please tick all that apply?')),
                Field('leaving_education_reasons'),
            ),
            Fieldset(
                _('Livelihood Information'),
                Div(
                    Div(
                        HTML(_('1. Relationship with Labour Market')),
                        Field('employment_status'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('2. What is the sector(s) you worked in / or are working in?')),
                        Field('employment_sectors'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div(
                        HTML(_('3. If you are currently not working, are you searching for work now?')),
                        Div('looking_for_work'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('3.a If yes, through whom? (select multiple)')),
                        Div('through_whom'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div(
                        HTML(_('4. What are the obstacles in searching for/or having work?')),
                        Div('obstacles_for_work'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('4.a Do you participate in supporting your family financially?')),
                        Div('supporting_family'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div(
                        HTML(_('5. Please check all the choice(s) that best describes your household composition')),
                        Div('household_composition'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('6. How many members in your household work?')),
                        Div('household_working'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Follow-up Availability'),
                Div(
                    Div(
                        HTML(_('1. Have you attended any kind of training before?')),
                        Div('trained_before'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('1.a If not, why?')),
                        Div('not_trained_reason'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div(
                        HTML(_('How did you know about this program?')),
                        Div('referred_by'),
                        css_class='col-md-6'),
                    Div(
                        HTML(_('4. We would like to follow up with you after the training, what is your preferred method of communication?')),
                        Div('communication_preference'),
                        css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel'))
            )
        )

    def save(self, user=None):
        print self
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

    # class Media:
    #     js = ('js/bootstrap-datetimepicker.js', )


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
