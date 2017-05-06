from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from .models import Enrollment, LoggingStudentMove
from student_registration.students.models import Student


class EnrollmentForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = '__all__'


class LoggingStudentMoveForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(LoggingStudentMoveForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LoggingStudentMove
        fields = (
            'student',
            'school_from',
            'school_to',
        )
