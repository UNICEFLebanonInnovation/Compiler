from student_registration.profile_widgets import ProfilePictureInput
from django import forms
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext as _
from .models import Registration


class ProfilePictureForm(forms.ModelForm):
    """Upload or replace the profile picture stored on a Registration record."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['profile_picture'].widget.download_url = reverse(
                'mscc:profile_picture_file', kwargs={'pk': self.instance.pk}
            )

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture and 'profile_picture' in self.files:
            FileExtensionValidator(
                allowed_extensions=('png', 'jpg', 'jpeg'),
                message=_('Only PNG, JPG, and JPEG pictures are allowed.'),
            )(picture)
            if picture.image.format not in ('PNG', 'JPEG'):
                raise forms.ValidationError(
                    _('Only PNG, JPG, and JPEG pictures are allowed.')
                )
        return picture

    class Meta:
        model = Registration
        fields = ('profile_picture',)
        widgets = {
            'profile_picture': ProfilePictureInput(
                attrs={'accept': '.png,.jpg,.jpeg,image/png,image/jpeg'}
            ),
        }
