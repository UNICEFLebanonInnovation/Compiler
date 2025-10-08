"""Stub implementations of fields from ``django.contrib.postgres``."""

from django.db import models


class ArrayField(models.Field):
    def __init__(self, base_field=None, size=None, **kwargs):  # noqa: ARG002 - compatibility
        super().__init__(**kwargs)
        self.base_field = base_field
        self.size = size
