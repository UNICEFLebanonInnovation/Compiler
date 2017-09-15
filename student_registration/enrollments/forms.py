from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML

from student_registration.students.models import (
    Person,
    Student,
    IDType,
    Nationality,
)
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    EducationLevel,
    ClassLevel,
)
from student_registration.alp.models import ALPRound
from .models import Enrollment, LoggingStudentMove, EducationYear
from .serializers import EnrollmentSerializer

YES_NO_CHOICE = ((1, "Yes"), (0, "No"))

EDUCATION_YEARS = list((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, Person.CURRENT_YEAR))
EDUCATION_YEARS.append(('na', 'n/a'))

YEARS = list(((str(x), x) for x in range(1930, Person.CURRENT_YEAR)))
YEARS.append(('', _('---------')))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.append(('', _('--------')))


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
        exclude = (
            'registered_in_unhcr',
        )


class EnrollmentForm(forms.ModelForm):

    new_registry = forms.TypedChoiceField(
        label=_("First time registered?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True, initial=0
    )
    student_outreached = forms.TypedChoiceField(
        label=_("Student outreached?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True, initial=1
    )
    have_barcode = forms.TypedChoiceField(
        label=_("Have barcode with him?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=False, initial=1
    )
    search_barcode = forms.CharField(widget=forms.TextInput, required=False)
    search_student = forms.CharField(widget=forms.TextInput, required=False)
    search_school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        empty_label=_('-------'),
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
        required=True
    )

    student_first_name = forms.CharField(widget=forms.TextInput, required=True)
    student_father_name = forms.CharField(widget=forms.TextInput, required=True)
    student_last_name = forms.CharField(widget=forms.TextInput, required=True)
    student_sex = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('', _('--------')),
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
            ('', _('-------')),
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
    student_registered_in_unhcr = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO_CHOICE,
    )
    student_id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id', empty_label=_('Student ID Type')
    )
    student_id_number = forms.CharField(widget=forms.TextInput, required=True)

    student_phone_prefix = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 2})), required=True)
    student_phone = forms.CharField(widget=forms.TextInput(attrs=({'maxlength': 6})), required=True)
    student_address = forms.CharField(widget=forms.TextInput, required=True)

    classroom = forms.ModelChoiceField(
        queryset=ClassRoom.objects.exclude(name='n/a'), widget=forms.Select,
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
    last_school_type = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=Enrollment.SCHOOL_TYPE
    )
    last_school_shift = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=Enrollment.SCHOOL_SHIFT
    )
    last_school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('School'),
        required=True, to_field_name='id',
    )
    last_education_year = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=EDUCATION_YEARS,
        initial='na',
    )
    last_year_result = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('na', _('n/a')),
            ('graduated', _('Graduated')),
            ('failed', _('Failed'))
        )
    )
    participated_in_alp = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('na', _('n/a')),
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
    student_outreach_child = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EnrollmentForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.fields['classroom'].empty_label = _('-------')
        self.fields['section'].empty_label = _('-------')

        self.fields['last_education_level'].empty_label = _('-------')
        self.fields['last_school_type'].empty_label = _('-------')
        self.fields['last_school_shift'].empty_label = _('-------')
        self.fields['last_school'].empty_label = _('-------')
        self.fields['last_education_year'].empty_label = _('-------')
        self.fields['last_year_result'].empty_label = _('-------')
        self.fields['last_informal_edu_level'].empty_label = _('-------')
        self.fields['last_informal_edu_round'].empty_label = _('-------')
        self.fields['last_informal_edu_final_result'].empty_label = _('-------')

        form_action = ''
        display_registry = ''
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            display_registry = ' d-none'
            form_action = reverse('enrollments:edit', kwargs={'pk': instance.id})
        else:
            form_action = reverse('enrollments:add')

        if self.request:
            search_id = ''
            search_parameter = ''
            if self.request.GET.get('enrollment_id', ''):
                search_parameter = 'enrollment_id'
                search_id = self.request.GET.get('enrollment_id')
            elif self.request.GET.get('child_id', 0):
                search_parameter = 'child_id'
                search_id = self.request.GET.get('child_id')

            self.helper.form_action = '{form_action}?{search_parameter}={search_id}&new_registry={new_registry}&student_outreached={student_outreached}&have_barcode={have_barcode}'.format(
                form_action=form_action,
                search_parameter=search_parameter,
                search_id=search_id,
                new_registry=self.request.GET.get('new_registry'),
                student_outreached=self.request.GET.get('student_outreached'),
                have_barcode=self.request.GET.get('have_barcode')
            )
        else:
            self.helper.form_action = form_action

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registry') + '</h4>')
                ),
                Div(
                    'student_id',
                    'enrollment_id',
                    'student_outreach_child',
                    HTML('<span class="badge badge-default">1</span>'),
                    Div(InlineRadios('new_registry'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div(InlineRadios('student_outreached'), css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div(InlineRadios('have_barcode'), css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry, css_id='registry_block'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Register by Barcode')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_barcode', css_class='col-md-4'),
                    css_class='row',
                ),
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Search old student (fullname Or ID number)')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('school_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('search_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Basic Data')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('registration_date', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('outreach_barcode', css_class='col-md-3', css_id='block_id_outreach_barcode'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('student_registered_in_unhcr', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">18</span>'),
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
                    Div('classroom', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Last student formal education')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('last_education_level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('last_school_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('last_school_shift', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('last_school', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('last_education_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('last_year_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">'+_('Last student informal education')+'</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('participated_in_alp', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('last_informal_edu_level', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('last_informal_edu_round', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('last_informal_edu_final_result', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning child_data'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
            )
        )

    # def clean(self):
    #     super(EnrollmentForm, self).clean()
        # print self.cleaned_data
        # cc_myself = self.cleaned_data.get("cc_myself")

    def save(self, request=None, instance=None):
        if instance:
            serializer = EnrollmentSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
        else:
            serializer = EnrollmentSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.school = request.user.school
                instance.owner = request.user
                instance.education_year = EducationYear.objects.get(current_year=True)
                instance.save()

    class Meta:
        model = Enrollment
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
            'classroom',
            'last_year_result',
            'last_school_type',
            'last_school_shift',
            'last_school',
            'last_education_level',
            'last_education_year',
            'outreach_barcode',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = (
            'js/jquery-1.12.3.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class GradingTerm1Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GradingTerm1Form, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:grading', kwargs={'pk': instance.id, 'term': 1})

        if instance.classroom_id in [2, 3, 4]:
            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grading Term 1') + '</h4>')
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_science', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        'exam_result_history',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        'exam_total',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
                )
            )

        if instance.classroom_id in [5, 6, 7]:
            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grading Term 1') + '</h4>')
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_science', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        'exam_result_history',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
                )
            )

        if instance.classroom_id in [8, 9, 10]:
            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grading Term 1') + '</h4>')
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_arabic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('exam_result_language', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('exam_result_education', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('exam_result_geo', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_history', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_math', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_physic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_chemistry', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_bio', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        'exam_result_science',
                        'exam_result_linguistic_ar',
                        'exam_result_linguistic_en',
                        'exam_result_sociology',
                        'exam_result_physical',
                        'exam_result_artistic',
                        'exam_result_mathematics',
                        'exam_result_sciences',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
                )
            )

        if instance.classroom_id == 1:
            self.helper.layout = Layout(
                Fieldset(
                    None,
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grading Term 1') + '</h4>')
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_linguistic_ar', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_linguistic_en', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_sociology', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_physical', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(

                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_artistic', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_mathematics', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result_sciences', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_total', css_class='col-md-2'),
                        HTML('<span class="badge badge-default">1</span>'),
                        Div('exam_result', css_class='col-md-2'),
                        css_class='row',
                    ),
                    Div(
                        'exam_result_arabic',
                        'exam_result_language',
                        'exam_result_education',
                        'exam_result_geo',
                        'exam_result_history',
                        'exam_result_math',
                        'exam_result_science',
                        'exam_result_physic',
                        'exam_result_chemistry',
                        'exam_result_bio',
                        css_class='d-none'
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                FormActions(
                    Submit('save', _('Save')),
                    HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
                )
            )

    def save(self, instance=None, request=None):
        instance = super(GradingTerm1Form, self).save()

    class Meta:
        model = Enrollment
        fields = (
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_linguistic_en',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class GradingTerm2Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GradingTerm2Form, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:grading', kwargs={'pk': instance.id, 'term': 2})
        if instance.classroom == 1:
            pass

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grading Term 2') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('exam_result_arabic_cmplt', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('exam_result_language_cmplt', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('exam_result_math_cmplt', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('exam_total_cmplt', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('exam_result_final', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(GradingTerm2Form, self).save()

    class Meta:
        model = Enrollment
        fields = (
            'exam_result_arabic_cmplt',
            'exam_result_language_cmplt',
            'exam_result_math_cmplt',
            'exam_total_cmplt',
            'exam_result_final',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class StudentMovedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        moved = kwargs.pop('moved', None)
        super(StudentMovedForm, self).__init__(*args, **kwargs)
        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('enrollments:moved',
                                          kwargs={'pk': instance.id, 'moved': moved}
                                          )
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Registration') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('classroom', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('section', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/enrollments/list/">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(StudentMovedForm, self).save()
        instance.owner = request.user
        instance.school = request.user.school
        instance.moved = False
        instance.save()

    class Meta:
        model = Enrollment
        fields = (
            'classroom',
            'section',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


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
            'education_year',
            'student',
            'school_from',
            'school_to',
        )
