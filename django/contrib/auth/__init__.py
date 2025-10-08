"""Minimal authentication utilities."""

from .models import User  # noqa: F401


def get_user_model():
    """Return the stub user model."""

    return User
