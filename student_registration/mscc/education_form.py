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
    Registration,
    EducationAssessment,
    YES_NO
)

class EducationAssessmentForm(forms.ModelForm):
    # Pre Test
    pre_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices= YES_NO,
        initial='yes'
    )
    pre_modality_arabic = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pre_arabic_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pre_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
    )
    pre_modality_language = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pre_language_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pre_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
    )
    pre_modality_math = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pre_math_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=True,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                       'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=True,
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
        choices= YES_NO,
        initial='yes'
    )
    post_modality_arabic = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    post_arabic_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    post_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
    )
    post_modality_language = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    post_language_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    post_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial='yes'
    )
    post_modality_math = forms.MultipleChoiceField(
        label=_('Modality'),
        choices=EducationAssessment.MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    post_math_grade = forms.FloatField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        reg_id = kwargs.pop('reg_id', None)

        super(EducationAssessmentForm, self).__init__(*args, **kwargs)


        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('mscc:add_education_assessment', kwargs={'reg_id': reg_id})

        self.fields['registration_id'].initial = reg_id

        if instance:
            form_action = reverse('mscc:edit_education_assessment', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    'registration_id',
                    css_class='row d-none',
                ),
                Div(
                    Div('pre_attended_arabic', css_class='col-md-3'),
                    Div('pre_modality_arabic', css_class='col-md-3'),
                    Div('pre_arabic_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('pre_attended_language', css_class='col-md-3'),
                    Div('pre_modality_language', css_class='col-md-3'),
                    Div('pre_language_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('pre_attended_math', css_class='col-md-3'),
                    Div('pre_modality_math', css_class='col-md-3'),
                    Div('pre_math_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('participation', css_class='col-md-3'),
                    Div('barriers', css_class='col-md-3'),
                    Div('barriers_other', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_test_done', css_class='col-md-3'),
                    Div('school_year_completed', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_attended_arabic', css_class='col-md-3'),
                    Div('post_modality_arabic', css_class='col-md-3'),
                    Div('post_arabic_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_attended_language', css_class='col-md-3'),
                    Div('post_modality_language', css_class='col-md-3'),
                    Div('post_language_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('post_attended_math', css_class='col-md-3'),
                    Div('post_modality_math', css_class='col-md-3'),
                    Div('post_math_grade', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                ),
                css_id='step-2'
            ),
        )

    def get_form_kwargs(self):
        kwargs = super(EducationAssessmentForm, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    class Meta:
        model = EducationAssessment
        fields = (
            'registration_id',
            'pre_attended_arabic',
            'pre_modality_arabic',
            'pre_arabic_grade',
            'pre_attended_language',
            'pre_modality_language',
            'pre_language_grade',
            'pre_attended_math',
            'pre_modality_math',
            'pre_math_grade',
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
