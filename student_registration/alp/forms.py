from __future__ import unicode_literals, absolute_import, division

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib import messages

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML

from .models import Outreach, ALPRound
from .serializers import OutreachSerializer, OutreachSmallSerializer
from student_registration.students.models import (
    Person,
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

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

EDUCATION_YEARS = list((str(x-1)+'/'+str(x), str(x-1)+'/'+str(x)) for x in range(2001, Person.CURRENT_YEAR+1))
EDUCATION_YEARS.append(('na', 'n/a'))

YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-18, Person.CURRENT_YEAR-5)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))

GENDER = (('', '----------'), ('Male', _('Male')), ('Female', _('Female')))
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
EXAM_LANGUAGES = (
            ('', _('Exam language')),
            ('english', _('English')),
            ('french', _('French'))
        )
ROOMS = list(((str(x), str(x)) for x in range(1, 20)))


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

    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
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
        choices=GENDER
    )
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
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
    student_mother_nationality = forms.ModelChoiceField(
        label=_("Mother nationality"),
        queryset=Nationality.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_registered_in_unhcr = forms.ChoiceField(
        label=_("Registered in UNHCR"),
        widget=forms.Select, required=True,
        choices=YES_NO_CHOICE,
        initial=1
    )
    student_id_type = forms.ModelChoiceField(
        label=_("ID type"),
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id'
    )
    student_id_number = forms.CharField(
        label=_("ID number"),
        widget=forms.TextInput, required=True
    )
    student_phone_prefix = forms.CharField(
        label=_("Phone prefix"),
        widget=forms.TextInput(attrs=({'maxlength': 2})), required=True
    )
    student_phone = forms.CharField(
        label=_("Phone number"),
        widget=forms.TextInput(attrs=({'maxlength': 6})), required=True
    )
    student_address = forms.CharField(
        label=_("Address"),
        widget=forms.TextInput, required=True
    )

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
                    Div('school', css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_first_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('student_father_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('student_last_name', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('student_registered_in_unhcr', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">16</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">17</span>'),
                    Div('student_address', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                Submit('save_add_another', _('Save and add another'), css_class='child_data'),
                HTML('<a class="btn btn-info cancel-button" href="/alp/outreach/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSmallSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = OutreachSmallSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                # instance.school = request.user.school
                instance.owner = request.user
                instance.alp_round = ALPRound.objects.get(current_pre_test=True)
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

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
            'js/jquery-3.3.1.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class PreTestForm(forms.ModelForm):

    school = forms.ModelChoiceField(
        label=_('School'),
        queryset=School.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
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
        choices=GENDER
    )
    level = forms.ModelChoiceField(
        label=_('Entrance test'),
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    pre_test_room = forms.ChoiceField(
        label=_('Pre-test room'),
        widget=forms.Select, required=True,
        choices=ROOMS
    )
    exam_result_arabic = forms.FloatField(
        label=_('Arabic'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_language = forms.ChoiceField(
        label=_('Exam language'),
        widget=forms.Select, required=True,
        choices=EXAM_LANGUAGES
    )
    exam_result_language = forms.FloatField(
        label=_('Foreign Language'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_result_math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_result_science = forms.FloatField(
        label=_('Science'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )

    def __init__(self, *args, **kwargs):
        super(PreTestForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            self.helper.form_action = reverse('alp:pre_test_edit', kwargs={'pk': instance.id})
        else:
            self.helper.form_action = reverse('alp:pre_test_add')
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Entrance test') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('school', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('pre_test_room', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Basic Data') + '</h4>')
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
                    Div('student_sex', css_class='col-md-3'),
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
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('exam_result_science', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('pre_comment', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/alp/pre-test/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSmallSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.calculate_pre_result()
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = OutreachSmallSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.alp_round = ALPRound.objects.get(current_pre_test=True)
                instance.calculate_pre_result()
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

    class Meta:
        model = Outreach
        fields = (
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
            'school',
            'pre_test_room',
            'pre_comment'
        )
        initial_fields = fields

    class Media:
        js = (
            'js/jquery-3.3.1.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class RegistrationForm(forms.ModelForm):

    new_registry = forms.ChoiceField(
        label=_("First time registered?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    student_outreached = forms.ChoiceField(
        label=_("Student outreached?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='no'
    )
    have_barcode = forms.ChoiceField(
        label=_("Have barcode with him?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='no'
    )
    search_barcode = forms.CharField(
        label=_("Search a barcode"),
        widget=forms.TextInput,
        required=False
    )
    search_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    search_school = forms.ModelChoiceField(
        label=_("Search by School"),
        queryset=School.objects.all(), widget=forms.Select,
        required=False, to_field_name='id',
        initial=0
    )
    outreach_barcode = forms.RegexField(
        label=_('Outreach barcode'),
        regex=r'^([A-Z]{2})(\d{8})|(-(\d{1}))$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: AA11111111'}),
        required=False
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
        choices=GENDER
    )
    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS
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
    student_mother_nationality = forms.ModelChoiceField(
        label=_("Mother nationality"),
        queryset=Nationality.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    student_registered_in_unhcr = forms.ChoiceField(
        label=_("Registered in UNHCR"),
        widget=forms.Select, required=True,
        choices=YES_NO_CHOICE,
    )
    student_id_type = forms.ModelChoiceField(
        label=_("ID type"),
        queryset=IDType.objects.all(), widget=forms.Select,
        required=True, to_field_name='id'
    )
    student_id_number = forms.CharField(
        label=_("ID number"),
        widget=forms.TextInput, required=True
    )
    student_phone_prefix = forms.CharField(
        label=_("Phone prefix"),
        widget=forms.TextInput(attrs=({'maxlength': 2})), required=True
    )
    student_phone = forms.CharField(
        label=_("Phone number"),
        widget=forms.TextInput(attrs=({'maxlength': 6})), required=True
    )
    student_address = forms.CharField(
        label=_("Address"),
        widget=forms.TextInput, required=True
    )

    registered_in_level = forms.ModelChoiceField(
        label=_("Current Level"),
        queryset=EducationLevel.objects.exclude(name='n/a'), widget=forms.Select,
        required=True, to_field_name='id',
    )
    section = forms.ModelChoiceField(
        label=_("Current Section"),
        queryset=Section.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=1
    )

    last_education_level = forms.ModelChoiceField(
        label=_('Last education level'),
        queryset=ClassRoom.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=11
    )
    last_education_year = forms.ChoiceField(
        label=_("Last Education year"),
        widget=forms.Select, required=True,
        choices=EDUCATION_YEARS,
        initial='na',
    )
    participated_in_alp = forms.ChoiceField(
        label=_("Participated in ALP"),
        widget=forms.Select, required=True,
        choices=(
            ('na', _('n/a')),
            ('yes', _('Yes')),
            ('no', _('No')),
        ),
        initial='na'
    )
    last_informal_edu_level = forms.ModelChoiceField(
        label=_("Last informal education level"),
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=13
    )
    last_informal_edu_round = forms.ModelChoiceField(
        label=_("Last informal education round"),
        queryset=ALPRound.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=8
    )
    last_informal_edu_final_result = forms.ModelChoiceField(
        label=_("Last informal education status"),
        queryset=ClassLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
        initial=27
    )

    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''

        display_registry = ''
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        if instance:
            display_registry = ' d-none'
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
                    Div('new_registry', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('student_outreached', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('have_barcode', css_class='col-md-3', css_id='have_barcode_option'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'+display_registry, css_id='registry_block'
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
                css_id='register_by_barcode', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Search old student (fullname Or ID number)') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('search_school', css_class='col-md-4'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('search_student', css_class='col-md-3'),
                    css_class='row',
                ),
                css_id='search_options', css_class='bd-callout bd-callout-warning'+display_registry
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Basic Data') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">0</span>'),
                    Div('outreach_barcode', css_class='col-md-3'),
                    HTML('<span style="padding-top: 25px;">' +
                         _('The barcode is not required, enter a valid one or leave it empty') +
                         '. <br/><a href="/static/images/barcode_example.png" target="_blank">' +
                         _('Click to see the barcode') + '</a></span>'),
                    css_class='row',
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
                    Div('student_birthday_year', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('student_birthday_month', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('student_birthday_day', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('student_sex', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('student_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('student_mother_fullname', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('student_mother_nationality', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('student_registered_in_unhcr', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('student_id_type', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('student_id_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('student_phone_prefix', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('student_phone', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">16</span>'),
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
                    HTML('<span class="badge badge-default">2</span>'),
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
                    HTML('<span class="badge badge-default">2</span>'),
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
                Submit('save', _('Save'), css_class='child_data'),
                Submit('save_add_another', _('Save and add another'), css_class='child_data'),
                HTML('<a class="btn btn-info cancel-button" href="/alp/list/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def clean(self):
        from django.db.models import Q
        cleaned_data = super(RegistrationForm, self).clean()
        student_first_name = cleaned_data.get('student_first_name')
        student_father_name = cleaned_data.get('student_father_name')
        student_last_name = cleaned_data.get('student_last_name')
        student_mother_fullname = cleaned_data.get('student_mother_fullname')
        student_id_number = cleaned_data.get('student_id_number')
        student_birthday_year = cleaned_data.get('student_birthday_year')
        student_birthday_day = cleaned_data.get('student_birthday_day')
        student_birthday_month = cleaned_data.get('student_birthday_month')
        edit = cleaned_data.get('student_id')
        if not edit:
            if (Student.objects.filter(
                Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                  mother_fullname=student_mother_fullname, birthday_year=student_birthday_year, birthday_month=
                  student_birthday_month, birthday_day=student_birthday_day)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    mother_fullname=student_mother_fullname, id_number=student_id_number)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    id_number=student_id_number, birthday_year=student_birthday_year,
                    birthday_month=student_birthday_month,
                    birthday_day=student_birthday_day)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    id_number=student_id_number, birthday_year=student_birthday_year)).count()):
                raise forms.ValidationError(_('Student name, already entered  '))
        else:
            if (Student.objects.filter(
                Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                  mother_fullname=student_mother_fullname, birthday_year=student_birthday_year, birthday_month=
                  student_birthday_month, birthday_day=student_birthday_day)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    mother_fullname=student_mother_fullname, id_number=student_id_number)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    id_number=student_id_number, birthday_year=student_birthday_year,
                    birthday_month=student_birthday_month,
                    birthday_day=student_birthday_day)
                | Q(first_name=student_first_name, father_name=student_father_name, last_name=student_last_name,
                    id_number=student_id_number, birthday_year=student_birthday_year)
            ).exclude(id=edit).count()):
                raise forms.ValidationError(_('Student name, already entered  '))

    def save(self, instance=None, request=None):
        if instance:
            serializer = OutreachSerializer(instance, data=request.POST)
            if serializer.is_valid():
                serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = OutreachSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.school = request.user.school
                instance.owner = request.user
                instance.alp_round = ALPRound.objects.get(current_round=True)
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

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
            'new_registry',
            'student_outreached',
            'have_barcode',
        )
        initial_fields = fields

    class Media:
        js = (
            'js/jquery-3.3.1.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/validator.js',
            'js/registrations.js',
        )


class PreTestGradingForm(forms.ModelForm):

    level = forms.ModelChoiceField(
        label=_('Entrance test'),
        queryset=EducationLevel.objects.all(), widget=forms.Select,
        required=True, to_field_name='id',
    )
    pre_test_room = forms.ChoiceField(
        label=_('Pre-test room'),
        widget=forms.Select, required=True,
        choices=ROOMS
    )
    exam_result_arabic = forms.FloatField(
        label=_('Arabic'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_language = forms.ChoiceField(
        label=_('Exam language'),
        widget=forms.Select, required=True,
        choices=EXAM_LANGUAGES
    )
    exam_result_language = forms.FloatField(
        label=_('Foreign Language'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_result_math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )
    exam_result_science = forms.FloatField(
        label=_('Science'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=True
    )

    def __init__(self, *args, **kwargs):
        super(PreTestGradingForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('alp:pre_test_grading', kwargs={'pk': instance.id})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Entrance test') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('level', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('pre_test_room', css_class='col-md-3'),
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
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('exam_result_science', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('pre_comment', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/alp/pre-test/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PreTestGradingForm, self).save()
        instance.modified_by = request.user
        instance.calculate_pre_result()
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Outreach
        fields = (
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
            'pre_test_room',
            'pre_comment',
        )

    class Media:
        js = (
            'js/jquery-3.3.1.min.js',
            'js/jquery-ui-1.12.1.js',
            'js/registrations.js',
        )


class PostTestGradingForm(forms.ModelForm):

    post_test_room = forms.ChoiceField(
        label=_('Post-test room'),
        widget=forms.Select, required=True,
        choices=ROOMS
    )
    post_exam_result_arabic = forms.FloatField(
        label=_('Arabic'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=20, min_value=0,
        required=True
    )
    post_exam_language = forms.ChoiceField(
        label=_('Exam language'),
        widget=forms.Select, required=True,
        choices=EXAM_LANGUAGES
    )
    post_exam_result_language = forms.FloatField(
        label=_('Foreign Language'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=20, min_value=0,
        required=True
    )
    post_exam_result_math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=20, min_value=0,
        required=True
    )
    post_exam_result_science = forms.FloatField(
        label=_('Science'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        max_value=20, min_value=0,
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
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Post-test') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_test_room', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Post-test Grades') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('post_exam_result_arabic', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('post_exam_language', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('post_exam_result_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('post_exam_result_math', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('post_exam_result_science', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('post_comment', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
                HTML('<a class="btn btn-info cancel-button" href="/alp/post-test/" translation="' + _('Are you sure you want to cancel this registration?') + '">' + _('Back to list') + '</a>'),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PostTestGradingForm, self).save()
        instance.modified_by = request.user
        instance.calculate_post_result()
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Outreach
        fields = (
            'post_test_room',
            'post_exam_result_arabic',
            'post_exam_language',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'post_comment',
        )

    class Media:
        js = (
            # 'js/validator.js',
        )
