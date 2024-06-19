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
    Round
)
from student_registration.schools.models import (
    School,
    PartnerOrganization
)


class EnrolledProgramsForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_("Child\'s educational level when registering for the round"),
        widget=forms.Select, required=True,
        choices=EnrolledPrograms.EDUCATION_STATUS,
    )
    dropout_date = forms.DateField(
        label=_("Please Specify dropout date from school"),
        required=False
    )
    round = forms.ModelChoiceField(
        queryset=Round.objects.all(), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    programs = forms.ChoiceField(
        label=_("Core Package Program"),
        widget=forms.Select, required=True,
        choices=EnrolledPrograms.PROGRAM,
    )
    class_section = forms.ChoiceField(
        label=_("Class Section"),
        widget=forms.Select, required=True,
        choices=EnrolledPrograms.CLASS_SECTION,
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

        form_action = reverse('youth:service_education_add', kwargs={'registry': registry, 'package_type': package_type})
        if instance:
            form_action = reverse('youth:service_education_edit',
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
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('education_program', css_class='col-md-3'),
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
            old_class_section = instance.class_section
            new_class_section = validated_data.get('class_section')

        instance.education_status = validated_data.get('education_status')
        dropout_date_str = validated_data.get('dropout_date')
        if dropout_date_str:
            dropout_date = datetime.strptime(dropout_date_str, '%Y-%m-%d')
            instance.dropout_date = dropout_date
        instance.programs = validated_data.get('programs')
        instance.class_section = validated_data.get('class_section')
        instance.round_id = validated_data.get('round')
        registration_date_str = validated_data.get('registration_date')
        if registration_date_str:
            registration_date = datetime.strptime(registration_date_str, '%Y-%m-%d')
            instance.registration_date = registration_date

        instance.save()

        registry = instance.registration
        registry.round_id = instance.round_id
        registry.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    # def clean(self):
    #     cleaned_data = super(EducationServiceForm, self).clean()
    #     instance = self.instance
    #     if not instance.pk:
    #         registration_id = cleaned_data.get("registration_id")
    #         round_id = cleaned_data.get("round").id
    #
    #         registration = Registration.objects.get(id=registration_id)
    #         child = registration.child
    #
    #         # Count the number of registrations for the same child and round
    #         count = Registration.objects.filter(
    #             child=child,
    #             round__id=round_id
    #         ).exclude(id=registration_id).count()
    #
    #         last_registration = Registration.objects.filter(
    #             child=child,
    #             round__id=round_id
    #         ).exclude(id=registration_id).values(
    #             'center__name'
    #         ).order_by('-id').first()
    #
    #         if count > 0:
    #             center_name = last_registration['center__name']
    #             self.add_error('round', 'This child is already registered in the Center: ' + center_name)

    class Meta:
        model = EnrolledPrograms
        fields = (
            'registration_id',
            'education_status',
            'dropout_date',
            'round',
            'programs',
            'class_section',
            'registration_date',
        )


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True

