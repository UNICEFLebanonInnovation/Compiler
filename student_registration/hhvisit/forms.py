from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.hhvisit.models import (
    HouseholdVisit,
    ChildVisit,
)

class HouseholdVisitForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HouseholdVisitForm, self).__init__(*args, **kwargs)

    class Meta:
        model = HouseholdVisit
        fields = '__all__'


class ChildVisitForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChildVisitForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ChildVisit
        fields = '__all__'

