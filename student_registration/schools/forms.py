from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML

from .models import School, PartnerOrganization, EducationYear


class ProfileForm(forms.ModelForm):

    email = forms.EmailField(
        label=_('School email')
    )
    land_phone_number = forms.RegexField(
        label=_('School land phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$'
    )
    fax_number = forms.RegexField(
        label=_('School fax number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        required=False
    )
    director_phone_number =forms.RegexField(
        label=_('School director cell phone'),
        regex=r'^[0-9]{2}-[0-9]{6}$'
    )
    it_phone_number = forms.RegexField(
        label=_('School IT phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$'
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        current_education_year = EducationYear.objects.get(current_year=True)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:profile', kwargs={})

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('director_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('land_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('fax_number', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('director_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">5</span>'),
                    Div('email', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('certified_foreign_language', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">7</span>'),
                    Div('comments', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">8</span>'),
                    Div('weekend', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">9</span>'),
                    Div('it_name', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">10</span>'),
                    Div('it_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">11</span>'),
                    Div('field_coordinator_name', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Current academic year') + ' ' + current_education_year.name + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('academic_year_start', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('academic_year_end', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('academic_year_exam_end', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(ProfileForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = School
        fields = (
            'academic_year_start',
            'academic_year_end',
            'academic_year_exam_end',
            'director_name',
            'land_phone_number',
            'director_phone_number',
            'it_name',
            'it_phone_number',
            'field_coordinator_name',
            'fax_number',
            'email',
            'certified_foreign_language',
            'comments',
            'weekend',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class PartnerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:partner', kwargs={})

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('CLM round') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('bln_round', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('rs_round', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('cbece_round', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PartnerForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = PartnerOrganization
        fields = (
            'bln_round',
            'rs_round',
            'cbece_round',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()
