"""Minimal subset of :mod:`django.apps` used in the tests."""


class AppConfig:
    """Small stand-in for :class:`django.apps.AppConfig`."""

    name = None

    def __init__(self, app_name=None, app_module=None):
        self.name = app_name or self.name
        self.module = app_module

    def ready(self):  # pragma: no cover - mirrors Django's API
        """Hook for subclasses."""

        return None


class _AppRegistry:
    def get_model(self, app_label, model_name):  # pragma: no cover - compatibility stub
        raise LookupError('App registry is not populated')


apps = _AppRegistry()
