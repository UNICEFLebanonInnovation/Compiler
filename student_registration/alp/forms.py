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


class OutreachAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    pre_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                     required=False)

    post_test_total = forms.CharField(widget=forms.TextInput(attrs=({'readonly': 'readonly'})),
                                      required=False)

    def __init__(self, *args, **kwargs):
        super(OutreachAdminForm, self).__init__(*args, **kwargs)
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


class OutreachForm(forms.ModelForm):

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

    def __init__(self, *args, **kwargs):
        super(OutreachForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            self.helper.form_action = reverse('alp:outreach_edit', kwargs={'pk': instance.id})
        else:
            self.helper.form_action = reverse('alp:outreach_add')
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Basic Data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('student_registered_in_unhcr'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel')),
                HTML('<a class="btn btn-info" href="/alp/outreach/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
        else:
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
        )
        initial_fields = fields

    class Media:
        js = (
            # 'js/bootstrap-datetimepicker.js',
            # 'js/validator.js',
            # 'js/registrations.js'
        )


class PreTestForm(forms.ModelForm):

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

    def __init__(self, *args, **kwargs):
        super(PreTestForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            self.helper.form_action = reverse('alp:pretest_edit', kwargs={'pk': instance.id})
        else:
            self.helper.form_action = reverse('alp:pretest_add')
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Basic Data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('student_registered_in_unhcr'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grades') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_science', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel')),
                HTML('<a class="btn btn-info" href="/alp/pre-test/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
        else:
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
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
        )
        initial_fields = fields

    class Media:
        js = (
            # 'js/bootstrap-datetimepicker.js',
            # 'js/validator.js',
            # 'js/registrations.js'
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

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.fields['registered_in_level'].empty_label = _('Current Class')
        self.fields['section'].empty_label = _('Current Section')

        self.fields['last_education_level'].empty_label = _('Last education level')
        self.fields['last_education_year'].empty_label = _('Education year')

        self.fields['last_informal_edu_level'].empty_label = _('ALP level')
        self.fields['last_informal_edu_round'].empty_label = _('ALP round')
        self.fields['last_informal_edu_final_result'].empty_label = _('ALP result')

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            self.helper.form_action = reverse('alp:edit', kwargs={'pk': instance.id})
        else:
            self.helper.form_action = reverse('alp:add')
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registry') + '</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('new_registry'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('student_outreached'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('have_barcode'), css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Register by Barcode') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='d-none'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Search old student (fullname Or ID number)') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Basic Data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('outreach_barcode', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('student_registered_in_unhcr'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Current situation') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('registered_in_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Last student formal education') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_education_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_education_year', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Last student informal education') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participated_in_alp', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_informal_edu_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_informal_edu_round', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_informal_edu_final_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel')),
                HTML('<a class="btn btn-info" href="/alp/list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
        else:
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
        )
        initial_fields = fields

    class Media:
        js = (
            # 'js/bootstrap-datetimepicker.js',
            # 'js/validator.js',
            # 'js/registrations.js'
        )


class PreTestGradingForm(forms.ModelForm):

    exam_result_arabic = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    exam_language = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Exam language')),
            ('english', _('English')),
            ('french', _('French'))
        )
    )
    exam_result_language = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    exam_result_math = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    exam_result_science = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(PreTestGradingForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.fields['level'].empty_label = _('Level')

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('alp:pre_test_grading', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Entrance Test') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('level', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grades') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_science', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel')),
                HTML('<a class="btn btn-info" href="/alp/pre-test/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PreTestGradingForm, self).save()
        instance.modified_by = request.user
        instance.save()

    class Meta:
        model = Outreach
        fields = (
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )


class PostTestGradingForm(forms.ModelForm):

    post_exam_result_arabic = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    post_exam_language = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('Exam language')),
            ('english', _('English')),
            ('french', _('French'))
        )
    )
    post_exam_result_language = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    post_exam_result_math = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )
    post_exam_result_science = forms.FloatField(
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=60, min_value=0,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(PostTestGradingForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('alp:post_test_grading', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Post-test Grades') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_result_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_result_science', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                Button('cancel', _('Cancel')),
                HTML('<a class="btn btn-info" href="/alp/post-test/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PostTestGradingForm, self).save()
        instance.modified_by = request.user
        instance.save()

    class Meta:
        model = Outreach
        fields = (
            'post_exam_result_arabic',
            'post_exam_language',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )
