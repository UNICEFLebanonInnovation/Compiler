from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
import json
from dal import autocomplete
from django.core.urlresolvers import reverse
from .models import Enrollment, LoggingStudentMove, EducationYear
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
    School,
    Section
)
from .serializers import EnrollmentSerializer

YES_NO_CHOICE = ((1, "Yes"), (0, "No"))


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

    new_registry = forms.TypedChoiceField(
        label=_("First time registered?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_outreached = forms.TypedChoiceField(
        label=_("Student outreached?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    have_barcode = forms.TypedChoiceField(
        label=_("Have barcode with him?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False,
    )
    search_barcode = forms.CharField(widget=forms.TextInput, required=False)
    search_student = forms.CharField(widget=forms.TextInput, required=False)
    search_school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        empty_label=_('Search by school'),
        required=False, to_field_name='id',
        initial=0
    )
    school_type = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=(
            ('', _('School type')),
            ('alp', _('ALP')),
            ('2ndshift', _('2nd Shift')),
        )
    )

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

    student_first_name = forms.CharField(widget=forms.TextInput, required=True)
    student_father_name = forms.CharField(widget=forms.TextInput, required=True)
    student_last_name = forms.CharField(widget=forms.TextInput, required=True)
    student_sex = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Gender')),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    student_birthday_year = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=((str(x), x) for x in range(1930, 2051))
    )
    student_birthday_month = forms.ChoiceField(
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
    student_birthday_day = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=((str(x), x) for x in range(1, 32))
    )

    student_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select,
        empty_label=_('Student nationality'),
        required=True, to_field_name='id',
    )

    student_mother_fullname = forms.CharField(widget=forms.TextInput, required=True)
    student_mother_nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(), widget=forms.Select,
        empty_label=_('Mather nationality'),
        required=True, to_field_name='id',
    )
    student_registered_in_unhcr = forms.TypedChoiceField(
        label=_("Registered in UNHCR?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id', empty_label=_('Student ID Type')
    )
    student_id_number = forms.CharField(widget=forms.TextInput, required=True)

    student_phone_prefix = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 2})), required=True)
    student_phone = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 6})), required=True)
    student_address = forms.CharField(widget=forms.TextInput, required=True)

    section = forms.ModelChoiceField(
        queryset=Section.objects.all(), widget=forms.Select,
        empty_label=_('Section'),
        required=False, to_field_name='id',
        initial=1
    )




    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)
    school = forms.CharField(widget=forms.HiddenInput, required=False)
    owner = forms.CharField(widget=forms.HiddenInput, required=False)
    education_year = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)
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
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    'school',
                    'owner',
                    'education_year',
                    Div(InlineRadios('new_registry'), css_class='col-md-4'),
                    Div(InlineRadios('student_outreached'), css_class='col-md-4'),
                    Div(InlineRadios('have_barcode'), css_class='col-md-4 invisible', css_id='have_barcode_option'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Register by Barcode'),
                Div(
                    Div(PrependedText('search_barcode', _('Search child by barcode')), css_class='col-md-6'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='invisible'
            ),
            Fieldset(
                _('Search old student (fullname Or ID number)'),
                Div(
                    Div('school_type', css_class='col-md-4'),
                    Div('search_school', css_class='col-md-4'),
                    Div(PrependedText('search_student', _('Search old student')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('outreach_barcode', _('Outreach Barcode')), css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='search_options', css_class='invisible'
            ),
            Fieldset(
                _('Basic Data'),
                Div(
                    Div(PrependedText('registration_date', _('Registration date')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('student_first_name', _('First Name')), css_class='col-md-4'),
                    Div(PrependedText('student_father_name', _('Father Name')), css_class='col-md-4'),
                    Div(PrependedText('student_last_name', _('Last Name')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('student_sex', css_class='col-md-3'),
                    Div('student_birthday_year', css_class='col-md-2'),
                    Div('student_birthday_month', css_class='col-md-2'),
                    Div('student_birthday_day', css_class='col-md-2'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('student_mother_fullname', _('Mother Full name')), css_class='col-md-4'),
                    Div('student_mother_nationality', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(InlineRadios('student_registered_in_unhcr', _('Registered in UNHCR')), css_class='col-md-4'),
                    Div('student_id_type', css_class='col-md-4'),
                    Div(PrependedText('student_id_number', _('Student ID Number')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('student_phone_prefix', _('Prefix (2 digits)')), css_class='col-md-4'),
                    Div(PrependedText('student_phone', _('Number (6 digits)')), css_class='col-md-4'),
                    Div(PrependedText('student_address', _('Address')), css_class='col-md-4'),
                    css_class='row',
                ),
                css_class='invisible child_data'
            ),
            Fieldset(
                _('Current situation'),
                Div(
                    Div('classroom', css_class='col-md-6'),
                    Div('section', css_class='col-md-6'),
                    css_class='row',
                ),
                css_class='invisible child_data'
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
                css_class='invisible child_data'
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
                css_class='invisible child_data'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel'))
            )
        )

    # def clean(self):
    #     super(EnrollmentForm, self).clean()
        # print self.cleaned_data
        # cc_myself = self.cleaned_data.get("cc_myself")

    def save(self, request=None):
        # instance = super(EnrollmentForm, self).save()
        # instance.school = request.user.school
        # instance.owner = request.user
        # instance.education_year = EducationYear.objects.get(current_year=True)
        # if request.POST.get('student_id'):
        #     student = Student.objects.get(id=int(request.POST.get('student_id'))).update(request.POST)
        # else:
        #     student = Student.create(request.POST)
        # instance.student = student
        # instance.save()
        serializer = EnrollmentSerializer(data=request.POST)
        if serializer.is_valid():
            instance = serializer.create(validated_data=serializer.validated_data)
            instance.school = request.user.school
            instance.owner = request.user
            instance.education_year = EducationYear.objects.get(current_year=True)
            instance.save()

    class Meta:
        model = Enrollment
        fields = '__all__'
            # (
            # 'student_id',
            # 'enrollment_id',
            # 'student_first_name',
            # 'student_father_name',
            # 'student_last_name',
            # 'student_mother_fullname',
            # 'student_sex',
            # 'student_birthday_year',
            # 'student_birthday_month',
            # 'student_birthday_day',
            # 'student_phone',
            # 'student_phone_prefix',
            # 'student_id_number',
            # 'student_id_type',
            # 'student_nationality',
            # 'student_mother_nationality',
            # 'registered_in_unhcr',
            # 'participated_in_alp',
            # 'last_informal_edu_level',
            # 'last_informal_edu_round',
            # 'last_informal_edu_final_result',
            # 'student_address',
            # 'section',
            # 'classroom',
            # 'last_year_result',
            # 'last_school_type',
            # 'last_school_shift',
            # 'last_school',
            # 'last_education_level',
            # 'last_education_year',
            # 'outreach_barcode',
            # 'owner',
            # 'moved',
            # 'exam_result_arabic',
            # 'exam_result_language',
            # 'exam_result_education',
            # 'exam_result_geo',
            # 'exam_result_history',
            # 'exam_result_math',
            # 'exam_result_science',
            # 'exam_result_physic',
            # 'exam_result_chemistry',
            # 'exam_result_bio',
            # 'exam_result_linguistic_ar',
            # 'exam_result_linguistic_en',
            # 'exam_result_sociology',
            # 'exam_result_physical',
            # 'exam_result_artistic',
            # 'exam_result_mathematics',
            # 'exam_result_sciences',
            # 'exam_total',
            # 'exam_result',
            # 'education_year',
            # 'education_year_name',
        # )
        initial_fields = fields
        widgets = {
            'employment_status': forms.RadioSelect(),
            'sports_group': forms.RadioSelect(),
            'student': autocomplete.ModelSelect2(url='student_autocomplete')
        }

    class Media:
        js = ('js/bootstrap-datetimepicker.js', 'js/validator.js', 'js/registrations.js')


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
