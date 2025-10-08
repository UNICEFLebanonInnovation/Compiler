"""Minimal stubs for django-mptt models used in the tests."""

from django.db import models


class MPTTModel(models.Model):
    class Meta:
        abstract = True


class TreeForeignKey(models.ForeignKey):
    pass
