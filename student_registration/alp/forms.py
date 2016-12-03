from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from dal import autocomplete
from .models import Outreach
from student_registration.students.models import Student


class OutreachForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(OutreachForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Outreach
        fields = '__all__'


