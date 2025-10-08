"""Bare minimum migration framework used in tests."""


class Migration:
    dependencies = []
    operations = []


class AddField:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
