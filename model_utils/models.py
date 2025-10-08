"""Provide stand-ins for the time stamped model base class."""

from datetime import datetime

from django.db import models


class TimeStampedModel(models.Model):
    """Model that stores ``created``/``modified`` timestamps in memory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.utcnow()
        self.created = kwargs.get('created', now)
        self.modified = kwargs.get('modified', now)

    def save(self):
        self.modified = datetime.utcnow()
        super().save()
