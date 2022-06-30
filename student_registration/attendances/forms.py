from django import forms
from student_registration.attendances.models import AttendanceDt
import datetime
from .widgets import DatePickerInput
from django.utils.translation import ugettext as _
from django.forms import inlineformset_factory,HiddenInput
from django.core.urlresolvers import reverse
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML
from dal import autocomplete
from .models import CLMAttendance,CLMAttendanceStudent
from student_registration.clm.models import Bridging
from student_registration.schools.models import (
    School,
)

class AttendanceDtdAdminForm(forms.ModelForm):
    class Meta:
        model = AttendanceDt
        fields = '__all__'


class AttendanceForm(forms.Form):
    CLOSE_REASON = (
        ('', '----------'),
        ('public_holiday', _('Public Holiday')),
        ('school_holiday', _('School Holiday')),
        ('strike', _('Strike')),
        ('weekly_holiday', _('Weekly Holiday')),
        ('roads_closed', _('Roads Closed')),
    )
    attendance_date = forms.DateField(initial=datetime.date.today,widget=DatePickerInput)

    day_off = forms.ChoiceField(
        label=_("Day Off"),
        widget=forms.Select, required=True,
        choices=Bridging.YES_NO,
        initial=1
    )
    close_reason = forms.ChoiceField(
        label=_("Day off reason"),
        widget=forms.Select, required=True,
        choices=CLOSE_REASON,
        initial=1
    )


class MainAttendanceForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_first_shift='yes'), widget=forms.Select,
        label=_('School Name'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    attendance_date = forms.DateField(
        initial=datetime.date.today,
        widget=DatePickerInput,
        label=_('Attendance date')
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=CLMAttendance.REGISTRATION_LEVEL
    )
    day_off = forms.ChoiceField(
        label=_("Day off ?"),
        widget=forms.Select, required=True,
        choices=CLMAttendance.YES_NO
    )
    close_reason = forms.ChoiceField(
        label=_("Day off reason"),
        widget=forms.Select, required=False,
        choices=CLMAttendance.CLOSE_REASON
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MainAttendanceForm, self).__init__(*args, **kwargs)
        # instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('attendances:main_attendance')
        # if instance:
        #     form_action = reverse('attendances:main_attendance', kwargs={'pk': instance.id})
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
                    Div('school', css_class='col-md-3 form-group'),
                    Div('registration_level', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                Div(
                    Div('day_off', css_class='col-md-3 form-group'),
                    Div('close_reason', css_class='col-md-3 form-group'),
                    css_class='row',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                        Button('LoadStudentsButton', _('Load'), css_class='col-md-2 btn btn-info'),
                        Submit('save', _('Save'), css_class='col-md-2'),
                        css_class='button-group'
                    )
        )

    def clean(self):
        cleaned_data = super(MainAttendanceForm, self).clean()
        if cleaned_data.get('day_off') == 'yes' and cleaned_data.get('close_reason') != '':
            self.add_error('close_reason', "The reason should be specified.")
    class Meta:
        model = CLMAttendance
        fields = (
            'attendance_date',
            'school',
            'registration_level',
            'day_off',
            'close_reason')


class AttendanceStudentForm(forms.ModelForm):

    student_id = forms.IntegerField(widget=HiddenInput(), required=False)
    student_name = forms.CharField()
    student_gender = forms.CharField()

    class Meta:
        model = CLMAttendanceStudent

        fields = ('attended', 'absence_reason', 'student_id')
        widgets = {'tag': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(AttendanceStudentForm, self).__init__(*args, **kwargs)

        self.fields['student_name'].widget.attrs['readonly'] = True
        self.fields['student_gender'].widget.attrs['readonly'] = True





