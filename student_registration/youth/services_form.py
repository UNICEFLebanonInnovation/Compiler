from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset

from .models import (
    YouthAssessment,
    YES_NO,
    AGREE_DISAGREE
)


class YouthAssessmentForm(forms.ModelForm):

    undertake_post_diagnostic = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the adolescent receive a passing grade for the tests?')
    )
    complete_life_skills = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_opportunity = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthAssessment.VOLUNTEERING_OPPORTUNITY,
        label=_('Is yes, please specify the volunteering opportunity')
    )
    benefit_innovation_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    compelete_yfs_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the YFS course?')
    )
    training_material = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthAssessment.TRAINING_MATERIAL,
        label=_('What training material was provided?')
    )
    future_path = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthAssessment.FUTURE_PATH,
        label=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate/come up in community based initiatives?')
    )
    attendance = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthAssessment.ATTENDANCE,
        label=_('Adolescent attendance')
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('youth:service_youth_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('youth:service_youth_assessment_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('undertake_post_diagnostic', css_class='col-md-5'),
                    Div('receive_passing_grade', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('complete_life_skills', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('participate_volunteering', css_class='col-md-7'),
                    Div('volunteering_opportunity', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('benefit_innovation_course', css_class='col-md-8'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('compelete_yfs_course', css_class='col-md-6'),
                    Div('training_material', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('future_path', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('participate_community_initiatives', css_class='col-md-8'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('attendance', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = YouthAssessment.objects.create(registration_id=registry)
        else:
            instance = YouthAssessment.objects.get(id=instance)

        instance.undertake_post_diagnostic = validated_data.get('undertake_post_diagnostic')
        instance.undertake_post_diagnostic = validated_data.get('undertake_post_diagnostic')
        instance.receive_passing_grade = validated_data.get('receive_passing_grade')
        instance.complete_life_skills = validated_data.get('complete_life_skills')
        instance.participate_volunteering = validated_data.get('participate_volunteering')
        instance.volunteering_opportunity = validated_data.get('volunteering_opportunity')
        instance.benefit_innovation_course = validated_data.get('benefit_innovation_course')
        instance.compelete_yfs_course = validated_data.get('compelete_yfs_course')
        instance.training_material = validated_data.get('training_material')
        instance.future_path = validated_data.get('future_path')
        instance.participate_community_initiatives = validated_data.get('participate_community_initiatives')
        instance.attendance = validated_data.get('attendance')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))


        return instance

    def clean(self):
        cleaned_data = super(YouthAssessmentForm, self).clean()
        undertake_post_diagnostic = cleaned_data.get("undertake_post_diagnostic")
        receive_passing_grade = cleaned_data.get("receive_passing_grade")
        if undertake_post_diagnostic and undertake_post_diagnostic == 'Yes' and not receive_passing_grade:
            self.add_error('receive_passing_grade', 'This field is required')

        participate_volunteering = cleaned_data.get("participate_volunteering")
        volunteering_opportunity = cleaned_data.get("volunteering_opportunity")
        if participate_volunteering and participate_volunteering == 'Yes' and not volunteering_opportunity:
            self.add_error('volunteering_opportunity', 'This field is required')

        compelete_yfs_course = cleaned_data.get("compelete_yfs_course")
        training_material = cleaned_data.get("training_material")
        if compelete_yfs_course and compelete_yfs_course == 'Yes' and not training_material:
            self.add_error('training_material', 'This field is required')

    class Meta:
        model = YouthAssessment
        fields = (
            'undertake_post_diagnostic',
            'receive_passing_grade',
            'complete_life_skills',
            'participate_volunteering',
            'volunteering_opportunity',
            'benefit_innovation_course',
            'compelete_yfs_course',
            'training_material',
            'future_path',
            'participate_community_initiatives',
            'attendance'
        )


