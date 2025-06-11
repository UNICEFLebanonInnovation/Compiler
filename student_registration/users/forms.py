from django import forms

from dal import autocomplete
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from student_registration.users.models import (
    User
)
from student_registration.schools.models import (
    School,
)


class UserAdminForm(UserChangeForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_closed=False),
        widget=autocomplete.ModelSelect2(url='school_autocomplete'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = '__all__'
