from __future__ import unicode_literals, absolute_import, division

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from bootstrap3_datetime.widgets import DateTimePicker

from .models import Outreach, ALPRound
from .serializers import OutreachSerializer
from student_registration.students.models import (
    Student,
    Nationality,
    IDType
)
from student_registration.schools.models import (
    School,
    EducationLevel,
    ClassLevel,
    Section,
    ClassRoom
)

YES_NO_CHOICE = ((1, "Yes"), (0, "No"))

EDUCATION_YEARS = list((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, 2021))
EDUCATION_YEARS.append(('0', _('Last education year')))
EDUCATION_YEARS.append(('n/a', 'N/A'))

YEARS = list(((str(x), x) for x in range(1930, 2051)))
YEARS.append(('', _('Birthday Year')))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.append(('', _('Birthday Day')))


class OutreachForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    pre_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                     required=False)

    post_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(OutreachForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['pre_test_total'].initial = instance.exam_total
            self.fields['post_test_total'].initial = instance.post_exam_total

    class Meta:
        model = Outreach
        fields = '__all__'
        exclude = (
            'partner',
            'location',
            'preferred_language',
            'last_class_level',
            'average_distance',
            'exam_year',
            'exam_month',
            'exam_day',
            'grade',
            'classroom',
            'alp_year',
            'exam_school',
            'enrolled_in_this_school',
            'not_enrolled_in_this_school',
            'exam_not_exist_in_school',
            'registered_in_school',
            'exam_corrector_arabic',
            'exam_corrector_language',
            'exam_corrector_math',
            'exam_corrector_science',
            'post_exam_corrector_arabic',
            'post_exam_corrector_language',
            'post_exam_corrector_math',
            'post_exam_corrector_science',
            'last_year_result',
            'last_informal_edu_result',
            'last_informal_edu_year',
        )


class RegistrationForm(forms.ModelForm):

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
        choices=YEARS
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
        choices=DAYS
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

    registered_in_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=1
    )

    last_education_level = forms.ModelChoiceField(
        label=_('Last education level'),
        queryset=ClassRoom.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    last_education_year = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=EDUCATION_YEARS,
        initial='0',
    )
    participated_in_alp = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Participated in ALP')),
            ('yes', _('Yes')),
            ('no', _('No')),
        )
    )
    last_informal_edu_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    last_informal_edu_round = forms.ModelChoiceField(
        queryset=ALPRound.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    last_informal_edu_final_result = forms.ModelChoiceField(
        queryset=ClassLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )

    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    school = forms.CharField(widget=forms.HiddenInput, required=False)
    owner = forms.CharField(widget=forms.HiddenInput, required=False)
    alp_round = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['registered_in_level'].empty_label = _('Current Class')
        self.fields['section'].empty_label = _('Current Section')

        self.fields['last_education_level'].empty_label = _('Last education level')
        self.fields['last_education_year'].empty_label = _('Education year')

        self.fields['last_informal_edu_level'].empty_label = _('ALP level')
        self.fields['last_informal_edu_round'].empty_label = _('ALP round')
        self.fields['last_informal_edu_final_result'].empty_label = _('ALP result')

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_action = reverse('alp:add')
        self.helper.layout = Layout(
            Fieldset(
                _('Registry'),
                Div(
                    'student_id',
                    'enrollment_id',
                    'school',
                    'owner',
                    'alp_round',
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
                    Div('search_school', css_class='col-md-4'),
                    Div(PrependedText('search_student', _('Search old student')), css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='search_options', css_class='invisible'
            ),
            Fieldset(
                _('Basic Data'),
                Div(
                    Div(PrependedText('outreach_barcode', _('Outreach Barcode')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('student_first_name', _('First Name')), css_class='col-md-4'),
                    Div(PrependedText('student_father_name', _('Father Name')), css_class='col-md-4'),
                    Div(PrependedText('student_last_name', _('Last Name')), css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('student_birthday_year', css_class='col-md-4'),
                    Div('student_birthday_month', css_class='col-md-4'),
                    Div('student_birthday_day', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('student_sex', css_class='col-md-4'),
                    Div('student_nationality', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(PrependedText('student_mother_fullname', _('Mother Full name')), css_class='col-md-4'),
                    Div('student_mother_nationality', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div(InlineRadios('student_registered_in_unhcr'), css_class='col-md-4'),
                    Div('student_id_type', css_class='col-md-4'),
                    Div(PrependedText('student_id_number', _('ID Number')), css_class='col-md-4'),
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
                    Div('registered_in_level', css_class='col-md-6'),
                    Div('section', css_class='col-md-6'),
                    css_class='row',
                ),
                css_class='invisible child_data'
            ),
            Fieldset(
                _('Last student formal education'),
                Div(
                    Div('last_education_level', css_class='col-md-6'),
                    Div('last_education_year', css_class='col-md-6'),
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

    def save(self, request=None):
        serializer = OutreachSerializer(data=request.POST)
        if serializer.is_valid():
            instance = serializer.create(validated_data=serializer.validated_data)
            instance.school = request.user.school
            instance.owner = request.user
            instance.alp_round = ALPRound.objects.get(current_round=True)
            instance.save()

    class Meta:
        model = Outreach
        fields = (
            'student_id',
            'enrollment_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_nationality',
            'student_mother_nationality',
            'student_registered_in_unhcr',
            'participated_in_alp',
            'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
            'student_address',
            'section',
            'registered_in_level',
            'last_education_level',
            'last_education_year',
            'outreach_barcode',
            'owner',
            # 'alp_round',
        )
        initial_fields = fields

    class Media:
        js = (
            # 'js/bootstrap-datetimepicker.js',
            # 'js/validator.js',
            # 'js/registrations.js'
        )
