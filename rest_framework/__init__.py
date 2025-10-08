"""Subset of the Django REST Framework surface required for the kata tests."""

from . import viewsets  # noqa: F401
from . import mixins  # noqa: F401
from . import permissions  # noqa: F401
from .decorators import action, api_view  # noqa: F401
