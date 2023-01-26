from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.forms import inlineformset_factory,HiddenInput

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete


from student_registration.locations.models import Center
from .models import (
    YES_NO
)
from student_registration.schools.models import (
    School
)
from .utils import generate_services, generate_education_history
from .serializers import MainSerializer
from student_registration.mscc.templatetags.simple_tags import get_service

from datetime import date, datetime, timedelta
from .widgets import DatePickerInput
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild

from collections import OrderedDict
from django.template.loader import render_to_string


DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))


class MainAttendanceForm(forms.ModelForm):
    attendance_date = forms.DateField(
        initial=date.today,
        widget=DatePickerInput,
        label=_('Attendance date')
    )
    day_off = forms.ChoiceField(
        label=_("Day off ?"),
        widget=forms.Select, required=True,
        choices=MSCCAttendance.YES_NO
    )
    close_reason = forms.ChoiceField(
        label=_("Day off reason"),
        widget=forms.Select, required=False,
        choices=MSCCAttendance.CLOSE_REASON
    )

    def render_attendance_children(self, request, context):
        template_name = "mscc/attendance_children.html"
        return render_to_string(template_name, context)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        attendance_child_formset = kwargs.pop('attendance_child_formset', None)
        saveStage = kwargs.pop('saveStage', None)
        update_disabled = kwargs.pop('update_disabled', False)


        if update_disabled:
            load_children_button = Button('LoadChildrenButton', _('Load'), css_class='col-md-2 btn btn-info', disabled=True)
            submit_button = Submit('save', _('Save'), css_class='col-md-2', disabled=True)
        elif saveStage:
            load_children_button = Button('LoadChildrenButton', _('Load'), css_class='col-md-2 btn btn-info', disabled=True)
            submit_button = Submit('save', _('Save'), css_class='col-md-2')

        else:
            load_children_button = Button('LoadChildrenButton', _('Load'), css_class='col-md-2 btn btn-info')
            submit_button = Submit('save', _('Save'), css_class='col-md-2', disabled=True)

        attendance_children_context = {}
        if attendance_child_formset:
            attendance_children_context['attendance_child_formset'] = attendance_child_formset

        super(MainAttendanceForm, self).__init__(*args, **kwargs)
        form_action = reverse('mscc:attendance_main')
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Attendance') + '</h4>')

                ),
                Div(
                    Div('attendance_date', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                Div(
                    Div('day_off', css_class='col-md-3 form-group'),
                    Div('close_reason', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            HTML(self.render_attendance_children(self.request, attendance_children_context)),
            FormActions(
                        load_children_button,
                        HTML('<div class="space"></div>'),
                        submit_button,
                        HTML('<div class="space"></div>'),
                        css_class='button-group'
                    )
        )


    def clean(self):
        cleaned_data = super(MainAttendanceForm, self).clean()
        attendance_date = cleaned_data.get('attendance_date')

        # Make sure filters are provided
        if cleaned_data.get('day_off') == 'yes' and cleaned_data.get('close_reason') == '':
            self.add_error('close_reason', "The reason should be specified.")

        if self.instance.id is None:
            day_off = cleaned_data.get("day_off")

            center_id = 1
            if  attendance_date != '' and day_off != '':
                num_results = MSCCAttendance.objects.filter(
                                                           center_id=center_id,
                                                           attendance_date=attendance_date,
                                                           ).count()
                if num_results > 0:
                    self.add_error('attendance_date', "There is already an attendance record for this date.")
            if attendance_date != '':
                current_date = datetime.today().date()
                two_weeks_ago = current_date - timedelta(days=14)
                if not ((attendance_date <= current_date)
                        and (attendance_date >= two_weeks_ago)):
                    self.add_error('attendance_date', "Attendance date is not valid.")

    class Meta:
        model = MSCCAttendance
        fields = (
            'attendance_date',
            'day_off',
            'close_reason')


class ChildAttendanceForm(forms.ModelForm):

    id = forms.IntegerField(widget=HiddenInput(), required=False)
    child_id = forms.IntegerField(widget=HiddenInput(), required=False)
    child_name = forms.CharField(label=_('Child name'))
    attended = forms.ChoiceField(
        label=_("Child Attended?"),
        widget=forms.Select, required=True,
        choices=YES_NO,
        initial=0
    )
    absence_reason = forms.ChoiceField(
        label=_("Absence reason"),
        widget=forms.Select, required=False,
        choices=MSCCAttendanceChild.ABSENCE_REASON,
        initial=0
    )
    absence_reason_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    def __init__(self, *args, **kwargs):
        super(ChildAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['child_name'].widget.attrs['readonly'] = True
        fields_keyorder = ['id','child_name', 'attended', 'absence_reason', 'absence_reason_other', 'child_id']
        if self.fields.has_key('keyOrder'):
            self.fields.keyOrder = fields_keyorder
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in fields_keyorder)

    def clean(self):
        cleaned_data = super(ChildAttendanceForm, self).clean()
        attended = cleaned_data.get('attended')
        absence_reason = cleaned_data.get('absence_reason')
        absence_reason_other = cleaned_data.get('absence_reason_other')
        if attended == 'no':
            if absence_reason == '':
                self.add_error('absence_reason', "The reason should be specified for " + cleaned_data.get('child_name'))
            elif absence_reason == 'other' and absence_reason_other == '':
                self.add_error('absence_reason_other',
                               "The reason should be specified for " + cleaned_data.get('child_name'))

    class Meta:
        model = MSCCAttendanceChild
        fields = ('id','absence_reason','absence_reason_other', 'attended', 'child_id')
        widgets = {'tag': forms.HiddenInput()}

