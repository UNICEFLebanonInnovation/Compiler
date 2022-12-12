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
        super(EducationAssessmentForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        # form_action = reverse('mscc:education_assessment_create')
        form_action = reverse('mscc:education_assessment')

        if instance:
            # form_action = reverse('mscc:education_assessment_edit', kwargs={'pk': instance.id})
            form_action = reverse('mscc:education_assessment', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
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

    def save(self, request=None, instance=None):

        data = {}
        validated_data = request.POST

        if not instance:
            instance = EducationAssessment.objects.create(owner=request.user)

        instance.registration_id = validated_data.get('registration_id')
        instance.pre_attended_arabic = validated_data.get('pre_attended_arabic')
        instance.pre_modality_arabic = validated_data.get('pre_modality_arabic')
        instance.pre_arabic_grade = validated_data.get('pre_arabic_grade')
        instance.pre_attended_language = validated_data.get('pre_attended_language')
        instance.pre_modality_language = validated_data.get('pre_modality_language')
        instance.pre_language_grade = validated_data.get('pre_language_grade')
        instance.pre_attended_math = validated_data.get('pre_attended_math')
        instance.pre_modality_math = validated_data.get('pre_modality_math')
        instance.pre_math_grade = validated_data.get('pre_math_grade')
        instance.participation = validated_data.get('participation')
        instance.barriers = validated_data.get('barriers')
        instance.barriers_other = validated_data.get('barriers_other')
        instance.post_test_done = validated_data.get('post_test_done')
        instance.school_year_completed = validated_data.get('school_year_completed')
        instance.post_attended_arabic = validated_data.get('post_attended_arabic')
        instance.post_modality_arabic = validated_data.get('post_modality_arabic')
        instance.post_arabic_grade = validated_data.get('post_arabic_grade')
        instance.post_attended_language = validated_data.get('post_attended_language')
        instance.post_modality_language = validated_data.get('post_modality_language')
        instance.post_language_grade = validated_data.get('post_language_grade')
        instance.post_attended_math = validated_data.get('post_attended_math')
        instance.post_modality_math = validated_data.get('post_modality_math')
        instance.post_math_grade = validated_data.get('post_math_grade')
        instance.modified_by = request.user
        instance.save()

        request.session['instance_id'] = instance.id
        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

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
