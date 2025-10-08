"""Stub token model used in tests."""

from django.db import models


class Token(models.Model):
    key = models.CharField(max_length=40)


Token.objects = models.InMemoryManager(Token)
