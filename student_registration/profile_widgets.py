from django.forms.widgets import ClearableFileInput


class ProfilePictureInput(ClearableFileInput):
    """Link saved pictures through the authenticated storage-backed endpoint."""
    template_name = 'widgets/profile_picture_input.html'
    download_url = ''

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['download_url'] = self.download_url
        return context
