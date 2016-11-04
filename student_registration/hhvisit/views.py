# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from django.core.urlresolvers import reverse
from datetime import datetime


from student_registration.eav.models import Attribute
from student_registration.hhvisit.models import (
    HouseholdVisit,
    HouseholdVisitListView,

)
from .serializers import HouseholdVisitSerializer
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

class HouseholdVisitListView(LoginRequiredMixin, TemplateView):
        """
        Provides the Household visit  page with lookup types in the context
        """
        model = HouseholdVisit
        template_name = 'hhvisit/list.html'

        def get_context_data(self, **kwargs):
            data = []
            locations = Location.objects.all()
            location = self.request.GET.get("location", 0)
            if location:
                data = self.model.objects.filter(registering_adult__school__location_id=location).order_by('id')

            return {
                'visits': data,
                'locations': locations,
                'selectedSchool': int(location),
            }

