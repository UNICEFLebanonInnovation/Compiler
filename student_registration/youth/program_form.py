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
    MasterProgram,
    SubProgram,
    Donor,
    ProgramDocument,
    Partner,
    FundedBy,
    FocalPoint,
    Plan,
    Sector,
    ProjectType,
    PopulationGroups
)
from student_registration.locations.models import Location


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
    master_program = forms.ModelChoiceField(
        queryset=MasterProgram.objects.all(), widget=forms.Select,
        label=_('Master Program'),
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
    program_document = forms.ModelChoiceField(
        queryset=ProgramDocument.objects.all(), widget=forms.Select,
        label=_('Program Document'),
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

        super(EnrolledProgramsForm, self).__init__(*args, **kwargs)

        self.fields['registration_id'].initial = registry

        form_action = reverse('youth:program_enrolled_programs_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('youth:program_enrolled_programs_edit',
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
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('donor', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('program_document', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('master_program', css_class='col-md-9'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
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

    def save(self, request=None, instance=None, registry=None):
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
        instance.master_program_id = validated_data.get('master_program')
        instance.sub_program_id = validated_data.get('sub_program')
        instance.donor_id = validated_data.get('donor')
        instance.program_document_id = validated_data.get('program_document')

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
            'master_program',
            'sub_program',
            'registration_date',
            'completion_date',
        )


class ProgramDocumentForm_bak(forms.ModelForm):
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all(), widget=forms.Select,
        label=_('Partner'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    # funded_by = forms.ModelChoiceField(
    #     queryset=FundedBy.objects.all(), widget=forms.Select,
    #     label=_('Funded By'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    # project_status = forms.ChoiceField(
    #     label=_("Project Status"),
    #     widget=forms.Select, required=True,
    #     choices=ProgramDocument.PROJECT_STATUS
    # )
    # project_code = forms.CharField(
    #     label=_("Project Code"),
    #     widget=forms.TextInput, required=True
    # )
    # project_name = forms.CharField(
    #     label=_("Project Name"),
    #     widget=forms.TextInput, required=True
    # )
    # project_description = forms.CharField(
    #     label=_("Project Description"),
    #     widget=forms.TextInput, required=True
    # )
    # implementing_partners = forms.CharField(
    #     label=_("Key Implementing Partner(s)"),
    #     widget=forms.TextInput, required=True
    # )
    # focal_point = forms.ModelChoiceField(
    #     queryset=FocalPoint.objects.all(), widget=forms.Select,
    #     label=_('UNICEF Focal Point'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    # start_date = forms.DateField(
    #     label=_("Start Date"),
    #     required=False
    # )
    # end_date = forms.DateField(
    #     label=_("End Date"),
    #     required=False
    # )
    # comment = forms.CharField(
    #     label=_('Comment'),
    #     widget=forms.Textarea, required=False
    # )
    # plan = forms.ModelChoiceField(
    #     queryset=Plan.objects.all(), widget=forms.Select,
    #     label=_('Plan'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    # sectors = forms.ModelChoiceField(
    #     queryset=Sector.objects.all(), widget=forms.Select,
    #     label=_('SELECT SECTORS TARGETED BY THIS PROJECT'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    # project_type = forms.ModelChoiceField(
    #     queryset=ProjectType.objects.all(), widget=forms.Select,
    #     label=_('Type of Project'),
    #     empty_label='-------',
    #     required=True, to_field_name='id',
    # )
    # public_institution_support = forms.ChoiceField(
    #     label=_("Support of Public Institution"),
    #     widget=forms.Select, required=True,
    #     choices=ProgramDocument.SUPPORT
    # )
    governorates = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label=_('Governorate of Coverage'),
        required=False
    )
    #
    # budget = forms.FloatField(
    #     label=_('Please add the Project Budget in USD'),
    #     widget=forms.NumberInput(attrs=({'maxlength': 4})),
    #     min_value=0, required=False
    # )
    # cash_assistance = forms.ChoiceField(
    #     label=_("Does this Project have any Cash Assistance Component"),
    #     widget=forms.Select, required=True,
    #     choices=ProgramDocument.YES_NO
    # )
    # population_groups = models.ManyToManyField(PopulationGroups, blank=True, verbose_name=_('Governorate of Coverage'))

    # number_targeted_syrians = forms.IntegerField(
    #     label=_('Number of Targeted Displaced Syrians'),
    #     widget=forms.TextInput, required=False
    # )
    # number_targeted_lebanese = forms.IntegerField(
    #     label=_('Number of Targeted Lebanese'),
    #     widget=forms.TextInput, required=False
    # )
    # number_targeted_prl = forms.IntegerField(
    #     label=_('Number of Targeted PRL'),
    #     widget=forms.TextInput, required=False
    # )
    # number_targeted_prs = forms.IntegerField(
    #     label=_('Number of Targeted PRS'),
    #     widget=forms.TextInput, required=False
    # )
    # master_programs = models.ManyToManyField(MasterProgram, blank=True, verbose_name=_('Master Programs'))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        instance = kwargs.pop('instance', None)

        super(ProgramDocumentForm, self).__init__(*args, **kwargs)

        form_action = reverse('youth:program_program_document_add')
        if instance:
            form_action = reverse('youth:program_program_document_edit',
                                  kwargs={'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('partner', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    # Div('funded_by', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                # Div(
                #     HTML('<span class="badge-form badge-pill">3</span>'),
                #     Div('project_status', css_class='col-md-5'),
                #     HTML('<span class="badge-form badge-pill">4</span>'),
                #     Div('project_code', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form badge-pill">5</span>'),
                #     Div('project_name', css_class='col-md-5'),
                #     HTML('<span class="badge-form badge-pill">6</span>'),
                #     Div('project_description', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form badge-pill">7</span>'),
                #     Div('implementing_partners', css_class='col-md-5'),
                #     HTML('<span class="badge-form badge-pill">8</span>'),
                #     Div('focal_point', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form badge-pill">9</span>'),
                #     Div('start_date', css_class='col-md-5'),
                #     HTML('<span class="badge-form-2 badge-pill">11</span>'),
                #     Div('end_date', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form-2 badge-pill">11</span>'),
                #     Div('comment', css_class='col-md-10'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form-2 badge-pill">12</span>'),
                #     Div('plan', css_class='col-md-5'),
                #     HTML('<span class="badge-form-2 badge-pill">13</span>'),
                #     Div('sectors', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                # Div(
                #     HTML('<span class="badge-form-2 badge-pill">14</span>'),
                #     Div('project_type', css_class='col-md-5'),
                #     HTML('<span class="badge-form-2 badge-pill">15</span>'),
                #     Div('public_institution_support', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('governorates', css_class='col-md-5  multiple-checbkoxes'),
                    css_class='row card-body'
                ),
                # Div(
                #     HTML('<span class="badge-form-2 badge-pill">17</span>'),
                #     Div('budget', css_class='col-md-5'),
                #     HTML('<span class="badge-form-2 badge-pill">18</span>'),
                #     Div('cash_assistance', css_class='col-md-5'),
                #     css_class='row card-body'
                # ),
        #     # population_groups
        #         Div(
        #             HTML('<span class="badge-form-2 badge-pill">20</span>'),
        #             Div('number_targeted_syrians', css_class='col-md-5'),
        #             css_class='row card-body'
        #         ),
        #         Div(
        #             HTML('<span class="badge-form-2 badge-pill">21</span>'),
        #             Div('number_targeted_lebanese', css_class='col-md-5'),
        #             css_class='row card-body'
        #         ),
        #         Div(
        #             HTML('<span class="badge-form-2 badge-pill">22</span>'),
        #             Div('number_targeted_prl', css_class='col-md-5'),
        #             css_class='row card-body'
        #         ),
        #         Div(
        #             HTML('<span class="badge-form-2 badge-pill">23</span>'),
        #             Div('number_targeted_prs', css_class='col-md-5'),
        #             css_class='row card-body'
        #         ),
        #     # master_programs
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                # HTML(
                #     '<a type="reset" name="cancel" class="btn btn-inverse btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning" id="cancel-id-cancel" href="/youth/Child-Registration-Cancel/{}/">Cancel</a>'.format(
                #         registry)
                # ),

            ),
        )

    def save(self, request=None, instance=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = ProgramDocument.objects.create()
        else:
            instance = ProgramDocument.objects.get(id=instance)

        instance.partner_id = validated_data.get('partner')

        # Save the instance to ensure it has an ID
        instance.save()

        # Assign the governorates from the form data
        governorates_ids = validated_data.getlist('governorates')
        governorates = Location.objects.filter(id__in=governorates_ids)
        instance.governorates.set(governorates)

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance


    class Meta:
        model = ProgramDocument
        fields = (
            'partner',
            'governorates',
            # 'dropout_date',
            # 'master_program',
            # 'sub_program',
            # 'registration_date',
            # 'completion_date',
        )


class ProgramDocumentForm(forms.ModelForm):
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all(), widget=forms.Select,
        label=_('Partner'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    governorates = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label=_('Governorate of Coverage'),
        required=False
    )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        instance = kwargs.pop('instance', None)

        super(ProgramDocumentForm, self).__init__(*args, **kwargs)

        form_action = reverse('youth:program_program_document_add')
        if instance:
            form_action = reverse('youth:program_program_document_edit',
                                  kwargs={'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('partner', css_class='col-md-5'),
                    css_class='row card-body'
                ),

                Div(
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('governorates', css_class='col-md-5  multiple-checbkoxes'),
                    css_class='row card-body'
                ),

                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),

            ),
        )

    def save(self, request=None, instance=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = ProgramDocument.objects.create()
        else:
            instance = ProgramDocument.objects.get(id=instance)

        instance.partner_id = validated_data.get('partner')

        # Save the instance to ensure it has an ID
        instance.save()

        # Assign the governorates from the form data
        governorates_ids = validated_data.getlist('governorates')
        governorates = Location.objects.filter(id__in=governorates_ids)
        instance.governorates.set(governorates)

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance


    class Meta:
        model = ProgramDocument
        fields = (
            'partner',
            'governorates',
        )


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True

