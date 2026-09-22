# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DataSyncConfig(AppConfig):
    """Outbound replication of MSCC data to BMA-NFE."""

    name = 'student_registration.datasync'
    verbose_name = 'Data replication'

    def ready(self):
        """Connect the change-capture receivers once the app registry is up."""
        from . import signals

        signals.connect()
