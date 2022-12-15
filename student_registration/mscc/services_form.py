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
    PSSService,
    InclusionService,
    DigitalService,
    HealthNutritionService,
    YouthKitService,
    YES_NO
)

class PSSServiceForm(forms.ModelForm):

    child_registered = forms.ChoiceField(
        label=_("Is the child registered/ have birth registration?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )

    child_living_arrangement = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.LIVING_ARRANGEMENT,
        label=_("What is the child's living arrangement?")
    )
    child_vulnerability = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.CHILD_VULNERABILITY,
        label=_("What is the child's living arrangement?")
    )
    child_out_school_reasons = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.OUT_SCHOOL_REASONS,
        label=_("Reasons for a child being out of school")
    )
    caregivers_distress = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Do you feel distressed and anxious?')
    )
    caregivers_additional_parenting = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('If yes, would you like any additional parenting or psychosocial support?')
    )
    child_distress = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Are any of the children in your HH experiencing any '
                       'signs of distress or negative mental health symptoms ?')
    )
    child_additional_parenting = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('If yes, do you need additional support '
                       'for taking care or better dealing with your children?')
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(PSSServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_pss_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_pss_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('child_registered', css_class='col-md-3'),
                    Div('child_living_arrangement', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('child_vulnerability', css_class='col-md-3'),
                    Div('child_out_school_reasons', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('caregivers_distress', css_class='col-md-3'),
                    Div('caregivers_additional_parenting', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('child_distress', css_class='col-md-3'),
                    Div('child_additional_parenting', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                ),
                css_id='step-2'
            )
        )
    def save(self, request=None, instance=None, registry=None):
        validated_data = request.POST

        if not instance:
            instance = PSSService.objects.create(registration_id=registry)
        else:
            instance = PSSService.objects.get(id=instance)
        instance.child_registered = validated_data.get('child_registered')
        instance.child_living_arrangement = validated_data.get('child_living_arrangement')
        instance.child_vulnerability = validated_data.get('child_vulnerability')
        instance.child_out_school_reasons = validated_data.get('child_out_school_reasons')
        instance.caregivers_distress = validated_data.get('caregivers_distress')
        instance.child_additional_parenting = validated_data.get('caregivers_additional_parenting')
        instance.child_additional_parenting = validated_data.get('child_distress')
        instance.child_additional_parenting = validated_data.get('child_additional_parenting')
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance

    class Meta:
        model = PSSService
        fields = (
            'child_registered',
            'child_living_arrangement',
            'child_vulnerability',
            'child_out_school_reasons',
            'caregivers_distress',
            'caregivers_additional_parenting',
            'child_distress',
            'child_additional_parenting',
        )


class InclusionServiceForm(forms.ModelForm):

    dropout = forms.ChoiceField(
        label=_("Dropout"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    parental_engagement = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=InclusionService.PARENTAL_ENGAGEMENT,
        label=_('Parental Engagement Curriculum')
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(InclusionServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_inclusion_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_inclusion_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('dropout', css_class='col-md-3'),
                    Div('parental_engagement', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = InclusionService.objects.create(registration_id=registry)
        else:
            instance = InclusionService.objects.get(id=instance)

        instance.dropout = validated_data.get('dropout')
        instance.parental_engagement = validated_data.get('parental_engagement')
        # instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = InclusionService
        fields = (
            'dropout',
            'parental_engagement',
        )


class DigitalServiceForm(forms.ModelForm):

    using_akelius = forms.ChoiceField(
        label=_("Is the child using Akelius?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    using_lp = forms.ChoiceField(
        label=_("Is the child using Learning Passport?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(DigitalServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_digital_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_digital_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('using_akelius', css_class='col-md-3'),
                    Div('using_lp', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = DigitalService.objects.create(registration_id=registry)
        else:
            instance = DigitalService.objects.get(id=instance)

        instance.using_akelius = validated_data.get('using_akelius')
        instance.using_lp = validated_data.get('using_lp')
        # instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = DigitalService
        fields = (
            'using_akelius',
            'using_lp',
        )


class HealthNutritionServiceForm(forms.ModelForm):
    # Caregivers of children 0-2
    baby_breastfed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Is the baby being Breastfed?')
    )
    # Caregivers of children 0-2
    infant_exclusively_breastfed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('if yes, is it exclusively breastfeeding for infants between 0-6 months?')
    )
    # Caregivers of children 0-2
    eat_solid_food = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the child start to eat solid food?')
    )
    # Caregivers of children 0-2
    age_eat_solid_food = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=HealthNutritionService.AGE_EAT_SOLID_FOOD,
        label=_('If yes, at which age ?')
    )
    # Caregivers of children 0-2 - children 3-5 - children 5-18
    child_vaccinated = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Is the child being vaccinated as per the National vaccination calendar?')
    )
    # Caregivers of children 0-2 - children 3-5
    development_delays_identified = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=HealthNutritionService.DEVELOPMENT_DELAYS,
        label=_('Any mental , cognitive or neurological development delays is being identified?')
    )

    # Caregivers of children 3-5 - children 5-18
    eating_minimum_meals = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Is the child eating 3 minimum meals per day?')
    )
    # Caregivers of children 3-5
    positive_parenting = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('positive parenting and dealing with difficult children without the use of harsh punishment?')
    )
    # Caregivers of children 5-18
    respond_stressful_events = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('How children of different ages respond to and understand stressful and traumatic events?')
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(HealthNutritionServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_health_nutrition_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_health_nutrition_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('baby_breastfed', css_class='col-md-3'),
                    Div('infant_exclusively_breastfed', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('eat_solid_food', css_class='col-md-3'),
                    Div('age_eat_solid_food', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('child_vaccinated', css_class='col-md-3'),
                    Div('development_delays_identified', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    Div('eating_minimum_meals', css_class='col-md-3'),
                    Div('positive_parenting', css_class='col-md-3'),
                    Div('respond_stressful_events', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = HealthNutritionService.objects.create(registration_id=registry)
        else:
            instance = HealthNutritionService.objects.get(id=instance)

        instance.baby_breastfed = validated_data.get('baby_breastfed')
        instance.infant_exclusively_breastfed = validated_data.get('infant_exclusively_breastfed')
        instance.eat_solid_food = validated_data.get('eat_solid_food')
        instance.age_eat_solid_food = validated_data.get('age_eat_solid_food')
        instance.child_vaccinated = validated_data.get('child_vaccinated')
        instance.development_delays_identified = validated_data.get('development_delays_identified')
        instance.eating_minimum_meals = validated_data.get('eating_minimum_meals')
        instance.positive_parenting = validated_data.get('positive_parenting')
        instance.respond_stressful_events = validated_data.get('respond_stressful_events')
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance

    class Meta:
        model = HealthNutritionService
        fields = (
            'baby_breastfed',
            'infant_exclusively_breastfed',
            'eat_solid_food',
            'age_eat_solid_food',
            'child_vaccinated',
            'development_delays_identified',
            'eating_minimum_meals',
            'positive_parenting',
            'respond_stressful_events',
        )


class YouthKitServiceForm(forms.ModelForm):

    # For Youth
    volunteering_experience = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Does the adolescent have any volunteering experience?')
    )
    previous_community_initiative = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Was the adolescent part of any previous community based initiative?')
    )
    enrollment_reason = forms.CharField(
        required=True,
        widget=forms.TextInput,
        label=_('What is the reason for the adolescent enrollment in the programme?')
    )
    pre_tests_administered = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Were pre-tests administered to assess adolescents level?')
    )
    # Youth Assessment
    test_diagnostic_done = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the adolescent receive a passing grade for the tests?')
    )
    life_skills_completed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate in any volunteering '
                       'opportunity during the course of the program?')
    )
    volunteering_specify = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthKitService.VOLUNTEERING,
        label=_('Please specify the volunteering opportunity')
    )
    social_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    yfs_course_completed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the YFS course?')
    )
    training_material = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthKitService.TRAINING_MATERIAL,
        label=_('What training material was provided?')
    )
    future_path = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthKitService.FUTURE_PATH,
        label=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate/come up in community based initiatives?')
    )
    community_initiatives_specify = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('What is the initiative?')
    )
    adolescent_attendance = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthKitService.ATTENDANCE,
        label=_('Adolescent attendance')
    )
    adolescent_dropout_reason = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Reason for dropout')
    )
    adolescent_dropout_date = forms.DateField(
        label=_("Dropout Date"),
        required=False
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthKitServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_kit_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_youth_kit_edit', kwargs={'registry': registry, 'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    Div('volunteering_experience', css_class='col-md-6'),
                    Div('previous_community_initiative', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('enrollment_reason', css_class='col-md-6'),
                    Div('pre_tests_administered', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    Div('test_diagnostic_done', css_class='col-md-6'),
                    Div('receive_passing_grade', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('life_skills_completed', css_class='col-md-6'),
                    css_class='row card-body'
                ),

                Div(
                    Div('participate_volunteering', css_class='col-md-8'),
                    Div('volunteering_specify', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    Div('social_course', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('yfs_course_completed', css_class='col-md-5'),
                    Div('training_material', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    Div('future_path', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('participate_community_initiatives', css_class='col-md-6'),
                    Div('community_initiatives_specify', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    Div('adolescent_attendance', css_class='col-md-4'),
                    Div('adolescent_dropout_reason', css_class='col-md-4'),
                    Div('adolescent_dropout_date', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                ),
                css_id='step-2',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = YouthKitService.objects.create(registration_id=registry)
        else:
            instance = YouthKitService.objects.get(id=instance)

        instance.volunteering_experience = validated_data.get('volunteering_experience')
        instance.previous_community_initiative = validated_data.get('previous_community_initiative')
        instance.enrollment_reason = validated_data.get('enrollment_reason')
        instance.pre_tests_administered = validated_data.get('pre_tests_administered')
        instance.test_diagnostic_done = validated_data.get('test_diagnostic_done')
        instance.receive_passing_grade = validated_data.get('receive_passing_grade')
        instance.life_skills_completed = validated_data.get('life_skills_completed')
        instance.participate_volunteering = validated_data.get('participate_volunteering')
        instance.volunteering_specify = validated_data.get('volunteering_specify')
        instance.social_course = validated_data.get('social_course')
        instance.yfs_course_completed = validated_data.get('yfs_course_completed')
        instance.training_material = validated_data.get('training_material')
        instance.future_path = validated_data.get('future_path')
        instance.participate_community_initiatives = validated_data.get('participate_community_initiatives')
        instance.community_initiatives_specify = validated_data.get('community_initiatives_specify')
        instance.adolescent_attendance = validated_data.get('adolescent_attendance')
        instance.adolescent_dropout_reason = validated_data.get('adolescent_dropout_reason')
        instance.adolescent_dropout_date = validated_data.get('adolescent_dropout_date')
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance

    class Meta:
        model = YouthKitService
        fields = (
            'volunteering_experience',
            'previous_community_initiative',
            'enrollment_reason',
            'pre_tests_administered',
            'test_diagnostic_done',
            'receive_passing_grade',
            'life_skills_completed',
            'participate_volunteering',
            'volunteering_specify',
            'social_course',
            'yfs_course_completed',
            'training_material',
            'future_path',
            'participate_community_initiatives',
            'community_initiatives_specify',
            'adolescent_attendance',
            'adolescent_dropout_reason',
            'adolescent_dropout_date'
        )


