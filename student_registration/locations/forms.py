from __future__ import unicode_literals, absolute_import, division

from student_registration.users.templatetags.custom_tags import has_group
from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)

from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset

from dal import autocomplete

from student_registration.locations.models import Location
from .models import (
    Center,

)


class CenterAdminForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput, required=True
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    caza = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False, type=2),
        widget=forms.Select,
        label=_('Caza'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        required=True,
        queryset=Location.objects.filter(parent__isnull=False, type=3),
        widget=autocomplete.ModelSelect2(url='location_autocomplete'),
        label=_('Cadaster')
    )
    p_code = forms.CharField(
        label=_("P-Code"),
        widget=forms.TextInput, required=True
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Municipality', _('Municipality')),
            ('Collective Settlement', _('Collective Settlement')),
            ('Informal Settlement', _('Informal Settlement')),
            ('Welfare Center', _('Welfare Center')),
            ('Community Hub', _('Community Hub')),
        ),
        initial=''
    )
    provided_packages = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices= Center.PROVIDED_PACKAGES,
    )

    def __init__(self, *args, **kwargs):
        super(CenterAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Center
        fields = '__all__'


class CenterForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput,
        required = False
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    caza = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False, type=2),
        widget=forms.Select,
        label=_('Caza'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        required=True,
        queryset=Location.objects.filter(parent__isnull=False, type=3),
        widget=autocomplete.ModelSelect2(url='location_autocomplete'),
        label=_('Cadaster')
    )
    longitude = forms.FloatField(
        label=_('Center GPS (longitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('Center GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    manager_name = forms.CharField(
        label=_("Center Manager name"),
        widget=forms.TextInput, required=True
    )
    phone_number = forms.RegexField(
        regex=r'^\d{2}-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        required=False,
        label=_('Email')
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=Center.TYPE,
        initial=''
    )
    provided_packages = forms.MultipleChoiceField(
        label=_('Provided Services'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=Center.PROVIDED_PACKAGES
    )
    education_programs = forms.MultipleChoiceField(
        label=_('Education Program'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=Center.EDUCATION_PROGRAM
    )
    youth_programs = forms.MultipleChoiceField(
        label=_('Youth Program'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=Center.YOUTH_PROGRAM
    )
    cwd_accessible = forms.ChoiceField(
        label=_("Is the center accessible for CWD ?"),
        widget=forms.Select, required=False,
        choices=Center.YES_NO,
    )
    admin_staff_number = forms.IntegerField(
        label=_('Number of Admin staff in the center'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0,
        min_value=0
    )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        pk = kwargs.pop('pk', None)
        super(CenterForm, self).__init__(*args, **kwargs)
        mscc_center_user = has_group(self.request.user, 'MSCC_CENTER')
        form_action = reverse('locations:center_add')

        if pk:
            form_action = reverse('locations:center_edit', kwargs={'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('name', css_class='col-md-3 disabled-input'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('caza', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(

                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('manager_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('type', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('provided_packages', css_class='col-md-3  multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('education_programs', css_class='col-md-3  multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('youth_programs', css_class='col-md-3  multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('cwd_accessible', css_class='col-md-3  multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('admin_staff_number', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),

                ),
                css_id='step-1',
            ),
        )

    def save(self, request=None, instance=None):
        validated_data = request.POST

        if not instance:
            instance = Center.objects.create()
        else:
            instance = Center.objects.get(id=instance)


        instance.governorate_id = validated_data.get('governorate')
        instance.caza_id = validated_data.get('caza')
        instance.cadaster_id = validated_data.get('cadaster')
        instance.longitude = validated_data.get('longitude')
        instance.latitude = validated_data.get('latitude')
        instance.manager_name = validated_data.get('manager_name')
        instance.phone_number = validated_data.get('phone_number')
        instance.email = validated_data.get('email')
        instance.type = validated_data.get('type')
        instance.provided_packages = validated_data.getlist('provided_packages')
        instance.education_programs = validated_data.getlist('education_programs')
        instance.youth_programs = validated_data.getlist('youth_programs')
        instance.cwd_accessible = validated_data.getlist('cwd_accessible')
        instance.admin_staff_number = validated_data.get('admin_staff_number')
        instance.modified_by = request.user

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance
    class Meta:
        model = Center
        fields = (
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'provided_packages',
            'education_programs',
            'youth_programs',
            'cwd_accessible',
            'admin_staff_number',

        )



