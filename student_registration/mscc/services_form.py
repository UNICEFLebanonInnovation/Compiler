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
        super(PSSServiceForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('mscc:service_pss_create')
        if instance:
            form_action = reverse('mscc:service_pss_edit', kwargs={'pk': instance.id})

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
                css_id='step-2'
            ),
        )

    def save(self, request=None, instance=None):

        data = {}
        validated_data = request.POST

        if not instance:
            instance = PSSService.objects.create(owner=request.user)

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

        request.session['instance_id'] = instance.id
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
            form_action = reverse('mscc:service_digital_edit', kwargs={'registry': registry, 'pk': instance.id})

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

        form_action = reverse('mscc:health_nutrition_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:health_nutrition_edit', kwargs={'registry': registry, 'pk': instance.id})

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
