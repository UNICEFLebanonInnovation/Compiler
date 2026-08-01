from __future__ import unicode_literals, absolute_import, division

from decimal import Decimal

from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset
from dal import autocomplete

from student_registration.mscc.templatetags.simple_tags import get_service
from student_registration.mscc.utils import DEFAULT_PACKAGE_TYPE, validate_date
from .models import (
    Registration,
    EducationAssessment,
    EducationService,
    ServiceProgramOption,
    Packages,
    EducationRSService,
    EducationProgrammeAssessment,
    EducationProgrammeWLAssessment,
    TarlAssessment,
    YES_NO,
    Round
)
from student_registration.schools.models import (
    School,
    PartnerOrganization
)
from .utils import update_child_attendance


WL_BLN_PROGRAMME_CONFIG = {
    "BLN Level 1": {
        "english_grade": {
            "label": _("English"),
            "total": 43,
            "components": (
                ("english_letter_sound", _("Letter Sound"), 13),
                ("english_familiar_words", _("Familiar Words"), 10),
                ("english_sentence", _("Sentence"), 10),
                ("english_dictation", _("Dictation"), 10),
            ),
        },
        "french_grade": {
            "label": _("French"),
            "total": 43,
            "components": (
                ("french_letter_sound", _("Letter Sound"), 13),
                ("french_familiar_words", _("Familiar Words"), 10),
                ("french_sentence", _("Sentence"), 10),
                ("french_dictation", _("Dictation"), 10),
            ),
        },
        "arabic_grade": {
            "label": _("Arabic"),
            "total": 68,
            "components": (
                ("arabic_letter_sound", _("Letter Sound"), 28),
                ("arabic_alphabet_vowel", _("Alphabet letters with vowel"), 5),
                ("arabic_alphabet_long_vowel", _("Alphabet letters with long vowel"), 5),
                ("arabic_familiar_words", _("Familiar Words"), 10),
                ("arabic_sentence", _("Sentence"), 10),
                ("arabic_dictation", _("Dictation"), 10),
            ),
        },
        "math_grade": {
            "label": _("Math"),
            "total": 22,
            "components": (
                ("math_natural_numbers", _("Natural Numbers"), 10),
                ("math_addition_words", _("Addition"), 8),
                ("math_subtraction", _("Subtraction"), 4),
            ),
        },
    },
    "BLN Level 2": {
        "english_grade": {
            "label": _("English"),
            "total": 65,
            "components": (
                ("english_letter_sound", _("Letter Sound"), 10),
                ("english_familiar_words", _("Familiar Words"), 10),
                ("english_paragraph", _("Paragraph"), 25),
                ("english_dictation", _("Dictation"), 10),
                ("english_reading_comprehension", _("Reading Comprehension"), 10),
            ),
        },
        "french_grade": {
            "label": _("French"),
            "total": 65,
            "components": (
                ("french_letter_sound", _("Letter Sound"), 10),
                ("french_familiar_words", _("Familiar Words"), 10),
                ("french_paragraph", _("Paragraph"), 25),
                ("french_dictation", _("Dictation"), 10),
                ("french_reading_comprehension", _("Reading Comprehension"), 10),
            ),
        },
        "arabic_grade": {
            "label": _("Arabic"),
            "total": 70,
            "components": (
                ("arabic_letter_sound", _("Letter Sound"), 10),
                ("arabic_alphabet_vowel", _("Alphabet letters with vowel"), 5),
                ("arabic_alphabet_long_vowel", _("Alphabet letters with long vowel"), 5),
                ("arabic_familiar_words", _("Familiar Words"), 10),
                ("arabic_paragraph", _("Paragraph"), 20),
                ("arabic_reading_comprehension", _("Reading Comprehension"), 10),
                ("arabic_dictation", _("Dictation"), 10),
            ),
        },
        "math_grade": {
            "label": _("Math"),
            "total": 32,
            "components": (
                ("math_natural_numbers", _("Natural Numbers"), 10),
                ("math_addition_words", _("Addition"), 10),
                ("math_subtraction", _("Subtraction"), 7),
                ("math_multiplication", _("Multiplication"), 5),
            ),
        },
    },
    "BLN Level 3": {
        "english_grade": {
            "label": _("English"),
            "total": 64,
            "components": (
                ("english_letter_sound", _("Letter Sound"), 10),
                ("english_familiar_words", _("Familiar Words"), 10),
                ("english_paragraph", _("Paragraph"), 20),
                ("english_dictation", _("Dictation"), 10),
                ("english_reading_comprehension", _("Reading Comprehension"), 14),
            ),
        },
        "french_grade": {
            "label": _("French"),
            "total": 59,
            "components": (
                ("french_letter_sound", _("Letter Sound"), 10),
                ("french_familiar_words", _("Familiar Words"), 10),
                ("french_paragraph", _("Paragraph"), 15),
                ("french_dictation", _("Dictation"), 10),
                ("french_reading_comprehension", _("Reading Comprehension"), 14),
            ),
        },
        "arabic_grade": {
            "label": _("Arabic"),
            "total": 69,
            "components": (
                ("arabic_letter_sound", _("Letter Sound"), 10),
                ("arabic_alphabet_vowel", _("Alphabet letters with vowel"), 5),
                ("arabic_alphabet_long_vowel", _("Alphabet letters with long vowel"), 5),
                ("arabic_familiar_words", _("Familiar Words"), 10),
                ("arabic_paragraph", _("Paragraph"), 15),
                ("arabic_reading_comprehension", _("Reading Comprehension"), 14),
                ("arabic_dictation", _("Dictation"), 10),
            ),
        },
        "math_grade": {
            "label": _("Math"),
            "total": 32,
            "components": (
                ("math_natural_numbers", _("Natural Numbers"), 8),
                ("math_addition_words", _("Addition"), 8),
                ("math_subtraction", _("Subtraction"), 6),
                ("math_multiplication", _("Multiplication"), 6),
                ("math_division", _("Division"), 4),
            ),
        },
    },
}


def wl_bln_numeric_field(label, readonly=False):
    attrs = {'step': '0.01', 'min': '0'}
    if readonly:
        attrs['readonly'] = 'readonly'
    return forms.DecimalField(
        label=label,
        required=False,
        min_value=0,
        initial=0,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs=attrs)
    )


def wl_bln_json_safe(data):
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, dict):
        return {key: wl_bln_json_safe(value) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [wl_bln_json_safe(value) for value in data]
    return data


class DiagnosticAssessmentForm(forms.ModelForm):
    # Pre Test
    pre_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_arabic = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_arabic_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    pre_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_language = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_language_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    pre_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_math = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_math_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(DiagnosticAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_diagnostic_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_diagnostic_assessment_edit',
                                  kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('pre_attended_arabic', css_class='col-md-6'),
                    Div('pre_modality_arabic', css_class='col-md-3'),
                    Div('pre_arabic_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('pre_attended_language', css_class='col-md-6'),
                    Div('pre_modality_language', css_class='col-md-3'),
                    Div('pre_language_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('pre_attended_math', css_class='col-md-6'),
                    Div('pre_modality_math', css_class='col-md-3'),
                    Div('pre_math_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationAssessment.objects.create(registration_id=registry)
        else:
            instance = EducationAssessment.objects.get(id=instance)

        instance.pre_attended_arabic = validated_data.get('pre_attended_arabic')
        instance.pre_modality_arabic = validated_data.get('pre_modality_arabic')
        instance.pre_arabic_grade = int(validated_data.get('pre_arabic_grade'))
        instance.pre_attended_language = validated_data.get('pre_attended_language')
        instance.pre_modality_language = validated_data.get('pre_modality_language')
        instance.pre_language_grade = int(validated_data.get('pre_language_grade'))
        instance.pre_attended_math = validated_data.get('pre_attended_math')
        instance.pre_modality_math = validated_data.get('pre_modality_math')
        instance.pre_math_grade = int(validated_data.get('pre_math_grade'))
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(DiagnosticAssessmentForm, self).clean()

        pre_attended_arabic = cleaned_data.get("pre_attended_arabic")
        pre_modality_arabic = cleaned_data.get("pre_modality_arabic")
        pre_arabic_grade = cleaned_data.get("pre_arabic_grade")
        if pre_attended_arabic and pre_attended_arabic == 'Yes':
            if not pre_modality_arabic:
                self.add_error('pre_modality_arabic', 'This field is required')
            if not pre_arabic_grade:
                self.add_error('pre_arabic_grade', 'This field is required')

        pre_attended_language = cleaned_data.get("pre_attended_language")
        pre_modality_language = cleaned_data.get("pre_modality_language")
        pre_language_grade = cleaned_data.get("pre_language_grade")
        if pre_attended_language and pre_attended_language == 'Yes':
            if not pre_modality_language:
                self.add_error('pre_modality_language', 'This field is required')
            if not pre_language_grade:
                self.add_error('pre_language_grade', 'This field is required')

        pre_attended_math = cleaned_data.get("pre_attended_math")
        pre_modality_math = cleaned_data.get("pre_modality_math")
        pre_math_grade = cleaned_data.get("pre_math_grade")
        if pre_attended_math and pre_attended_math == 'Yes':
            if not pre_modality_math:
                self.add_error('pre_modality_math', 'This field is required')
            if not pre_math_grade:
                self.add_error('pre_math_grade', 'This field is required')

    class Meta:
        model = EducationAssessment
        fields = (
            'pre_attended_arabic',
            'pre_modality_arabic',
            'pre_arabic_grade',
            'pre_attended_language',
            'pre_modality_language',
            'pre_language_grade',
            'pre_attended_math',
            'pre_modality_math',
            'pre_math_grade',
        )


class EducationAssessmentForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=True,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    # Post test
    post_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_arabic = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_arabic_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    post_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_language = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_language_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    post_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_math = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_math_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(EducationAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_education_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_education_assessment_edit',
                                  kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('participation', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('barriers', css_class='col-md-8'),
                    Div('barriers_other', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('post_test_done', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('school_year_completed', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('post_attended_arabic', css_class='col-md-6'),
                    Div('post_modality_arabic', css_class='col-md-3 grd-arabic'),
                    Div('post_arabic_grade', css_class='col-md-2 grd-arabic'),
                    css_class='row grades card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('post_attended_language', css_class='col-md-6'),
                    Div('post_modality_language', css_class='col-md-3'),
                    Div('post_language_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('post_attended_math', css_class='col-md-6'),
                    Div('post_modality_math', css_class='col-md-3'),
                    Div('post_math_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationAssessment.objects.create(registration_id=registry)
        else:
            instance = EducationAssessment.objects.get(id=instance)

        instance.participation = validated_data.get('participation')
        instance.barriers = validated_data.get('barriers')
        instance.barriers_other = validated_data.get('barriers_other')
        instance.post_test_done = validated_data.get('post_test_done')
        instance.school_year_completed = validated_data.get('school_year_completed')
        instance.post_attended_arabic = validated_data.get('post_attended_arabic')
        instance.post_modality_arabic = validated_data.get('post_modality_arabic')
        instance.post_arabic_grade = int(validated_data.get('post_arabic_grade'))
        instance.post_attended_language = validated_data.get('post_attended_language')
        instance.post_modality_language = validated_data.get('post_modality_language')
        instance.post_language_grade = int(validated_data.get('post_language_grade'))
        instance.post_attended_math = validated_data.get('post_attended_math')
        instance.post_modality_math = validated_data.get('post_modality_math')
        instance.post_math_grade = int(validated_data.get('post_math_grade'))
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationAssessmentForm, self).clean()
        barriers = cleaned_data.get("barriers")
        barriers_other = cleaned_data.get("barriers_other")
        if barriers and barriers == 'Other' and not barriers_other:
            self.add_error('barriers_other', 'This field is required')

        post_test_done = cleaned_data.get("post_test_done")
        if post_test_done and post_test_done == 'Yes':

            post_attended_arabic = cleaned_data.get("post_attended_arabic")
            post_modality_arabic = cleaned_data.get("post_modality_arabic")
            post_arabic_grade = cleaned_data.get("post_arabic_grade")
            if post_attended_arabic and post_attended_arabic == 'Yes':
                if not post_modality_arabic:
                    self.add_error('post_modality_arabic', 'This field is required')
                if not post_arabic_grade:
                    self.add_error('post_arabic_grade', 'This field is required')

            post_attended_language = cleaned_data.get("post_attended_language")
            post_modality_language = cleaned_data.get("post_modality_language")
            post_language_grade = cleaned_data.get("post_language_grade")
            if post_attended_language and post_attended_language == 'Yes':
                if not post_modality_language:
                    self.add_error('post_modality_language', 'This field is required')
                if not post_language_grade:
                    self.add_error('post_language_grade', 'This field is required')

            post_attended_math = cleaned_data.get("post_attended_math")
            post_modality_math = cleaned_data.get("post_modality_math")
            post_math_grade = cleaned_data.get("post_math_grade")
            if post_attended_math and post_attended_math == 'Yes':
                if not post_modality_math:
                    self.add_error('post_modality_math', 'This field is required')
                if not post_math_grade:
                    self.add_error('post_math_grade', 'This field is required')

    class Meta:
        model = EducationAssessment
        fields = (
            'participation',
            'barriers',
            'barriers_other',
            'post_test_done',
            'school_year_completed',
            'post_attended_arabic',
            'post_modality_arabic',
            'post_arabic_grade',
            'post_attended_language',
            'post_modality_language',
            'post_language_grade',
            'post_attended_math',
            'post_modality_math',
            'post_math_grade'
        )


class EducationServiceForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_("Child\'s educational level when registering for the round"),
        widget=forms.Select, required=True,
        choices=EducationService.EDUCATION_STATUS,
    )
    dropout_date = forms.DateField(
        label=_("Please Specify dropout date from school"),
        required=False
    )
    round = forms.ModelChoiceField(
        queryset=Round.objects.filter(current_year=True),
        widget=forms.Select,
        label=_('Cycle'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    education_program = forms.ChoiceField(
        label=_("Core Package Program"),
        widget=forms.Select, required=True,
        choices=EducationService.EDUCATION_PROGRAM,
    )
    ppl_sector = forms.ChoiceField(
        label=_('PPL Sector'),
        widget=forms.Select,
        required=False,
        choices=EducationService.PPL_SECTOR,
    )
    catch_up_registered = forms.ChoiceField(
        label=_("Is the child registered in catch-up program"),
        widget=forms.Select, required=False,
        choices=EducationService.CATCH_UP_REGISTERED,
    )
    registration_date = forms.DateField(
        label=_("Date of registration in the round"),
        required=True
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)
        package_type = kwargs.pop('package_type', None)

        if not package_type:
            package_type = (
                Registration.objects.filter(id=registry)
                .values_list('type', flat=True)
                .first()
            ) or DEFAULT_PACKAGE_TYPE

        super(EducationServiceForm, self).__init__(*args, **kwargs)

        self.fields['registration_id'].initial = registry

        programme_labels = dict(EducationService.EDUCATION_PROGRAM)
        service_programs = list(ServiceProgramOption.objects.filter(is_tarl='Yes'))

        if service_programs:
            service_names = {option.service_name for option in service_programs}
            available_services = {
                service_name: get_service(registry, service_name)
                for service_name in service_names
            }
            available_service_names = {
                name for name, service in available_services.items() if service
            }

            if registry and not available_service_names:
                registry_obj = Registration.objects.select_related('child').filter(id=registry).first()
                if registry_obj:
                    available_service_names = set(
                        Packages.objects.filter(
                            type=registry_obj.type,
                            age=registry_obj.child_age
                        ).values_list('name', flat=True)
                    )

            choices = []
            for option in service_programs:
                if available_service_names and option.service_name not in available_service_names:
                    continue

                label = programme_labels.get(option.program_code, _(option.program_code))
                choices.append((option.program_code, label))

            self.fields['education_program'].choices = choices

        choices_education_status = list()
        if package_type == 'Walk-in':
            choices_education_status.append(('', _('----------')))
            choices_education_status.append(('Currently registered in Formal Education school',
                                             _('Currently registered in Formal Education school')))
            choices_education_status.append(('Currently registered in Formal Education school but not attending',
                                             _('Currently registered in Formal Education school but not attending')))
            self.fields['education_status'].choices = choices_education_status

        display_edu_section = ''
        if package_type != 'Core-Package':
            display_edu_section = ' d-none'
            self.fields['education_program'].choices = []
            self.fields['education_program'].initial = ''
            self.fields['education_program'].required = False
            self.fields['class_section'].required = False
            self.fields['registration_date'].required = False


        if registry:
            child_id = Registration.objects.filter(id=registry).values_list('child_id', flat=True).first()

            if instance:
                try:
                    education_service = EducationService.objects.get(pk=instance)
                    current_round_id = education_service.round_id
                except EducationService.DoesNotExist:
                    current_round_id = None
            else:
                current_round_id = None

            # Get rounds already registered under non-TLS registrations, excluding the current.
            registered_education_services = EducationService.objects.filter(
                registration__child_id=child_id,
                registration__deleted=False
            ).exclude(registration__type='TLS')
            if current_round_id:
                registered_education_services = registered_education_services.exclude(
                    round_id=current_round_id
                )
            rounds_registered = registered_education_services.values_list('round_id', flat=True)

            # Remove any None values
            rounds_registered = [r for r in rounds_registered if r is not None]

            #  rounds for current_year, excluding already registered and including current round.
            if current_round_id:
                available_rounds = Round.objects.filter(
                    Q(current_year=True) & (
                        ~Q(id__in=rounds_registered) | Q(id=current_round_id)
                    )
                )
            else:
                available_rounds = Round.objects.filter(current_year=True).exclude(id__in=rounds_registered)

            self.fields['round'].queryset = available_rounds


        form_action = reverse('mscc:service_education_add', kwargs={'registry': registry, 'package_type': package_type})
        if instance:
            form_action = reverse('mscc:service_education_edit',
                                  kwargs={'registry': registry, 'package_type': package_type, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('education_status', css_class='col-md-6'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('dropout_date', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('round', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('education_program', css_class='col-md-3'),
                    Div('ppl_sector', css_class='col-md-3'),
                    Div('catch_up_registered', css_class='col-md-3'),
                    css_class='row card-body' + display_edu_section
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('class_section', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('registration_date', css_class='col-md-3'),
                    css_class='row card-body'+display_edu_section
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                HTML(
                    '<a type="reset" name="cancel" class="btn btn-inverse btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning" id="cancel-id-cancel" href="/mscc/child-registration-cancel/{}/">Cancel</a>'.format(
                        registry)
                ),

            ),
        )

    def save(self, request=None, instance=None, registry=None, package_type=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = EducationService.objects.create(registration_id=registry)
        else:
            instance = EducationService.objects.get(id=instance)
            old_class_section = instance.class_section
            new_class_section = validated_data.get('class_section')

            if str(old_class_section) != str(new_class_section):
                update_child_attendance(instance.registration.id, instance.education_program, old_class_section,
                                        new_class_section)

        instance.education_status = validated_data.get('education_status')
        dropout_date_str = validated_data.get('dropout_date')
        if dropout_date_str:
            try:
                instance.dropout_date = validate_date(dropout_date_str)
            except ValidationError as e:
                raise ValidationError("Dropout date error: {}".format(e))
        instance.education_program = validated_data.get('education_program')
        if instance.education_program == 'PPL':
            instance.ppl_sector = validated_data.get('ppl_sector')
        else:
            instance.ppl_sector = None
        instance.class_section = validated_data.get('class_section')
        instance.round_id = validated_data.get('round')

        registration_date_str = validated_data.get('registration_date')
        if registration_date_str:
            try:
                instance.registration_date = validate_date(registration_date_str)
            except ValidationError as e:
                raise ValidationError("Registration date error: {}".format(e))

        instance.save()

        registry = instance.registration
        registry.round_id = instance.round_id
        registry.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):

        cleaned_data = super(EducationServiceForm, self).clean()

        dropout_date_str = cleaned_data.get("dropout_date")
        if dropout_date_str:
            try:
                validate_date(dropout_date_str)
            except ValidationError as e:
                self.add_error("dropout_date", str(e))

        registration_date_str = cleaned_data.get("registration_date")
        if registration_date_str:
            try:
                validate_date(registration_date_str)
            except ValidationError as e:
                self.add_error("registration_date", str(e))

        education_status = cleaned_data.get("education_status")
        dropout_date = cleaned_data.get("dropout_date")
        education_program = cleaned_data.get("education_program")
        ppl_sector = cleaned_data.get("ppl_sector")

        if education_status and education_status == 'Currently registered in Formal Education school but not attending'\
            and not dropout_date:
            self.add_error('dropout_date', 'This field is required')

        if education_program != 'PPL':
            cleaned_data['ppl_sector'] = None
        elif not ppl_sector:
            self.add_error('ppl_sector', _('This field is required'))

        return cleaned_data

        # instance = self.instance

        # if not instance.pk:
        #     registration_id = cleaned_data.get("registration_id")
        #     round_id = cleaned_data.get("round").id
        #
        #     registration = Registration.objects.get(id=registration_id)
        #     child = registration.child
        #
        #     # Count the number of registrations for the same child and round
        #     count = Registration.objects.filter(
        #         child=child,
        #         round__id=round_id
        #     ).exclude(id=registration_id).count()
        #
        #     last_registration = Registration.objects.filter(
        #         child=child,
        #         round__id=round_id
        #     ).exclude(id=registration_id).values(
        #         'center__name'
        #     ).order_by('-id').first()
        #
        #     if count > 0:
        #         center_name = last_registration['center__name']
        #         self.add_error('round', 'This child is already registered in the Center: ' + center_name)

    class Meta:
        model = EducationService
        fields = (
            'registration_id',
            'education_status',
            'dropout_date',
            'round',
            'education_program',
            'ppl_sector',
            'class_section',
            'registration_date',
        )


class EducationRSServiceForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_bma=True).order_by('name'),
        widget=forms.Select,
        empty_label='-------',
        label=_('Name of public School'),
        required=True,
        to_field_name='id',
    )
    shift = forms.ChoiceField(
        label=_("First or Second shift schools"),
        widget=forms.Select,
        required=False,
        choices=EducationRSService.SCHOOL_SHIFTS
    )
    support_needed = forms.MultipleChoiceField(
        label=_('Needed Support?'),
        choices=EducationRSService.SUPPORT_NEEDED,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        pk = kwargs.pop('pk', None)

        super(EducationRSServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_education_rs_add', kwargs={'registry': registry})
        if pk:
            form_action = reverse('mscc:service_education_rs_edit',
                                  kwargs={'registry': registry, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('school', css_class='col-md-6'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('shift', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('support_needed', css_class='col-md-3 multiple-choice'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),

            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
            ),
        )

    def save(self, request=None, instance=None, registry=None):
        from .utils import update_service

        validated_data = request.POST

        if not instance:
            instance = EducationRSService.objects.create(registration_id=registry)
        else:
            instance = EducationRSService.objects.get(id=instance)

        instance.school_id = validated_data.get('school')

        instance.shift = validated_data.get('shift')
        instance.support_needed = validated_data.getlist('support_needed')
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='RS', service_id=instance.id)

        return instance

    class Meta:
        model = EducationRSService
        fields = (
            'school',
            'shift',
            'support_needed',
        )


class EducationGradingForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=False,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    arabic_grade = forms.DecimalField(
        label=_('Arabic Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    language_grade = forms.DecimalField(
        label=_('Foreign Language Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    english_grade = forms.DecimalField(
        label=_('English Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    french_grade = forms.DecimalField(
        label=_('French Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    math_grade = forms.DecimalField(
        label=_('Mathematics Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    science_grade = forms.DecimalField(
        label=_('Sciences Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    biology_grade = forms.DecimalField(
        label=_('Biology Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    chemistry_grade = forms.DecimalField(
        label=_('Chemistry Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    physics_grade = forms.DecimalField(
        label=_('Physics Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    social_emotional_grade = forms.DecimalField(
        label=_('Social-Emotional Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    artistic_grade = forms.DecimalField(
        label=_('Artistic Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    psychomotor_grade = forms.DecimalField(
        label=_('Psychomotor Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', None)
        instance = kwargs.pop('instance', None)

        super(EducationGradingForm, self).__init__(*args, **kwargs)

        center = getattr(getattr(self.request, 'user', None), 'center', None)
        provide_french_language = getattr(center, 'provide_french_language', None) == "Yes"
        self.provide_french_language = provide_french_language

        form_action = reverse('mscc:service_education_grading_add',
                              kwargs={'registry': registry, 'programme_type': programme_type})
        if instance:
            form_action = reverse('mscc:service_education_grading_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post,
                                          'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type

        if programme_type in ["BLN Level 1", "BLN Level 2", "BLN Level 3"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 20)
            field_init(self.fields['english_grade'], 'English Language Development', 30)
            field_init(self.fields['french_grade'], 'French Language Development', 30)
            if provide_french_language:
                self.fields['english_grade'].hidden_widget()
                self.fields['english_grade'].required = False
            else:
                self.fields['french_grade'].hidden_widget()
                self.fields['french_grade'].required = False
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['social_emotional_grade'].required = False
            self.fields['artistic_grade'].hidden_widget()
            self.fields['artistic_grade'].required = False
            self.fields['language_grade'].hidden_widget()
            self.fields['language_grade'].required = False
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()

            if pre_post == "pre":
                field_init(self.fields['math_grade'], 'Mathematics', 25)
            if pre_post == "post":
                field_init(self.fields['math_grade'], 'Mathematics', 20)
            if pre_post == "mid":
                field_init(self.fields['math_grade'], 'Mathematics', 20)
                self.fields['math_grade'].required = True
                self.fields['arabic_grade'].required = False
                self.fields['english_grade'].required = False
                self.fields['french_grade'].required = False
                self.fields['arabic_grade'].hidden_widget()
                if provide_french_language:
                    self.fields['french_grade'].hidden_widget()
                else:
                    self.fields['english_grade'].hidden_widget()

        if programme_type == "ABLN Level 1":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 46)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 24)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 10)
            self.fields['language_grade'].hidden_widget()
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "ABLN Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development ', 56)
            field_init(self.fields['math_grade'], 'Mathematics', 36)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 24)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 10)
            self.fields['language_grade'].hidden_widget()
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "CBECE Level 1":
            field_init(self.fields['language_grade'], 'Language Development', 48)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 24)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 18)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 14)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 20)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 10)
            self.fields['arabic_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "CBECE Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 66)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 66)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 48)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 38)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 40)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 40)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 16)
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "CBECE Level 3":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 74)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 74)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 50)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 38)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 40)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 42)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 16)
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['biology_grade'], 'Biology', 20)
            field_init(self.fields['chemistry_grade'], 'Chemistry', 20)
            field_init(self.fields['physics_grade'], 'Physics', 20)
            self.fields['science_grade'].hidden_widget()
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['artistic_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type in ["Summer RS Grade 7", "Summer RS Grade 8", "Summer RS Grade 9", "YFS Level 1 - Summer RS Grade 9", "YFS Level 2 - Summer RS Grade 9"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['biology_grade'], 'Biology', 20)
            field_init(self.fields['chemistry_grade'], 'Chemistry', 20)
            field_init(self.fields['physics_grade'], 'Physics', 20)
            self.fields['science_grade'].hidden_widget()
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['artistic_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['artistic_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type in ["Summer RS Grade 1", "Summer RS Grade 2", "Summer RS Grade 3", "Summer RS Grade 4", "Summer RS Grade 5", "Summer RS Grade 6"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['artistic_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        display_post_fields_css = 'd-none'
        display_pre_fields_css = ''
        badge_css = 'badge-form'
        grade_field_css = ''
        ctr = 0
        if pre_post == 'post':
            ctr = 4
            badge_css = 'badge-form-2'
            grade_field_css = 'grade-field'
            display_post_fields_css = ''
            display_pre_fields_css = ' d-none'
            self.fields['participation'].required = True
            self.fields['barriers'].required = True
            self.fields['post_test_done'].required = True
            self.fields['school_year_completed'].required = True

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["BLN Level 1", "BLN Level 2", "BLN Level 3"]:
            language_field = 'french_grade' if provide_french_language else 'english_grade'
            first_grade_row_css = ' d-none' if pre_post == "mid" else ''
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div(language_field, css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css + first_grade_row_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )
        if programme_type in ["ABLN Level 1", "ABLN Level 2"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('social_emotional_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('artistic_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["CBECE Level 1"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('psychomotor_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('social_emotional_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('artistic_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["CBECE Level 2", "CBECE Level 3"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('psychomotor_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('social_emotional_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(7 + ctr) + '</span>'),
                        Div('artistic_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )
        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('biology_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('chemistry_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('physics_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["Summer RS Grade 7", "Summer RS Grade 8", "Summer RS Grade 9", "YFS Level 1 - Summer RS Grade 9", "YFS Level 2 - Summer RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('biology_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('chemistry_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('physics_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["Summer RS Grade 1", "Summer RS Grade 2", "Summer RS Grade 3", "Summer RS Grade 4", "Summer RS Grade 5", "Summer RS Grade 6"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):

        if not instance:
            instance = EducationProgrammeAssessment.objects.create(registration_id=registry)
            instance.pre_test = request.POST
        else:
            instance = EducationProgrammeAssessment.objects.get(id=instance)
            if pre_post == "pre":
                instance.pre_test = request.POST
            if pre_post == "mid":
                instance.mid_test = request.POST
            if pre_post == "post":
                instance.post_test = request.POST

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):

        cleaned_data = super(EducationGradingForm, self).clean()
        programme_type = cleaned_data.get("programme_type")
        pre_post = cleaned_data.get("pre_post")

        # Validation thresholds for each programme type
        thresholds = {
            "BLN Level 1 - BLN Level 2 - BLN Level 3": {
                "arabic_grade": 20,
                "english_grade": 30,
                "french_grade": 30,
                "math_grade": 22,
            },
            "ABLN Level 1": {
                "arabic_grade": 46,
                "math_grade": 20,
                "social_emotional_grade": 24,
                "artistic_grade": 10,
            },
            "ABLN Level 2": {
                "arabic_grade": 56,
                "math_grade": 36,
                "social_emotional_grade": 24,
                "artistic_grade": 10,
            },
            "CBECE Level 1": {
                "language_grade": 48,
                "math_grade": 24,
                "science_grade": 18,
                "social_emotional_grade": 14,
                "psychomotor_grade": 20,
                "artistic_grade": 10,
            },
            "CBECE Level 2": {
                "arabic_grade": 66,
                "language_grade": 66,
                "math_grade": 48,
                "science_grade": 38,
                "social_emotional_grade": 40,
                "psychomotor_grade": 40,
                "artistic_grade": 16,
            },
            "CBECE Level 3": {
                "arabic_grade": 74,
                "language_grade": 74,
                "math_grade": 50,
                "science_grade": 38,
                "social_emotional_grade": 40,
                "psychomotor_grade": 42,
                "artistic_grade": 16,
            },
            "YFS Level 1 - RS Grade 9": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "YFS Level 2 - RS Grade 9": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "RS Grade 1": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 2": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 3": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 4": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 5": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 6": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 7": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "RS Grade 8": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "RS Grade 9": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "Summer RS Grade 1": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 2": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 3": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 4": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 5": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 6": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "Summer RS Grade 7": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "Summer RS Grade 8": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
            "Summer RS Grade 9": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "biology_grade": 20,
                "chemistry_grade": 20,
                "physics_grade": 20,
            },
        }

        if programme_type in thresholds:
            programme_thresholds = thresholds[programme_type].copy()

            if programme_type == "BLN Level 1 - BLN Level 2 - BLN Level 3":
                if pre_post == "pre":
                    programme_thresholds["math_grade"] = 25
                elif pre_post in ["post", "mid"]:
                    programme_thresholds["math_grade"] = 20

            for field, max_value in programme_thresholds.items():
                field_value = cleaned_data.get(field)
                if field_value is not None and field_value > max_value:
                    self.add_error(field, "This value is greater than " + str(max_value))

        return cleaned_data

    class Meta:
        model = EducationProgrammeAssessment
        fields = (
            'programme_type',
        )


class WLBLNAssessmentForm(forms.ModelForm):
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    english_letter_sound = wl_bln_numeric_field(_('English - Letter Sound'))
    english_familiar_words = wl_bln_numeric_field(_('English - Familiar Words'))
    english_sentence = wl_bln_numeric_field(_('English - Sentence'))
    english_paragraph = wl_bln_numeric_field(_('English - Paragraph'))
    english_dictation = wl_bln_numeric_field(_('English - Dictation'))
    english_reading_comprehension = wl_bln_numeric_field(_('English - Reading Comprehension'))
    english_grade = wl_bln_numeric_field(_('English Total'), readonly=True)

    french_letter_sound = wl_bln_numeric_field(_('French - Letter Sound'))
    french_familiar_words = wl_bln_numeric_field(_('French - Familiar Words'))
    french_sentence = wl_bln_numeric_field(_('French - Sentence'))
    french_paragraph = wl_bln_numeric_field(_('French - Paragraph'))
    french_dictation = wl_bln_numeric_field(_('French - Dictation'))
    french_reading_comprehension = wl_bln_numeric_field(_('French - Reading Comprehension'))
    french_grade = wl_bln_numeric_field(_('French Total'), readonly=True)

    arabic_letter_sound = wl_bln_numeric_field(_('Arabic - Letter Sound'))
    arabic_alphabet_vowel = wl_bln_numeric_field(_('Arabic - Alphabet letters with vowel'))
    arabic_alphabet_long_vowel = wl_bln_numeric_field(_('Arabic - Alphabet letters with long vowel'))
    arabic_familiar_words = wl_bln_numeric_field(_('Arabic - Familiar Words'))
    arabic_sentence = wl_bln_numeric_field(_('Arabic - Sentence'))
    arabic_paragraph = wl_bln_numeric_field(_('Arabic - Paragraph'))
    arabic_reading_comprehension = wl_bln_numeric_field(_('Arabic - Reading Comprehension'))
    arabic_dictation = wl_bln_numeric_field(_('Arabic - Dictation'))
    arabic_grade = wl_bln_numeric_field(_('Arabic Total'), readonly=True)

    math_natural_numbers = wl_bln_numeric_field(_('Math - Natural Numbers'))
    math_addition_words = wl_bln_numeric_field(_('Math - Addition'))
    math_subtraction = wl_bln_numeric_field(_('Math - Subtraction'))
    math_multiplication = wl_bln_numeric_field(_('Math - Multiplication'))
    math_division = wl_bln_numeric_field(_('Math - Division'))
    math_grade = wl_bln_numeric_field(_('Math Total'), readonly=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', None) or 'pre'
        instance = kwargs.pop('instance', None)

        super(WLBLNAssessmentForm, self).__init__(*args, **kwargs)

        self.pre_post = pre_post
        self.programme_type = programme_type
        self.programme_config = WL_BLN_PROGRAMME_CONFIG.get(programme_type, {})

        center = getattr(getattr(self.request, 'user', None), 'center', None)
        provide_french_language = getattr(center, 'provide_french_language', None)
        if provide_french_language == "Yes":
            self.programme_config = {
                field_name: config
                for field_name, config in self.programme_config.items()
                if not field_name.startswith('english_')
            }
        else:
            self.programme_config = {
                field_name: config
                for field_name, config in self.programme_config.items()
                if not field_name.startswith('french_')
            }

        form_action = reverse('mscc:wl_bln_assessment_add',
                              kwargs={'registry': registry, 'programme_type': programme_type})
        if instance:
            form_action = reverse('mscc:wl_bln_assessment_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type,
                                          'pre_post': pre_post, 'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type

        active_fields = {'programme_type'}
        total_labels = {}

        for total_field, subject_config in self.programme_config.items():
            active_fields.add(total_field)
            total_labels[total_field] = self.fields[total_field].label
            self.fields[total_field].label = ''
            self.fields[total_field].widget.attrs.update({
                'data-wl-bln-total-field': total_field,
                'readonly': 'readonly',
            })
            for component_name, _label, max_score in subject_config['components']:
                active_fields.add(component_name)
                self.fields[component_name].label = mark_safe(
                    '{0} / <strong class="text-primary">{1}</strong>'.format(
                        self.fields[component_name].label,
                        max_score,
                    )
                )
                self.fields[component_name].widget.attrs.update({
                    'data-wl-bln-component': '1',
                    'data-wl-bln-total-target': total_field,
                    'step': '0.01',
                    'min': '0',
                })

        for field_name, field in self.fields.items():
            if field_name not in active_fields:
                field.widget = forms.HiddenInput()
                field.required = False

        self._set_initial_totals()

        score_section_css = 'wl-bln-score-field'

        layout_items = []

        for index, (total_field, subject_config) in enumerate(self.programme_config.items(), start=1):
            layout_items.append(
                HTML(
                    '<div class="card-body {0}">'
                    '<h5 class="mb-3 d-flex align-items-center">'
                    '<span class="badge-form badge-pill mr-2">{1}</span>'
                    '{2} / {3}'
                    '</h5>'
                    '</div>'.format(
                        score_section_css,
                        index,
                        subject_config['label'],
                        subject_config['total'],
                    )
                )
            )
            components = list(subject_config['components'])
            for start in range(0, len(components), 2):
                row_fields = []
                for component_name, _component_label, max_score in components[start:start + 2]:
                    row_fields.append(
                        Div(
                            Field(component_name, placeholder='0'),
                            css_class='col-md-5'
                        )
                    )
                layout_items.append(
                    Div(
                        *row_fields,
                        css_class='row card-body {}'.format(score_section_css)
                    )
                )
            total_value = self.data.get(total_field) if self.is_bound else self.fields[total_field].initial or 0
            layout_items.append(
                Div(
                    Div(
                        HTML(
                            '<label class="form-label font-weight-bold mb-0">{0}</label>'.format(
                                total_labels[total_field],
                            )
                        ),
                        css_class='col-md-3 d-flex align-items-center'
                    ),
                    Div(
                        HTML(
                            '<input type="number" name="{0}" value="{1}" class="numberinput form-control" '
                            'id="id_{0}" readonly="readonly" step="0.01" min="0" data-wl-bln-total-field="{0}">'.format(
                                total_field,
                                total_value,
                            )
                        ),
                        css_class='col-md-2'
                    ),
                    css_class='row card-body {} align-items-center'.format(score_section_css)
                )
            )

        layout_items.append(
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
            )
        )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(Div(*layout_items, css_id='step-1'))

    def _score_source(self):
        if self.is_bound:
            return self.data
        if self.initial:
            return self.initial
        return {}

    def _set_initial_totals(self):
        source = self._score_source()
        for total_field, subject_config in self.programme_config.items():
            total = Decimal('0')
            for component_name, _label, _max_score in subject_config['components']:
                try:
                    total += Decimal(str(source.get(component_name) or 0))
                except (TypeError, ValueError):
                    total += Decimal('0')
            self.fields[total_field].initial = total

    def clean(self):
        cleaned_data = super(WLBLNAssessmentForm, self).clean()
        programme_type = cleaned_data.get('programme_type') or self.programme_type
        programme_config = self.programme_config or WL_BLN_PROGRAMME_CONFIG.get(programme_type, {})


        for total_field, subject_config in programme_config.items():
            total = Decimal('0')
            for component_name, _component_label, max_score in subject_config['components']:
                value = cleaned_data.get(component_name)
                if value in (None, ''):
                    self.add_error(component_name, 'This field is required')
                    value = Decimal('0')
                if value is not None and value not in ('',):
                    if value > max_score:
                        self.add_error(component_name, 'Max value is {0}'.format(max_score))
                    total += value or Decimal('0')
                cleaned_data[component_name] = value or Decimal('0')
            cleaned_data[total_field] = total

        return cleaned_data

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):
        cleaned_data = wl_bln_json_safe(self.cleaned_data.copy())
        if not instance:
            instance = EducationProgrammeWLAssessment.objects.create(registration_id=registry)
        else:
            instance = EducationProgrammeWLAssessment.objects.get(id=instance)

        if pre_post == 'post':
            instance.post_test = cleaned_data
        else:
            instance.pre_test = cleaned_data

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance

    class Meta:
        model = EducationProgrammeWLAssessment
        fields = ('programme_type',)


class TarlGradingForm(forms.ModelForm):
    WORD_PROBLEM_CHOICES = (
        ('', '---'),
        ('1', '1'),
        ('0', '0'),
    )
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    test_taken = forms.ChoiceField(
        label=_('Test Taken'),
        widget=forms.Select,
        choices=YES_NO,
        required=True,
    )
    arabic_level_reached = forms.ChoiceField(
        label=_('Arabic Level Reached / المستوى الذي وصل إليه المتعلم/ة'),
        widget=forms.Select,
        choices=TarlAssessment.ARABIC_LEVELS,
        required=False,
    )
    french_level_reached = forms.ChoiceField(
        label=_('French Level Reached / المستوى الذي وصل إليه المتعلم/ة'),
        widget=forms.Select,
        choices=TarlAssessment.FRENCH_LEVELS,
        required=False,
    )
    math_level_reached = forms.ChoiceField(
        label=_('Math Level Reached / المستوى الذي وصل إليه المتعلم/ة'),
        widget=forms.Select,
        choices=TarlAssessment.MATH_LEVELS,
        required=False,
    )
    word_problem_q1 = forms.ChoiceField(
        label=_('Word Problem Q1'),
        widget=forms.Select,
        choices=WORD_PROBLEM_CHOICES,
        required=False,
    )
    word_problem_q2=forms.ChoiceField(
        label=_('Word Problem Q2'),
        widget=forms.Select,
        choices=WORD_PROBLEM_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', 'pre')
        instance = kwargs.pop('instance', None)

        super(TarlGradingForm, self).__init__(*args, **kwargs)

        center = getattr(getattr(self.request, 'user', None), 'center', None)
        provide_french_language = getattr(center, 'provide_french_language', None) == "Yes"
        self.require_french_language = provide_french_language

        if not provide_french_language:
            self.fields.pop('french_level_reached', None)

        form_action = reverse('mscc:service_tarl_grading_add',
                              kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post})
        if instance:
            form_action = reverse('mscc:service_tarl_grading_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post,
                                          'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        tarl_blocks = [
            Div(
                HTML('<span class="badge-form badge-pill">1</span>'),
                Div('test_taken', css_class='col-md-4'),
                css_class='row card-body '
            ),
            Div(
                HTML('<span class="badge-form badge-pill">2</span>'),
                Div('arabic_level_reached', css_class='col-md-4 tarl-dependent'),
                css_class='row card-body'
            ),
        ]

        if provide_french_language:
            tarl_blocks.append(
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('french_level_reached', css_class='col-md-4 tarl-dependent'),
                    css_class='row card-body'
                )
            )

        tarl_blocks.append(
            Div(
                HTML('<span class="badge-form badge-pill">4</span>'),
                Div('math_level_reached', css_class='col-md-4 tarl-dependent'),
                Div('word_problem_q1', css_class='col-md-3 tarl-dependent tarl-word-problem'),
                Div('word_problem_q2', css_class='col-md-3 tarl-dependent tarl-word-problem'),
                css_class='row card-body'
            )
        )
        tarl_blocks.append(
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
            )
        )

        self.helper.layout = Layout(
            Div(
                *tarl_blocks,
                css_id='step-1'
            )
        )

    def clean(self):
        cleaned_data = super(TarlGradingForm, self).clean()
        test_taken = cleaned_data.get('test_taken')
        required_fields = [
            'arabic_level_reached',
            'math_level_reached',
        ]
        if self.require_french_language:
            required_fields.append('french_level_reached')
        if test_taken == 'Yes':
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('This field is required.'))

            math_level_reached = cleaned_data.get('math_level_reached')
            if math_level_reached in ['Subtraction', 'Division']:
                if not cleaned_data.get('word_problem_q1'):
                    self.add_error('word_problem_q1', _('This field is required.'))
                if not cleaned_data.get('word_problem_q2'):
                    self.add_error('word_problem_q2', _('This field is required.'))

        return cleaned_data

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):
        if not instance:
            instance = TarlAssessment.objects.create(registration_id=registry)
            instance.pre_test = request.POST
        else:
            instance = TarlAssessment.objects.get(id=instance)
            if pre_post == "pre":
                instance.pre_test = request.POST
            if pre_post == "mid":
                instance.mid_test = request.POST
            if pre_post == "post":
                instance.post_test = request.POST

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance


    class Meta:
        model = TarlAssessment
        fields = (
            'programme_type',
        )


class YouthScoringForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=False,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )

    arabic_grade = forms.IntegerField(
        label=_('Arabic'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    language_grade = forms.IntegerField(
        label=_('Foreign Language'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    math_grade = forms.IntegerField(
        label=_('Mathematics'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    life_skills = forms.IntegerField(
        label=_('Life Skills'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    english_development = forms.IntegerField(
        label=_('English Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    financial_development = forms.IntegerField(
        label=_('Financial Literacy Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    it_development = forms.IntegerField(
        label=_('IT Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', 'pre')
        instance = kwargs.pop('instance', None)

        super(YouthScoringForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_scoring_add',
                              kwargs={'registry': registry, 'programme_type': programme_type})
        if instance:
            form_action = reverse('mscc:service_youth_scoring_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post,
                                          'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type
            if self.data:
                self.data = self.data.copy()
                self.data['programme_type'] = programme_type

        if programme_type == "YBLN Level 1":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 12)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 15)
            field_init(self.fields['life_skills'], 'Life Skills Development', 12)
            self.fields['english_development'].hidden_widget()
            self.fields['financial_development'].hidden_widget()
            self.fields['it_development'].hidden_widget()

        if programme_type == "YBLN Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 12)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 12)
            field_init(self.fields['math_grade'], 'Mathematics', 21)
            field_init(self.fields['life_skills'], 'Life Skills Development', 12)
            self.fields['english_development'].hidden_widget()
            self.fields['financial_development'].hidden_widget()
            self.fields['it_development'].hidden_widget()

        if programme_type in ["YFS Level 1", "YFS Level 2", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            field_init(self.fields['english_development'], 'English Development', 100)
            field_init(self.fields['financial_development'], 'Financial Literacy Development', 100)
            field_init(self.fields['it_development'], 'IT Development', 100)
            self.fields['arabic_grade'].hidden_widget()
            self.fields['language_grade'].hidden_widget()
            self.fields['math_grade'].hidden_widget()
            self.fields['life_skills'].hidden_widget()

        display_post_fields_css = 'd-none'
        display_pre_fields_css = ''
        badge_css = 'badge-form'
        grade_field_css = ''
        ctr = 0
        if pre_post == 'post':
            ctr = 4
            badge_css = 'badge-form-2'
            grade_field_css = 'grade-field'
            display_post_fields_css = ''
            display_pre_fields_css = ' d-none'
            self.fields['participation'].required = True
            self.fields['barriers'].required = True
            self.fields['post_test_done'].required = True
            self.fields['school_year_completed'].required = True

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["YBLN Level 1", "YBLN Level 2"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('life_skills', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["YFS Level 1", "YFS Level 2", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('english_development', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('financial_development', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('it_development', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):
        if not instance:
            instance = EducationProgrammeAssessment.objects.create(registration_id=registry)
            instance.pre_test = request.POST
        else:
            instance = EducationProgrammeAssessment.objects.get(id=instance)
            if pre_post == "pre":
                instance.pre_test = request.POST
            if pre_post == "post":
                instance.post_test = request.POST

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(YouthScoringForm, self).clean()
        programme_type = cleaned_data.get("programme_type") or self.initial.get("programme_type")
        thresholds = {
            "YBLN Level 1": {
                "arabic_grade": 12,
                "language_grade": 20,
                "math_grade": 15,
                "life_skills": 12,
            },
            "YBLN Level 2": {
                "arabic_grade": 12,
                "language_grade": 12,
                "math_grade": 21,
                "life_skills": 12,
            },
            "YFS Level 1": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 2": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 1 - RS Grade 9": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 2 - RS Grade 9": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            }
        }

        if programme_type in thresholds:
            programme_thresholds = thresholds[programme_type]

            for field, max_value in programme_thresholds.items():
                field_value = cleaned_data.get(field)
                if field_value is not None and field_value > max_value:
                    self.add_error(field, "This value is greater than {}".format(max_value))

        return cleaned_data

    class Meta:
        model = EducationProgrammeAssessment
        fields = (
            'programme_type',
        )


class EducationSchoolGradingForm(forms.ModelForm):
    arabic_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Arabic Language",
        initial=0
    )
    language_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Foreign Language",
        initial=0
    )
    math_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Mathematics",
        initial=0
    )
    biology_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Biology",
        initial=0
    )
    chemistry_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Chemistry",
        initial=0
    )
    physics_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Physics",
        initial=0
    )
    science_grade = forms.DecimalField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'step': '0.01'})),
        required=False,
        label="Science",
        initial=0
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        instance = kwargs.pop('instance', None)

        super(EducationSchoolGradingForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_school_grading',
                              kwargs={'registry': registry, 'programme_type': programme_type, 'pk': instance})

        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['biology_grade'], 'Biology', 20)
            field_init(self.fields['chemistry_grade'], 'Chemistry', 20)
            field_init(self.fields['physics_grade'], 'Physics', 20)
            self.fields['science_grade'].hidden_widget()

        if programme_type in ["Summer RS Grade 7", "Summer RS Grade 8", "Summer RS Grade 9", "YFS Level 1 - Summer RS Grade 9", "YFS Level 2 - Summer RS Grade 9"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['biology_grade'], 'Biology', 20)
            field_init(self.fields['chemistry_grade'], 'Chemistry', 20)
            field_init(self.fields['physics_grade'], 'Physics', 20)
            self.fields['science_grade'].hidden_widget()

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()

        if programme_type in ["Summer RS Grade 1", "Summer RS Grade 2", "Summer RS Grade 3", "Summer RS Grade 4", "Summer RS Grade 5", "Summer RS Grade 6"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('biology_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('chemistry_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('physics_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),

                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["Summer RS Grade 7", "Summer RS Grade 8", "Summer RS Grade 9", "YFS Level 1 - Summer RS Grade 9", "YFS Level 2 - Summer RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('biology_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('chemistry_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('physics_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),

                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["Summer RS Grade 1", "Summer RS Grade 2", "Summer RS Grade 3", "Summer RS Grade 4", "Summer RS Grade 5", "Summer RS Grade 6"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None):
        instance = EducationProgrammeAssessment.objects.get(id=instance)
        instance.school_test = request.POST
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationSchoolGradingForm, self).clean()
        arabic_grade = cleaned_data.get("arabic_grade")
        language_grade = cleaned_data.get("language_grade")
        math_grade = cleaned_data.get("math_grade")
        biology_grade = cleaned_data.get("biology_grade")
        chemistry_grade = cleaned_data.get("chemistry_grade")
        physics_grade = cleaned_data.get("physics_grade")
        science_grade = cleaned_data.get("science_grade")

        if arabic_grade and arabic_grade > 20:
            self.add_error('arabic_grade', 'This value is greater that 20')
        if language_grade and language_grade > 20:
            self.add_error('language_grade', 'This value is greater that 20')
        if math_grade and math_grade > 20:
            self.add_error('math_grade', 'This value is greater that 20')
        if biology_grade and biology_grade > 20:
            self.add_error('biology_grade', 'This value is greater that 20')
        if chemistry_grade and chemistry_grade > 20:
            self.add_error('chemistry_grade', 'This value is greater that 20')
        if physics_grade and physics_grade > 20:
            self.add_error('physics_grade', 'This value is greater that 20')
        if science_grade and science_grade > 20:
            self.add_error('science_grade', 'This value is greater that 20')

    class Meta:
        model = EducationProgrammeAssessment
        fields = ()


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True
