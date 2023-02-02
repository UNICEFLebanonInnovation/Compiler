from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete

from .models import (
    EducationAssessment,
    EducationService,
    EducationRSService,
    YES_NO
)
from student_registration.schools.models import (
    School,
    PartnerOrganization
)


class DiagnosticAssessmentForm(forms.ModelForm):
    # Pre Test
    pre_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
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
        initial='yes'
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
        initial='yes'
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
                    Div('pre_attended_arabic', css_class='col-md-7'),
                    Div('pre_modality_arabic', css_class='col-md-3'),
                    Div('pre_arabic_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    Div('pre_attended_language', css_class='col-md-7'),
                    Div('pre_modality_language', css_class='col-md-3'),
                    Div('pre_language_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    Div('pre_attended_math', css_class='col-md-7'),
                    Div('pre_modality_math', css_class='col-md-3'),
                    Div('pre_math_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
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
        if pre_attended_arabic and pre_attended_arabic == 'Yes' :
            if not pre_modality_arabic:
                self.add_error('pre_modality_arabic', 'This field is required')
            if not pre_arabic_grade:
                self.add_error('pre_arabic_grade', 'This field is required')

        pre_attended_language = cleaned_data.get("pre_attended_language")
        pre_modality_language = cleaned_data.get("pre_modality_language")
        pre_language_grade = cleaned_data.get("pre_language_grade")
        if pre_attended_language and pre_attended_language == 'Yes' :
            if not pre_modality_language:
                self.add_error('pre_modality_language', 'This field is required')
            if not pre_language_grade:
                self.add_error('pre_language_grade', 'This field is required')

        pre_attended_math = cleaned_data.get("pre_attended_math")
        pre_modality_math = cleaned_data.get("pre_modality_math")
        pre_math_grade = cleaned_data.get("pre_math_grade")
        if pre_attended_math and pre_attended_math == 'Yes' :
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
        initial='yes'
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
        initial = 0
    )
    post_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
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
        initial = 0
    )
    post_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
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
        initial = 0
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
                    Div('participation', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    Div('barriers', css_class='col-md-8'),
                    Div('barriers_other', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_test_done', css_class='col-md-6'),
                    Div('school_year_completed', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_attended_arabic', css_class='col-md-7'),
                    Div('post_modality_arabic', css_class='col-md-3 grd-arabic'),
                    Div('post_arabic_grade', css_class='col-md-2 grd-arabic'),
                    css_class='row grades card-body'
                ),
                Div(
                    Div('post_attended_language', css_class='col-md-7'),
                    Div('post_modality_language', css_class='col-md-3'),
                    Div('post_language_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                Div(
                    Div('post_attended_math', css_class='col-md-7'),
                    Div('post_modality_math', css_class='col-md-3'),
                    Div('post_math_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
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
    dropout_program = forms.ChoiceField(
        label=_("Dropout Program"),
        widget=forms.Select, required=False,
        choices=EducationService.DROPOUT_PROGRAM,
    )
    dropout_program_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    education_program = forms.ChoiceField(
        label=_("Education Program"),
        widget=forms.Select, required=True,
        choices=EducationService.EDUCATION_PROGRAM,
    )
    registration_date = forms.DateField(
        label=_("Date of registration in the round"),
        required=False
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(EducationServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_education_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_education_edit',
                                  kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('education_status', css_class='col-md-9'),
                    css_class='row card-body'
                ),
                Div(
                    Div('dropout_date', css_class='col-md-5'),
                    Div('dropout_program', css_class='col-md-4'),
                    Div('dropout_program_specify', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('education_program', css_class='col-md-4'),
                    Div('registration_date', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationService.objects.create(registration_id=registry)
        else:
            instance = EducationService.objects.get(id=instance)

        instance.education_status = validated_data.get('education_status')
        if validated_data.get('dropout_date'):
            instance.dropout_date = validated_data.get('dropout_date')
        instance.dropout_program = validated_data.get('dropout_program')
        instance.dropout_program_specify = validated_data.get('dropout_program_specify')
        instance.education_program = validated_data.get('education_program')
        if validated_data.get('registration_date'):
            instance.registration_date = validated_data.get('registration_date')
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationServiceForm, self).clean()
        dropout_program = cleaned_data.get("dropout_program")
        dropout_program_specify = cleaned_data.get("dropout_program_specify")
        if dropout_program and dropout_program == 'Other' and not dropout_program_specify:
            self.add_error('dropout_program_specify', 'This field is required')
    class Meta:
        model = EducationService
        fields = (
            'education_status',
            'dropout_date',
            'dropout_program',
            'dropout_program_specify',
            'education_program',
            'registration_date',
        )


class EducationRSServiceForm(forms.ModelForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.all(), widget=forms.Select,
        label=_('Name of public School'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    foreign_language_grade = forms.IntegerField(
        label=_('Foreign Language\'s grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    arabic_grade = forms.IntegerField(
        label=_('Arabic grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    math_grade = forms.IntegerField(
        label=_('Math grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    sciences_grade = forms.IntegerField(
        label=_('Sciences grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False,
        initial=0
    )
    shift = forms.ChoiceField(
        label=_("First or Second shift schools"),
        widget=forms.Select,
        required=False,
        choices=EducationRSService.SCHOOL_SHIFTS
    )
    grade_level = forms.ChoiceField(
        label=_("Grade level"),
        widget=forms.Select,
        required=False,
        choices=EducationRSService.REGISTRATION_LEVEL
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
                    Div('school', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('foreign_language_grade', css_class='col-md-3'),
                    Div('arabic_grade', css_class='col-md-3'),
                    Div('math_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('sciences_grade', css_class='col-md-3'),
                    Div('shift', css_class='col-md-3'),
                    Div('grade_level', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('support_needed', css_class='col-md-3 multiple-choice'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),

                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
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

        instance.foreign_language_grade = int(validated_data.get('foreign_language_grade'))
        instance.arabic_grade = int(validated_data.get('arabic_grade'))
        instance.math_grade = int(validated_data.get('math_grade'))
        instance.sciences_grade = int(validated_data.get('sciences_grade'))
        instance.shift = validated_data.get('shift')
        instance.grade_level = validated_data.get('grade_level')
        instance.support_needed = validated_data.getlist('support_needed')
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='RS', service_id=instance.id)

        return instance


    class Meta:
        model = EducationRSService
        fields = (
            'school',
            'foreign_language_grade',
            'arabic_grade',
            'math_grade',
            'sciences_grade',
            'shift',
            'grade_level',
            'support_needed',
        )
