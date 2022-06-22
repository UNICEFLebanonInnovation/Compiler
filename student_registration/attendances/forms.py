from django import forms
from student_registration.attendances.models import AttendanceDt
import datetime
from .widgets import DatePickerInput
from django.utils.translation import ugettext as _
from django.forms import inlineformset_factory,HiddenInput
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
        required=False, to_field_name='id',
        initial=0
    )
    class Meta:
        model = CLMAttendance
        fields = (
            'school',
            'registration_level',
            'day_off',
            'close_reason')


class AttendanceStudentForm(forms.ModelForm):

    student_id = forms.IntegerField(widget=HiddenInput(), required=False)
    student_name = forms.CharField()

    class Meta:
        model = CLMAttendanceStudent

        fields = ('attended', 'absence_reason','student_id')
        widgets = {'tag': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(AttendanceStudentForm, self).__init__(*args, **kwargs)

        self.fields['student_name'].widget.attrs['readonly'] = True



