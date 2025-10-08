"""Lightweight Django compatibility shims for unit tests."""

from .conf import settings  # noqa: F401


def setup():
    """Stub implementation of :func:`django.setup`.

    The real Django initialises application registries. The tests in this kata
    simply need the function to exist so the stub is intentionally empty.
    """

    return None


# Re-export commonly imported Django modules so ``from django import forms``
# works with the shim implementation.
from . import forms  # noqa: E402,F401
from . import template  # noqa: E402,F401
