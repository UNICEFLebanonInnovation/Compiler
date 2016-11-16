from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import ugettext as _
from django import forms
from student_registration.hhvisit.models import (
    HouseholdVisit,
    ChildVisit,
)
from student_registration.schools.models import School
from student_registration.locations.models import Location

class HouseholdVisitForm(forms.ModelForm):

    # YESNO_CHOICES = ((0, _('No')), (1, _('Yes')))
    #
    # child_enrolled_in_another_school = forms.TypedChoiceField(
    #     choices=YESNO_CHOICES, widget=forms.RadioSelect, coerce=int, required=False
    # )

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

