from django.forms.widgets import ClearableFileInput


class _ProfilePictureLink:
    """Presentation value for the built-in widget; never changes stored files."""

    def __init__(self, value, url):
        self.value = value
        self.url = url

    def __str__(self):
        return str(self.value)


class ProfilePictureInput(ClearableFileInput):
    """Use Django's built-in template with a storage-backed download link."""
    download_url = ''

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if context['widget']['is_initial'] and self.download_url:
            context['widget']['value'] = _ProfilePictureLink(value, self.download_url)
        return context
