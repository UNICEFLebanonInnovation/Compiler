# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.utils import timezone

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
    MainReason,
    SpecificReason,
    ServiceType,
)
from .serializers import SpecificReasonSerializer , HouseholdVisitSerializer
from student_registration.hhvisit.forms import (
    HouseholdVisitForm
)

from student_registration.locations.models import Location

from .models import HouseholdVisit , SpecificReason
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



class HouseholdVisitLoadViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = HouseholdVisit
    lookup_field = 'id'
    queryset = HouseholdVisit.objects.all()
    serializer_class = HouseholdVisitSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # def get_context_data(self, **kwargs):
    #
    #     return {
    #         'form': HouseholdVisitForm({'location': self.request.user.location_id,
    #                                  'locations': self.request.user.locations.all()}),
    #     }

    # def get_object(self):
    #     householdvisit = []
    #     try:
    #         householdvisit = HouseholdVisit.objects.filter(id=self.kwargs.get  ('id')).order_by('id')
    #         if householdvisit:
    #
    #             householdvisit[0].attempts = []
    #
    #             householdvisit[0].attempts.append({})
    #             householdvisit[0].attempts[0]["household_found"] = True
    #             householdvisit[0].attempts[0]["comment"] = 'C C C C'
    #             householdvisit[0].attempts[0]["date"] = datetime.strptime('2016-11-8T00:00:00', '%Y-%m-%dT%H:%M:%S')
    #
    #
    #             return householdvisit[0]
    #         raise Http404()
    #     except Http404 as exp:
    #         raise exp




class HouseholdVisitListView(LoginRequiredMixin, TemplateView):
        """
        Provides the Household visit  page with lookup types in the context
        """
        model = HouseholdVisit
        template_name = 'hhvisit/list.html'

        def get_context_data(self, **kwargs):
            data = []
            locations = Location.objects.all().filter(type_id=2).order_by('name')
            mainreasons = MainReason.objects.order_by('name')
            specificreasons = SpecificReason.objects.order_by('name')
            servicetypes = ServiceType.objects.order_by('name')
            location = self.request.GET.get("location", 0)
            if location:
                data = self.model.objects.filter(registering_adult__school__location_id=location).order_by('id')

            return {
                'visits': data,
                'locations': locations,
                'mainreasons': mainreasons,
                'specificreasons': specificreasons,
                'servicetypes' : servicetypes,
                'selectedLocation': int(location),
                'visit_form': HouseholdVisitForm
            }

class SpecificReasonViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    model = SpecificReason
    queryset = SpecificReason.objects.all()
    serializer_class = SpecificReasonSerializer
    permission_classes = (permissions.IsAuthenticated,)


def get_success_url(self):
    return reverse('registrations:registering_pilot')
