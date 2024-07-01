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
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset
from dal import autocomplete

from .models import (
    Registration,
    EnrolledPrograms,
    YES_NO,
    Round,
    Program,
    SubProgram,
    Donor
)
from student_registration.schools.models import (
    School,
    PartnerOrganization
)


class EnrolledProgramsForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_("Youth\'s educational level when registering"),
        widget=forms.Select, required=True,
        choices=EnrolledPrograms.EDUCATION_STATUS,
    )
    dropout_date = forms.DateField(
        label=_("Please Specify dropout date from school"),
        required=False
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(), widget=forms.Select,
        label=_('Program'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    sub_program = forms.ModelChoiceField(
        queryset=SubProgram.objects.all(), widget=forms.Select,
        label=_('Sub Program'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    donor = forms.ModelChoiceField(
        queryset=Donor.objects.all(), widget=forms.Select,
        label=_('Donor'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    registration_date = forms.DateField(
        label=_("Date of registration"),
        required=True
    )

    completion_date = forms.DateField(
        label=_("Date of completion"),
        required=True
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)
        package_type = kwargs.pop('package_type', None)

        super(EnrolledProgramsForm, self).__init__(*args, **kwargs)

        self.fields['registration_id'].initial = registry

        choices_education_status = list()
        if package_type == 'Walk-in':
            choices_education_status.append(('', _('----------')))
            choices_education_status.append(('Currently registered in Formal Education school',
                                             _('Currently registered in Formal Education school')))
            choices_education_status.append(('Currently registered in Formal Education school but not attending',
                                             _('Currently registered in Formal Education school but not attending')))
            self.fields['education_status'].choices = choices_education_status

        display_edu_section = ''

        form_action = reverse('youth:service_enrolled_programs_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('youth:service_enrolled_programs_edit',
                                  kwargs={'registry': registry, 'pk': instance})

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
                    Div('registration_date', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('completion_date', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('donor', css_class='col-md-3'),
                    css_class='row card-body'
                ),

                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('program', css_class='col-md-9'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('sub_program', css_class='col-md-9'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                HTML(
                    '<a type="reset" name="cancel" class="btn btn-inverse btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning" id="cancel-id-cancel" href="/youth/Child-Registration-Cancel/{}/">Cancel</a>'.format(
                        registry)
                ),

            ),
        )

    def save(self, request=None, instance=None, registry=None, package_type=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = EnrolledPrograms.objects.create(registration_id=registry)
        else:
            instance = EnrolledPrograms.objects.get(id=instance)

        instance.education_status = validated_data.get('education_status')
        dropout_date_str = validated_data.get('dropout_date')
        if dropout_date_str:
            dropout_date = datetime.strptime(dropout_date_str, '%Y-%m-%d')
            instance.dropout_date = dropout_date
        instance.program_id = validated_data.get('program')
        instance.sub_program_id = validated_data.get('sub_program')
        instance.donor_id = validated_data.get('donor')
        registration_date_str = validated_data.get('registration_date')
        if registration_date_str:
            registration_date = datetime.strptime(registration_date_str, '%Y-%m-%d')
            instance.registration_date = registration_date

        completion_date_str = validated_data.get('completion_date')
        if completion_date_str:
            completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d')
            instance.completion_date = completion_date

        instance.save()

        registry = instance.registration
        registry.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance


    class Meta:
        model = EnrolledPrograms
        fields = (
            'registration_id',
            'education_status',
            'dropout_date',
            'program',
            'sub_program',
            'registration_date',
            'completion_date',
        )


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True

