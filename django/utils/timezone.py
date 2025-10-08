"""Small subset of :mod:`django.utils.timezone`."""

from datetime import datetime


def now():
    """Return a naive ``datetime`` similar to Django's default behaviour."""

    return datetime.utcnow()
