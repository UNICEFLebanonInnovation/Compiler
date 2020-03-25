from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.forms import modelformset_factory
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import  render
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, ButtonHolder

from .models import School, PartnerOrganization, EducationYear, Evaluation


class ProfileForm(forms.ModelForm):

    email = forms.EmailField(
        label=_('School email'),
        widget=forms.TextInput(attrs={'placeholder': 'Format: school@email.com'})
    )
    land_phone_number = forms.RegexField(
        label=_('School land phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    fax_number = forms.RegexField(
        label=_('School fax number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    director_phone_number = forms.RegexField(
        label=_('School director cell phone'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    it_phone_number = forms.RegexField(
        label=_('School IT phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )

    academic_year_start = forms.DateField(
        label=_('School year start date'),
        widget=forms.TextInput,
        required=True
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
                    Div('coordinator', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">12</span>'),
                    Div('is_2nd_shift', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">13</span>'),
                    Div('is_alp', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">14</span>'),
                    Div('number_students_2nd_shift', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">15</span>'),
                    Div('number_students_alp', css_class='col-md-3'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Bank Accounts Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('iban_base1', css_class='col-md-5'),

                    HTML('<span class="badge badge-default">2</span>'),
                    Div('bank_Base1', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">3</span>'),
                    Div('branch_base1', css_class='col-md-3'),
                    css_class='row',
                ),
                Div(
                    HTML('<span class="badge badge-default">4</span>'),
                    Div('iban_base2', css_class='col-md-5'),

                    HTML('<span class="badge badge-default">5</span>'),
                    Div('bank_Base2', css_class='col-md-3'),
                    HTML('<span class="badge badge-default">6</span>'),
                    Div('branch_base2', css_class='col-md-3'),
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
            #'field_coordinator_name',
            'coordinator',
            'fax_number',
            'email',
            'certified_foreign_language',
            'comments',
            'weekend',
            'is_2nd_shift',
            'is_alp',
            'number_students_2nd_shift',
            'number_students_alp',
            'bank_Base1',
            'branch_base1',
            'iban_base1',
            'bank_Base2',
            'branch_base2',
            'iban_base2',
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


class EvaluationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:evaluation', kwargs={})
        self.fields['implemented_de_prep'].label = ''
        self.fields['reasons_no_de_prep'].label = False

        self.fields['implemented_de'].label = ''
        self.fields['reasons_no_de'].label = False

        self.fields['implemented_de_2'].label = ''
        self.fields['reasons_no_de_2'].label = False

        self.fields['implemented_de_3'].label = ''
        self.fields['reasons_no_de_3'].label = False

        self.fields['implemented_de_9'].label = ''
        self.fields['reasons_no_de_9'].label = False

        self.fields['implemented_de_prep'].label = ''
        self.fields['reasons_no_de_prep'].label = False

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span class="badge badge-default">1</span>'),
                    Div('total_teaching_days', css_class='col-md-4'),
                    Div('total_teaching_days_tillnow', css_class='col-md-4'),
                    css_class='row',
                    style="background: #E3F2FC;",
                ),
                css_class='bd-callout bd-callout-warning'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>'+_('Evaluation for Prep-Ece')+'</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_cprep" pk=' +
                         str(self.instance.id) + ' %}>' + _('Prep-Ece') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_prep', css_class='col-md-3', id='implemented-de-prep'),
                            css_class='row',
                        ),
                        Div(
                            Div('reasons_no_de_prep', css_class='col-md-10', id='reasons-no-de-prep'),
                            css_class='row',

                        ),
                        css_class='bd-callout bd-callout-warning',
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">2</span>'),
                            Div('steps_de_prep', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">3</span>'),
                            Div('challenges_de_prep', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">4</span>'),
                            Div('evaluate_steps_de_prep', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #F8FAFC;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cylce 1') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c1" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 1') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 2') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c3" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 3') + '  </a></div>'),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de', css_class='col-md-3'),
                            Div('reasons_no_de', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">2</span>'),
                            Div('steps_de', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">3</span>'),
                            Div('challenges_de', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">4</span>'),
                            Div('evaluate_steps_de', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #FDFFD8;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cycle 2') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c4" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 4') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c5" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 5') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c6" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 6') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_2', css_class='col-md-3'),
                            Div('reasons_no_de_2', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">2</span>'),
                            Div('steps_de_2', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">3</span>'),
                            Div('challenges_de_2', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">4</span>'),
                            Div('evaluate_steps_de_2', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #F8FAFC;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cycle 3') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c7" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 7') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c8" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 8') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_3', css_class='col-md-3'),
                            Div('reasons_no_de_3', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">2</span>'),
                            Div('steps_de_3', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">3</span>'),
                            Div('challenges_de_3', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge badge-default">4</span>'),
                            Div('evaluate_steps_de_3', css_class='col-md-10'),
                            css_class='row',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    style="background: #FDFFD8;",
                ),
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Grade 9') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c9" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 9') + '  </a></div>'),
                    css_class='bd-callout bd-callout-warning'
                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">1</span>'),
                        HTML(_('Have you implemented distance education ?')),
                        Div('implemented_de_9', css_class='col-md-3'),
                        Div('reasons_no_de_9', css_class='col-md-10'),
                        css_class='row',
                    ),
                    css_class='bd-callout bd-callout-warning'

                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">2</span>'),
                        Div('steps_de_9', css_class='col-md-10'),
                        css_class='row',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">3</span>'),
                        Div('challenges_de_9', css_class='col-md-10'),
                        css_class='row',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),

                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge badge-default">4</span>'),
                        Div('evaluate_steps_de_9', css_class='col-md-10'),
                        css_class='row',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                style="background: #F8FAFC;",
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span class="badge badge-default">2</span>'),
                    Div('other_notes_de', css_class='col-md-10'),
                    css_class='row',
                    style="background: #E3F2FC;",
                ),
            ),
            FormActions(
                Submit('save', _('Save')),
            ),
        )

    def save(self, instance=None, request=None):
        instance = super(EvaluationForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Evaluation
        fields = ('total_teaching_days', 'total_teaching_days_tillnow', 'implemented_de', 'reasons_no_de', 'challenges_de', 'steps_de',
                  'evaluate_steps_de', 'other_notes_de',
                  'implemented_de_2', 'reasons_no_de_2', 'challenges_de_2', 'steps_de_2', 'evaluate_steps_de_2',
                  'implemented_de_3', 'reasons_no_de_3', 'challenges_de_3', 'steps_de_3', 'evaluate_steps_de_3',
                  'implemented_de_9', 'reasons_no_de_9', 'challenges_de_9', 'steps_de_9', 'evaluate_steps_de_9',
                  'implemented_de_prep', 'reasons_no_de_prep', 'challenges_de_prep', 'steps_de_prep', 'evaluate_steps_de_prep',
                  )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class Classroom_Form(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c2_eng_completed'].label = False
        self.fields['c2_eng_completed_de'].label = False
        self.fields['c2_eng_remaining_de'].label = False
        self.fields['c2_fr_completed'].label = False
        self.fields['c2_fr_completed_de'].label = False
        self.fields['c2_fr_remaining_de'].label = False
        self.fields['c2_math_completed'].label = False
        self.fields['c2_math_completed_de'].label = False
        self.fields['c2_math_remaining_de'].label = False
        self.fields['c2_sc_completed'].label = False
        self.fields['c2_sc_completed_de'].label = False
        self.fields['c2_sc_remaining_de'].label = False
        self.fields['c2_ara_completed'].label = False
        self.fields['c2_ara_completed_de'].label = False
        self.fields['c2_ara_remaining_de'].label = False
        self.fields['c2_civic_completed'].label = False
        self.fields['c2_civic_completed_de'].label = False
        self.fields['c2_civic_remaining_de'].label = False
        self.fields['c2_geo_completed'].label = False
        self.fields['c2_geo_completed_de'].label = False
        self.fields['c2_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),


                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 2') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c2_eng_completed', 'c2_eng_completed_de', 'c2_eng_remaining_de',
                      'c2_fr_completed', 'c2_fr_completed_de', 'c2_fr_remaining_de',
                      'c2_math_completed', 'c2_math_completed_de', 'c2_math_remaining_de',
                      'c2_sc_completed', 'c2_sc_completed_de', 'c2_sc_remaining_de',
                      'c2_ara_completed', 'c2_ara_completed_de', 'c2_ara_remaining_de',
                      'c2_civic_completed', 'c2_civic_completed_de', 'c2_civic_remaining_de',
                      'c2_geo_completed', 'c2_geo_completed_de', 'c2_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c1(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c1, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c1_eng_completed'].label = False
        self.fields['c1_eng_completed_de'].label = False
        self.fields['c1_eng_remaining_de'].label = False
        self.fields['c1_fr_completed'].label = False
        self.fields['c1_fr_completed_de'].label = False
        self.fields['c1_fr_remaining_de'].label = False
        self.fields['c1_math_completed'].label = False
        self.fields['c1_math_completed_de'].label = False
        self.fields['c1_math_remaining_de'].label = False
        self.fields['c1_sc_completed'].label = False
        self.fields['c1_sc_completed_de'].label = False
        self.fields['c1_sc_remaining_de'].label = False
        self.fields['c1_ara_completed'].label = False
        self.fields['c1_ara_completed_de'].label = False
        self.fields['c1_ara_remaining_de'].label = False
        self.fields['c1_civic_completed'].label = False
        self.fields['c1_civic_completed_de'].label = False
        self.fields['c1_civic_remaining_de'].label = False
        self.fields['c1_geo_completed'].label = False
        self.fields['c1_geo_completed_de'].label = False
        self.fields['c1_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 1') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label > <font color="navy" size="3" >' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c1, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c1_eng_completed', 'c1_eng_completed_de', 'c1_eng_remaining_de',
                      'c1_fr_completed', 'c1_fr_completed_de', 'c1_fr_remaining_de',
                      'c1_math_completed', 'c1_math_completed_de', 'c1_math_remaining_de',
                      'c1_sc_completed', 'c1_sc_completed_de', 'c1_sc_remaining_de',
                      'c1_ara_completed', 'c1_ara_completed_de', 'c1_ara_remaining_de',
                      'c1_civic_completed', 'c1_civic_completed_de', 'c1_civic_remaining_de',
                      'c1_geo_completed', 'c1_geo_completed_de', 'c1_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c3(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c3, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c3_eng_completed'].label = False
        self.fields['c3_eng_completed_de'].label = False
        self.fields['c3_eng_remaining_de'].label = False
        self.fields['c3_fr_completed'].label = False
        self.fields['c3_fr_completed_de'].label = False
        self.fields['c3_fr_remaining_de'].label = False
        self.fields['c3_math_completed'].label = False
        self.fields['c3_math_completed_de'].label = False
        self.fields['c3_math_remaining_de'].label = False
        self.fields['c3_sc_completed'].label = False
        self.fields['c3_sc_completed_de'].label = False
        self.fields['c3_sc_remaining_de'].label = False
        self.fields['c3_ara_completed'].label = False
        self.fields['c3_ara_completed_de'].label = False
        self.fields['c3_ara_remaining_de'].label = False
        self.fields['c3_civic_completed'].label = False
        self.fields['c3_civic_completed_de'].label = False
        self.fields['c3_civic_remaining_de'].label = False
        self.fields['c3_geo_completed'].label = False
        self.fields['c3_geo_completed_de'].label = False
        self.fields['c3_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 3') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c3, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c3_eng_completed', 'c3_eng_completed_de', 'c3_eng_remaining_de',
                      'c3_fr_completed', 'c3_fr_completed_de', 'c3_fr_remaining_de',
                      'c3_math_completed', 'c3_math_completed_de', 'c3_math_remaining_de',
                      'c3_sc_completed', 'c3_sc_completed_de', 'c3_sc_remaining_de',
                      'c3_ara_completed', 'c3_ara_completed_de', 'c3_ara_remaining_de',
                      'c3_civic_completed', 'c3_civic_completed_de', 'c3_civic_remaining_de',
                      'c3_geo_completed', 'c3_geo_completed_de', 'c3_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c4(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c4, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c4_eng_completed'].label = False
        self.fields['c4_eng_completed_de'].label = False
        self.fields['c4_eng_remaining_de'].label = False
        self.fields['c4_fr_completed'].label = False
        self.fields['c4_fr_completed_de'].label = False
        self.fields['c4_fr_remaining_de'].label = False
        self.fields['c4_math_completed'].label = False
        self.fields['c4_math_completed_de'].label = False
        self.fields['c4_math_remaining_de'].label = False
        self.fields['c4_sc_completed'].label = False
        self.fields['c4_sc_completed_de'].label = False
        self.fields['c4_sc_remaining_de'].label = False
        self.fields['c4_ara_completed'].label = False
        self.fields['c4_ara_completed_de'].label = False
        self.fields['c4_ara_remaining_de'].label = False
        self.fields['c4_civic_completed'].label = False
        self.fields['c4_civic_completed_de'].label = False
        self.fields['c4_civic_remaining_de'].label = False
        self.fields['c4_geo_completed'].label = False
        self.fields['c4_geo_completed_de'].label = False
        self.fields['c4_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 4') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c4, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c4_eng_completed', 'c4_eng_completed_de', 'c4_eng_remaining_de',
                      'c4_fr_completed', 'c4_fr_completed_de', 'c4_fr_remaining_de',
                      'c4_math_completed', 'c4_math_completed_de', 'c4_math_remaining_de',
                      'c4_sc_completed', 'c4_sc_completed_de', 'c4_sc_remaining_de',
                      'c4_ara_completed', 'c4_ara_completed_de', 'c4_ara_remaining_de',
                      'c4_civic_completed', 'c4_civic_completed_de', 'c4_civic_remaining_de',
                      'c4_geo_completed', 'c4_geo_completed_de', 'c4_geo_remaining_de',
                      'owner', 'school', 'education_year', 'total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c5(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c5, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c5_eng_completed'].label = False
        self.fields['c5_eng_completed_de'].label = False
        self.fields['c5_eng_remaining_de'].label = False
        self.fields['c5_fr_completed'].label = False
        self.fields['c5_fr_completed_de'].label = False
        self.fields['c5_fr_remaining_de'].label = False
        self.fields['c5_math_completed'].label = False
        self.fields['c5_math_completed_de'].label = False
        self.fields['c5_math_remaining_de'].label = False
        self.fields['c5_sc_completed'].label = False
        self.fields['c5_sc_completed_de'].label = False
        self.fields['c5_sc_remaining_de'].label = False
        self.fields['c5_ara_completed'].label = False
        self.fields['c5_ara_completed_de'].label = False
        self.fields['c5_ara_remaining_de'].label = False
        self.fields['c5_civic_completed'].label = False
        self.fields['c5_civic_completed_de'].label = False
        self.fields['c5_civic_remaining_de'].label = False
        self.fields['c5_geo_completed'].label = False
        self.fields['c5_geo_completed_de'].label = False
        self.fields['c5_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 5') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c5, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c5_eng_completed', 'c5_eng_completed_de', 'c5_eng_remaining_de',
                      'c5_fr_completed', 'c5_fr_completed_de', 'c5_fr_remaining_de',
                      'c5_math_completed', 'c5_math_completed_de', 'c5_math_remaining_de',
                      'c5_sc_completed', 'c5_sc_completed_de', 'c5_sc_remaining_de',
                      'c5_ara_completed', 'c5_ara_completed_de', 'c5_ara_remaining_de',
                      'c5_civic_completed', 'c5_civic_completed_de', 'c5_civic_remaining_de',
                      'c5_geo_completed', 'c5_geo_completed_de', 'c5_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c6(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c6, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c6_eng_completed'].label = False
        self.fields['c6_eng_completed_de'].label = False
        self.fields['c6_eng_remaining_de'].label = False
        self.fields['c6_fr_completed'].label = False
        self.fields['c6_fr_completed_de'].label = False
        self.fields['c6_fr_remaining_de'].label = False
        self.fields['c6_math_completed'].label = False
        self.fields['c6_math_completed_de'].label = False
        self.fields['c6_math_remaining_de'].label = False
        self.fields['c6_sc_completed'].label = False
        self.fields['c6_sc_completed_de'].label = False
        self.fields['c6_sc_remaining_de'].label = False
        self.fields['c6_ara_completed'].label = False
        self.fields['c6_ara_completed_de'].label = False
        self.fields['c6_ara_remaining_de'].label = False
        self.fields['c6_civic_completed'].label = False
        self.fields['c6_civic_completed_de'].label = False
        self.fields['c6_civic_remaining_de'].label = False
        self.fields['c6_geo_completed'].label = False
        self.fields['c6_geo_completed_de'].label = False
        self.fields['c6_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 6') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c6, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c6_eng_completed', 'c6_eng_completed_de', 'c6_eng_remaining_de',
                      'c6_fr_completed', 'c6_fr_completed_de', 'c6_fr_remaining_de',
                      'c6_math_completed', 'c6_math_completed_de', 'c6_math_remaining_de',
                      'c6_sc_completed', 'c6_sc_completed_de', 'c6_sc_remaining_de',
                      'c6_ara_completed', 'c6_ara_completed_de', 'c6_ara_remaining_de',
                      'c6_civic_completed', 'c6_civic_completed_de', 'c6_civic_remaining_de',
                      'c6_geo_completed', 'c6_geo_completed_de', 'c6_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c7(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c7, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c7_eng_completed'].label = False
        self.fields['c7_eng_completed_de'].label = False
        self.fields['c7_eng_remaining_de'].label = False
        self.fields['c7_fr_completed'].label = False
        self.fields['c7_fr_completed_de'].label = False
        self.fields['c7_fr_remaining_de'].label = False
        self.fields['c7_math_completed'].label = False
        self.fields['c7_math_completed_de'].label = False
        self.fields['c7_math_remaining_de'].label = False
        self.fields['c7_sc_completed'].label = False
        self.fields['c7_sc_completed_de'].label = False
        self.fields['c7_sc_remaining_de'].label = False
        self.fields['c7_ara_completed'].label = False
        self.fields['c7_ara_completed_de'].label = False
        self.fields['c7_ara_remaining_de'].label = False
        self.fields['c7_civic_completed'].label = False
        self.fields['c7_civic_completed_de'].label = False
        self.fields['c7_civic_remaining_de'].label = False
        self.fields['c7_geo_completed'].label = False
        self.fields['c7_geo_completed_de'].label = False
        self.fields['c7_geo_remaining_de'].label = False

        self.fields['c7_his_completed'].label = False
        self.fields['c7_his_completed_de'].label = False
        self.fields['c7_his_remaining_de'].label = False

        self.fields['c7_che_completed'].label = False
        self.fields['c7_che_completed_de'].label = False
        self.fields['c7_che_remaining_de'].label = False

        self.fields['c7_phy_completed'].label = False
        self.fields['c7_phy_completed_de'].label = False
        self.fields['c7_phy_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 7') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c7, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c7_eng_completed', 'c7_eng_completed_de', 'c7_eng_remaining_de',
                      'c7_fr_completed', 'c7_fr_completed_de', 'c7_fr_remaining_de',
                      'c7_math_completed', 'c7_math_completed_de', 'c7_math_remaining_de',
                      'c7_sc_completed', 'c7_sc_completed_de', 'c7_sc_remaining_de',
                      'c7_ara_completed', 'c7_ara_completed_de', 'c7_ara_remaining_de',
                      'c7_civic_completed', 'c7_civic_completed_de', 'c7_civic_remaining_de',
                      'c7_geo_completed', 'c7_geo_completed_de', 'c7_geo_remaining_de',
                      'c7_his_completed', 'c7_his_completed_de', 'c7_his_remaining_de',
                      'c7_che_completed', 'c7_che_completed_de', 'c7_che_remaining_de',
                      'c7_phy_completed', 'c7_phy_completed_de', 'c7_phy_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c8(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c8, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c8_eng_completed'].label = False
        self.fields['c8_eng_completed_de'].label = False
        self.fields['c8_eng_remaining_de'].label = False
        self.fields['c8_fr_completed'].label = False
        self.fields['c8_fr_completed_de'].label = False
        self.fields['c8_fr_remaining_de'].label = False
        self.fields['c8_math_completed'].label = False
        self.fields['c8_math_completed_de'].label = False
        self.fields['c8_math_remaining_de'].label = False
        self.fields['c8_sc_completed'].label = False
        self.fields['c8_sc_completed_de'].label = False
        self.fields['c8_sc_remaining_de'].label = False
        self.fields['c8_ara_completed'].label = False
        self.fields['c8_ara_completed_de'].label = False
        self.fields['c8_ara_remaining_de'].label = False
        self.fields['c8_civic_completed'].label = False
        self.fields['c8_civic_completed_de'].label = False
        self.fields['c8_civic_remaining_de'].label = False
        self.fields['c8_geo_completed'].label = False
        self.fields['c8_geo_completed_de'].label = False
        self.fields['c8_geo_remaining_de'].label = False
        self.fields['c8_his_completed'].label = False
        self.fields['c8_his_completed_de'].label = False
        self.fields['c8_his_remaining_de'].label = False

        self.fields['c8_che_completed'].label = False
        self.fields['c8_che_completed_de'].label = False
        self.fields['c8_che_remaining_de'].label = False

        self.fields['c8_phy_completed'].label = False
        self.fields['c8_phy_completed_de'].label = False
        self.fields['c8_phy_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 8') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c8, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c8_eng_completed', 'c8_eng_completed_de', 'c8_eng_remaining_de',
                      'c8_fr_completed', 'c8_fr_completed_de', 'c8_fr_remaining_de',
                      'c8_math_completed', 'c8_math_completed_de', 'c8_math_remaining_de',
                      'c8_sc_completed', 'c8_sc_completed_de', 'c8_sc_remaining_de',
                      'c8_ara_completed', 'c8_ara_completed_de', 'c8_ara_remaining_de',
                      'c8_civic_completed', 'c8_civic_completed_de', 'c8_civic_remaining_de',
                      'c8_geo_completed', 'c8_geo_completed_de', 'c8_geo_remaining_de',
                      'c8_his_completed', 'c8_his_completed_de', 'c8_his_remaining_de',
                      'c8_che_completed', 'c8_che_completed_de', 'c8_che_remaining_de',
                      'c8_phy_completed', 'c8_phy_completed_de', 'c8_phy_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c9(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c9, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c9_eng_completed'].label = False
        self.fields['c9_eng_completed_de'].label = False
        self.fields['c9_eng_remaining_de'].label = False
        self.fields['c9_fr_completed'].label = False
        self.fields['c9_fr_completed_de'].label = False
        self.fields['c9_fr_remaining_de'].label = False
        self.fields['c9_math_completed'].label = False
        self.fields['c9_math_completed_de'].label = False
        self.fields['c9_math_remaining_de'].label = False
        self.fields['c9_sc_completed'].label = False
        self.fields['c9_sc_completed_de'].label = False
        self.fields['c9_sc_remaining_de'].label = False
        self.fields['c9_ara_completed'].label = False
        self.fields['c9_ara_completed_de'].label = False
        self.fields['c9_ara_remaining_de'].label = False
        self.fields['c9_civic_completed'].label = False
        self.fields['c9_civic_completed_de'].label = False
        self.fields['c9_civic_remaining_de'].label = False
        self.fields['c9_geo_completed'].label = False
        self.fields['c9_geo_completed_de'].label = False
        self.fields['c9_geo_remaining_de'].label = False
        self.fields['c9_his_completed'].label = False
        self.fields['c9_his_completed_de'].label = False
        self.fields['c9_his_remaining_de'].label = False

        self.fields['c9_che_completed'].label = False
        self.fields['c9_che_completed_de'].label = False
        self.fields['c9_che_remaining_de'].label = False

        self.fields['c9_phy_completed'].label = False
        self.fields['c9_phy_completed_de'].label = False
        self.fields['c9_phy_remaining_de'].label = False
        self.fields['c9_total_std'].label = False
        self.fields['c9_total_std_de'].label = False
        self.fields['c9_total_teachers'].label = False
        self.fields['c9_total_teachers_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 9') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                  None,
                ),
                Div(
                    HTML('<label> ' + _('Total of teachers') + '</label>'),
                    Div('c9_total_teachers', css_class='col-md-5'),
                    css_class='row',
                ),
                Div(
                    HTML('<label> ' + _('Number of teachers who have committed to distance education') + '</label>'),
                    Div('c9_total_teachers_de', css_class='col-md-5'),
                    css_class='row',
                ),
                Div(
                  HTML('<label> '+_('Total of students')+'</label>'),
                  Div('c9_total_std', css_class='col-md-4'),
                  css_class='row',
                ),
                Div(
                    HTML('<label> ' + _('Total of students they follow distance education') + '</label>'),
                    Div('c9_total_std_de', css_class='col-md-4'),
                    css_class='row',
                ),

                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c9, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c9_eng_completed', 'c9_eng_completed_de', 'c9_eng_remaining_de',
                      'c9_fr_completed', 'c9_fr_completed_de', 'c9_fr_remaining_de',
                      'c9_math_completed', 'c9_math_completed_de', 'c9_math_remaining_de',
                      'c9_sc_completed', 'c9_sc_completed_de', 'c9_sc_remaining_de',
                      'c9_ara_completed', 'c9_ara_completed_de', 'c9_ara_remaining_de',
                      'c9_civic_completed', 'c9_civic_completed_de', 'c9_civic_remaining_de',
                      'c9_geo_completed', 'c9_geo_completed_de', 'c9_geo_remaining_de',
                      'c9_his_completed', 'c9_his_completed_de', 'c9_his_remaining_de',
                      'c9_che_completed', 'c9_che_completed_de', 'c9_che_remaining_de',
                      'c9_phy_completed', 'c9_phy_completed_de', 'c9_phy_remaining_de',
                      'c9_total_std', 'c9_total_std_de',
                      'c9_total_teachers', 'c9_total_teachers_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_cprep(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_cprep, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['cprep_eng_completed'].label = False
        self.fields['cprep_eng_completed_de'].label = False
        self.fields['cprep_eng_remaining_de'].label = False
        self.fields['cprep_fr_completed'].label = False
        self.fields['cprep_fr_completed_de'].label = False
        self.fields['cprep_fr_remaining_de'].label = False
        self.fields['cprep_math_completed'].label = False
        self.fields['cprep_math_completed_de'].label = False
        self.fields['cprep_math_remaining_de'].label = False
        self.fields['cprep_sc_completed'].label = False
        self.fields['cprep_sc_completed_de'].label = False
        self.fields['cprep_sc_remaining_de'].label = False
        self.fields['cprep_ara_completed'].label = False
        self.fields['cprep_ara_completed_de'].label = False
        self.fields['cprep_ara_remaining_de'].label = False
        self.fields['cprep_civic_completed'].label = False
        self.fields['cprep_civic_completed_de'].label = False
        self.fields['cprep_civic_remaining_de'].label = False
        self.fields['cprep_geo_completed'].label = False
        self.fields['cprep_geo_completed_de'].label = False
        self.fields['cprep_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    css_class='row',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade Prep-Ece') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge badge-default">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_cprep, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('cprep_eng_completed', 'cprep_eng_completed_de', 'cprep_eng_remaining_de',
                      'cprep_fr_completed', 'cprep_fr_completed_de', 'cprep_fr_remaining_de',
                      'cprep_math_completed', 'cprep_math_completed_de', 'cprep_math_remaining_de',
                      'cprep_sc_completed', 'cprep_sc_completed_de', 'cprep_sc_remaining_de',
                      'cprep_ara_completed', 'cprep_ara_completed_de', 'cprep_ara_remaining_de',
                      'cprep_civic_completed', 'cprep_civic_completed_de', 'cprep_civic_remaining_de',
                      'cprep_geo_completed', 'cprep_geo_completed_de', 'cprep_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()
