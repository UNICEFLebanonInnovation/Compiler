# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.utils.translation import ugettext as _

from student_registration.hhvisit.models import (
    HouseholdVisit,
)
from student_registration.hhvisit.forms import (
    HouseholdVisitForm
)


from student_registration.locations.models import Location

from .models import HouseholdVisit
from .models import ChildVisit


class HouseholdVisitView(LoginRequiredMixin, TemplateView):
    """
    Provides the registration page with lookup types in the context
    """
    model = HouseholdVisit
    template_name = 'hhvisit/household-visit.html'

    def get_context_data(self, **kwargs):

        return {
            'form': HouseholdVisitForm({'location': self.request.user.location_id,
                                     'locations': self.request.user.locations.all()}),
        }

