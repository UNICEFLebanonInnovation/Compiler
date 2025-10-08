"""Very small stand-ins for Django's auth models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from django.db import models


class _UserManager(models.InMemoryManager):
    def create(self, username: str = 'testuser', **extra: Any):
        instance = super().create(username=username, **extra)
        instance.is_authenticated = True
        return instance


@dataclass
class User(models.Model):  # type: ignore[misc] - model base provides custom behaviour
    username: str = 'testuser'
    is_staff: bool = False
    is_superuser: bool = False
    is_active: bool = True

    def __post_init__(self):
        super().__init__(username=self.username,
                         is_staff=self.is_staff,
                         is_superuser=self.is_superuser,
                         is_active=self.is_active)
        self.is_authenticated = True

    def __str__(self):
        return self.username


User.objects = _UserManager(User)


class Group(models.Model):
    name = models.CharField(max_length=80)


Group.objects = models.InMemoryManager(Group)


class AbstractUser(User):
    class Meta:
        abstract = True
