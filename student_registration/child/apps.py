# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class ChildConfig(AppConfig):
    name = 'student_registration.child'

    def ready(self):
        import reversion
        for model in self.get_models():
            if not reversion.is_registered(model):
                reversion.register(model)
