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
from dal import autocomplete

from .models import (
    Registration,
    EnrolledPrograms,
    YES_NO,
    MasterProgram,
    SubProgram,
    Donor,
    ProgramDocument,
    PartnerOrganization,
    FundedBy,
    FocalPoint,
    Plan,
    Sector,
    ProjectType,
    PopulationGroups,
    ProjectStatus,
)
from student_registration.locations.models import Location
from student_registration.users.templatetags.custom_tags import has_group


def _name_en_label(obj):
    return getattr(obj, "name_en", None) or getattr(obj, "name", str(obj))


class EnrolledProgramsForm(forms.ModelForm):
    dropout_date = forms.DateField(
        label=_("Please Specify dropout date from school"),
        required=False
    )
    registration_date = forms.DateField(
        label=_("Date of registration"),
        required=True
    )
    completion_date = forms.DateField(
        label=_("Date of completion"),
        required=False
    )
    donor = forms.ModelChoiceField(
        queryset=Donor.objects.filter(active=True),
        widget=forms.Select,
        label=_('Donor'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    program_document = forms.ModelChoiceField(
        queryset=ProgramDocument.objects.all(),
        widget=forms.Select,
        label=_('Program Document'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    master_program = forms.ModelChoiceField(
        queryset=MasterProgram.objects.all(),
        widget=forms.Select,
        label=_('Master Indicator'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    sub_program = forms.ModelChoiceField(
        queryset=SubProgram.objects.all(), widget=forms.Select,
        label=_('Sub Indicator'),
        empty_label='-------',
        required=True, to_field_name='id',
    )

    same_location = forms.BooleanField(
        label=_('Same location'),
        required=False,
        initial=True,
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=False, to_field_name='id',
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False),
        widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=False, to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False),
        widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=False, to_field_name='id',
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(EnrolledProgramsForm, self).__init__(*args, **kwargs)

        for field_name in ['governorate', 'district', 'cadaster']:
            if field_name in self.fields:
                self.fields[field_name].label_from_instance = _name_en_label

        self.fields['registration_id'].initial = registry

        registration_obj = None
        if registry:
            registration_obj = Registration.objects.filter(id=registry).select_related('adolescent').first()

        if self.data:
            same_location = self.data.get('same_location') in ['on', 'True', 'true', True, '1']
        else:
            same_location = self.initial.get('same_location', True)
        self.fields['same_location'].initial = same_location

        gov_initial = self.initial.get('governorate')
        dist_initial = self.initial.get('district')
        cad_initial = self.initial.get('cadaster')
        if registration_obj and registration_obj.adolescent:
            reg_gov = registration_obj.adolescent.governorate_id
            reg_dist = registration_obj.adolescent.district_id
            reg_cad = registration_obj.adolescent.cadaster_id
            if same_location:
                gov_initial = reg_gov
                dist_initial = reg_dist
                cad_initial = reg_cad
                self.fields['governorate'].widget.attrs['disabled'] = 'disabled'
                self.fields['district'].widget.attrs['disabled'] = 'disabled'
                self.fields['cadaster'].widget.attrs['disabled'] = 'disabled'
            else:
                if not gov_initial:
                    gov_initial = reg_gov
                if not dist_initial:
                    dist_initial = reg_dist
                if not cad_initial:
                    cad_initial = reg_cad

        self.fields['governorate'].initial = gov_initial
        self.fields['district'].initial = dist_initial
        self.fields['cadaster'].initial = cad_initial

        gov_id = self.data.get('governorate') or self.fields['governorate'].initial
        if gov_id:
            self.fields['district'].queryset = Location.objects.filter(parent_id=gov_id).order_by('name')
        else:
            self.fields['district'].queryset = Location.objects.none()

        dist_id = self.data.get('district') or self.fields['district'].initial
        if dist_id:
            self.fields['cadaster'].queryset = Location.objects.filter(parent_id=dist_id).order_by('name')
        else:
            self.fields['cadaster'].queryset = Location.objects.none()

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
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('same_location', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body'
                ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                HTML(
                    '<a type="reset" name="cancel" class="btn btn-inverse btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning" id="cancel-id-cancel" href="/youth/child-profile/{}/">Cancel</a>'.format(
                        registry)
                )
            ),
            css_id='step-1'
        )
        )

    def save(self, request=None, instance=None, registry=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = EnrolledPrograms.objects.create(registration_id=registry)
        else:
            instance = EnrolledPrograms.objects.get(id=instance)

        dropout_date_str = validated_data.get('dropout_date')
        if dropout_date_str:
            dropout_date = datetime.strptime(dropout_date_str, '%Y-%m-%d')
            instance.dropout_date = dropout_date
        instance.master_program_id = validated_data.get('master_program')
        instance.sub_program_id = validated_data.get('sub_program')
        instance.donor_id = validated_data.get('donor')
        instance.program_document_id = validated_data.get('program_document')

        same_location = validated_data.get('same_location')
        instance.same_location = True if same_location in ['on', 'True', 'true', True, '1'] else False

        gov_id = validated_data.get('governorate')
        dist_id = validated_data.get('district')
        cad_id = validated_data.get('cadaster')

        if instance.same_location and (not gov_id or not dist_id or not cad_id):
            if registry:
                reg_obj = Registration.objects.filter(id=registry).select_related('adolescent').first()
                if reg_obj and reg_obj.adolescent:
                    gov_id = reg_obj.adolescent.governorate_id
                    dist_id = reg_obj.adolescent.district_id
                    cad_id = reg_obj.adolescent.cadaster_id

        instance.governorate_id = gov_id
        instance.district_id = dist_id
        instance.cadaster_id = cad_id

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

    def clean(self):
        cleaned_data = super(EnrolledProgramsForm, self).clean()
        registration_date = cleaned_data.get("registration_date")
        completion_date = cleaned_data.get("completion_date")
        if registration_date and completion_date and registration_date > completion_date:
            self.add_error('registration_date', 'Registration Date must be less than Completion Date')

        same_location = cleaned_data.get('same_location')
        if not same_location:
            if not cleaned_data.get('governorate'):
                self.add_error('governorate', _('This field is required.'))
            if not cleaned_data.get('district'):
                self.add_error('district', _('This field is required.'))
            if not cleaned_data.get('cadaster'):
                self.add_error('cadaster', _('This field is required.'))

        return cleaned_data

    class Meta:
        model = EnrolledPrograms
        fields = (
            'registration_id',
            'dropout_date',
            'registration_date',
            'completion_date',
            'donor',
            'program_document',
            'master_program',
            'sub_program',
            'same_location',
            'governorate',
            'district',
            'cadaster',
        )


class ProgramDocumentForm(forms.ModelForm):
    partner = forms.ModelChoiceField(
        queryset=PartnerOrganization.objects.filter(is_youth=True),
        widget=forms.Select,
        label=_('Partner'),
        empty_label='-------',
        required=False, to_field_name='id',
    )
    funded_by = forms.ModelChoiceField(
        queryset=FundedBy.objects.all(), widget=forms.Select,
        label=_('Funded By'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    project_status = forms.ModelChoiceField(
        queryset=ProjectStatus.objects.all(), widget=forms.Select,
        label=_('Project Status'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    project_code = forms.CharField(
        label=_("Project Code"),
        widget=forms.TextInput, required=True
    )
    project_name = forms.CharField(
        label=_("Project Name"),
        widget=forms.TextInput, required=True
    )
    project_description = forms.CharField(
        label=_('Project Description'),
        widget=forms.Textarea, required=True
    )
    implementing_partners = forms.CharField(
        label=_("Key Implementing Partner(s)"),
        widget=forms.TextInput, required=True
    )
    focal_point = forms.ModelChoiceField(
        queryset=FocalPoint.objects.all(), widget=forms.Select,
        label=_('UNICEF Focal Point'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False
    )
    comment = forms.CharField(
        label=_('Comment'),
        widget=forms.Textarea, required=False
    )

    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(), widget=forms.Select,
        label=_('Plan'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    sectors = forms.ModelChoiceField(
        queryset=Sector.objects.all(), widget=forms.Select,
        label=_('SELECT SECTORS TARGETED BY THIS PROJECT'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    project_type = forms.ModelChoiceField(
        queryset=ProjectType.objects.all(), widget=forms.Select,
        label=_('Type of Project'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    public_institution_support = forms.ChoiceField(
        label=_("Support of Public Institution"),
        widget=forms.Select, required=True,
        choices=ProgramDocument.SUPPORT
    )
    governorates = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label=_('Governorate of Coverage'),
        required=False
    )
    budget = forms.FloatField(
        label=_('Please add the Project Budget in USD'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    cash_assistance = forms.ChoiceField(
        label=_("Does this Project have any Cash Assistance Component"),
        widget=forms.Select, required=True,
        choices=ProgramDocument.YES_NO
    )
    population_groups = forms.ModelMultipleChoiceField(
        queryset=PopulationGroups.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_('Population Groups Targeted'),
        required=False
    )
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
    donors = forms.ModelMultipleChoiceField(
        queryset=Donor.objects.filter(active=True),
        widget=forms.CheckboxSelectMultiple,
        label=_('Donors'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        instance = kwargs.pop('instance', None)
        self.instance_pk = None
        if isinstance(instance, ProgramDocument):
            self.instance_pk = instance.pk
            kwargs['instance'] = instance
        elif instance is not None:
            self.instance_pk = instance
            try:
                kwargs['instance'] = ProgramDocument.objects.get(pk=instance)
            except ProgramDocument.DoesNotExist:
                kwargs['instance'] = None


        super(ProgramDocumentForm, self).__init__(*args, **kwargs)

        if 'governorates' in self.fields:
            self.fields['governorates'].label_from_instance = _name_en_label

        form_action = reverse('youth:program_program_document_add')
        if instance:
            form_action = reverse('youth:program_program_document_edit',
                                  kwargs={'pk': instance})

        display_donor = has_group(self.request.user, 'YOUTH_UNICEF')
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if display_donor:
            self.fields['donors'].required = True
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('partner', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('funded_by', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('project_status', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('project_code', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('project_name', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('project_description', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('implementing_partners', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('focal_point', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('start_date', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('end_date', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('plan', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('sectors', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('project_type', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">14</span>'),
                        Div('public_institution_support', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('governorates', css_class='col-md-5  multiple-choice checkbox'),
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('comment', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('budget', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">18</span>'),
                        Div('cash_assistance', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">19</span>'),
                        Div('population_groups', css_class='col-md-10  multiple-choice checkbox'),
                        css_class='row card-body'
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    #     Div('number_targeted_syrians', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">21</span>'),
                    #     Div('number_targeted_lebanese', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">22</span>'),
                    #     Div('number_targeted_prl', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">23</span>'),
                    #     Div('number_targeted_prs', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    css_id='step-1'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('donors', css_class='col-md-6 multiple-choice-options checkbox'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    ),
                    css_id='step-2'
                )
            )
        else:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('partner', css_class='col-md-5 d-none'),
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('funded_by', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('project_status', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('project_code', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('project_name', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('project_description', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('implementing_partners', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('focal_point', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('start_date', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">9</span>'),
                        Div('end_date', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('plan', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('sectors', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('project_type', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('public_institution_support', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">14</span>'),
                        Div('governorates', css_class='col-md-5  multiple-choice checkbox'),
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('comment', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('budget', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('cash_assistance', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">18</span>'),
                        Div('population_groups', css_class='col-md-10  multiple-choice checkbox'),
                        css_class='row card-body'
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    #     Div('number_targeted_syrians', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">21</span>'),
                    #     Div('number_targeted_lebanese', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">22</span>'),
                    #     Div('number_targeted_prl', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">23</span>'),
                    #     Div('number_targeted_prs', css_class='col-md-5'),
                    #     css_class='row card-body'
                    # ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    ),
                    css_id='step-1'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('donors', css_class='col-md-6 multiple-choice-options checkbox'),
                        css_class='row card-body'
                    ),
                    css_id='step-2',
                    css_class='d-none'
                ),

            )



    def save(self, request=None, instance=None):
        from datetime import datetime
        validated_data = request.POST

        if not instance:
            instance = ProgramDocument.objects.create()
        else:
            instance = ProgramDocument.objects.get(id=instance)

        # Save the instance to ensure it has an ID
        instance.save()

        # handle blank string inputs
        def blank_int(value):
            return int(value) if value and value.isdigit() else None

        if has_group(self.request.user, 'YOUTH_UNICEF'):
            instance.partner_id = validated_data.get('partner')
        else:
            instance.partner = request.user.partner

        instance.funded_by_id = validated_data.get('funded_by')
        instance.project_status_id = validated_data.get('project_status')
        instance.project_code = validated_data.get('project_code')
        instance.project_name = validated_data.get('project_name')
        instance.project_description = validated_data.get('project_description')
        instance.implementing_partners = validated_data.get('implementing_partners')
        instance.focal_point_id = validated_data.get('focal_point')
        instance.start_date = None if validated_data.get('start_date') == '' else validated_data.get('start_date')
        instance.end_date = None if validated_data.get('end_date') == '' else validated_data.get('end_date')

        instance.comment = validated_data.get('comment')
        instance.plan_id = validated_data.get('plan')
        instance.sectors_id = validated_data.get('sectors')
        instance.project_type_id = validated_data.get('project_type')
        instance.public_institution_support = validated_data.get('public_institution_support')

        instance.budget = 0 if validated_data.get('budget') == '' else validated_data.get('budget')

        instance.cash_assistance = validated_data.get('cash_assistance')
        # instance.number_targeted_syrians = validated_data.get('number_targeted_syrians')
        # instance.number_targeted_lebanese = validated_data.get('number_targeted_lebanese')
        # instance.number_targeted_prl = validated_data.get('number_targeted_prl')
        # instance.number_targeted_prs = validated_data.get('number_targeted_prs')

        # Assign the governorates from the form data
        governorates_ids = validated_data.getlist('governorates')
        governorates = Location.objects.filter(id__in=governorates_ids)
        instance.governorates.set(governorates)

        # Assign the population_groups from the form data
        population_groups_ids = validated_data.getlist('population_groups')
        population_groups = PopulationGroups.objects.filter(id__in=population_groups_ids)
        instance.population_groups.set(population_groups)

        # Assign the donors from the form data
        donor_ids = validated_data.getlist('donors')
        donors = Donor.objects.filter(id__in=donor_ids)
        instance.donors.set(donors)

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(ProgramDocumentForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date >= end_date:
            self.add_error('start_date', 'Start Date must be less than End Date')

        project_code = cleaned_data.get('project_code')
        if project_code:
            project_code = project_code.strip()
            cleaned_data['project_code'] = project_code
            existing_code = ProgramDocument.objects.filter(
                project_code__iexact=project_code
            )
            instance_pk = self.instance_pk or getattr(self.instance, 'pk', None)
            if instance_pk:
                existing_code = existing_code.exclude(pk=instance_pk)
            if existing_code.exists():
                self.add_error(
                    'project_code',
                    _('A Program Document with this project code already exists.')
                )

        project_name = cleaned_data.get('project_name')
        if project_name:
            project_name = project_name.strip()
            cleaned_data['project_name'] = project_name
            existing_name = ProgramDocument.objects.filter(
                project_name__iexact=project_name
            )
            instance_pk = self.instance_pk or getattr(self.instance, 'pk', None)
            if instance_pk:
                existing_name = existing_name.exclude(pk=instance_pk)
            if existing_name.exists():
                self.add_error(
                    'project_name',
                    _('A Program Document with this project name already exists.')
                )

        return cleaned_data

    class Meta:
        model = ProgramDocument
        fields = (
            'partner',
            'governorates',
            'population_groups',
            # 'donors'
        )


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True

