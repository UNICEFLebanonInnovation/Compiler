# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework import viewsets, mixins, permissions

from student_registration.hhvisit.forms import (
    HouseholdVisitForm
)

from student_registration.registrations.models import (
    RegisteringAdult
)

from student_registration.hhvisit.models import (
    MainReason,
    ServiceType,
    HouseholdVisitAttempt,
    ChildService,
    HouseholdVisitComment,
    HouseholdVisitTeam
)
from student_registration.locations.models import Location
from .models import ChildVisit
from .models import HouseholdVisit , SpecificReason
from .serializers import SpecificReasonSerializer , HouseholdVisitSerializer, VisitAttemptSerializer, ChildVisitSerializer, ChildServiceSerializer, HouseholdVisitCommentSerializer, HouseholdVisitRecordSerializer


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

    def get_queryset(self):
        return self.queryset.order_by('-id')

    # def get_queryset(self):
    #     return self.queryset.order_by()
    # def update(self, request, *args, **kwargs):
    #
    #     data = request.data
    #
    #
    #     import pprint
    #     import json
    #     #b = json.loads(data)
    #
    #
    #
    #     #myDict = dict(data.iterlists())
    #
    #     #data = (myDict.keys())
    #
    #     #serializer = HouseholdVisitSerializer(data=data)
    #
    #
    #     result = data
    #
    #     # if serializer.is_valid():
    #     #     result=1
    #     #     serializer.save()
    #     #     serializer.save()
    #
    #
    #     return Response(result)

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
    #             householdvisit[0].attempts[0]["household_not_found"] = True
    #             householdvisit[0].attempts[0]["comment"] = 'C C C C'
    #             householdvisit[0].attempts[0]["date"] = datetime.strptime('2016-11-8T00:00:00', '%Y-%m-%dT%H:%M:%S')
    #
    #
    #             return householdvisit[0]
    #         raise Http404()
    #     except Http404 as exp:
    #         raise exp


class HouseholdVisitAttemptViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = HouseholdVisitAttempt
    lookup_field = 'id'
    queryset = HouseholdVisitAttempt.objects.all()
    serializer_class = VisitAttemptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.order_by('-id')



class HouseholdVisitChildViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = ChildVisit
    lookup_field = 'id'
    queryset = ChildVisit.objects.all()
    serializer_class = ChildVisitSerializer
    permission_classes = (permissions.IsAuthenticated,)


class HouseholdVisitServiceViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = ChildService
    lookup_field = 'id'
    queryset = ChildService.objects.all()
    serializer_class = ChildServiceSerializer
    permission_classes = (permissions.IsAuthenticated,)



class HouseholdVisitCommentViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = HouseholdVisitComment
    lookup_field = 'id'
    queryset = HouseholdVisitComment.objects.all()
    serializer_class = HouseholdVisitCommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

class HouseholdVisitListView(LoginRequiredMixin, TemplateView):
        """
        Provides the Household visit  page with lookup types in the context
        """
        model = HouseholdVisit
        template_name = 'hhvisit/list.html'

        def get_context_data(self, **kwargs):
            data = []
            # locations = Location.objects.all().filter(type_id=2).order_by('name')
            mainreasons = MainReason.objects.order_by('name')
            specificreasons = SpecificReason.objects.order_by('name')
            servicetypes = ServiceType.objects.order_by('name')
            # location = self.request.GET.get("location", 0)
            data = self.model.objects.filter(
                Q(household_visit_team__first_enumerator=self.request.user.id)
                | Q(household_visit_team__second_enumerator = self.request.user.id)
                | Q(registering_adult__school__location__parent_id=self.request.user.governante_id)
            ).order_by('-visit_status', 'id')
            return {
                'visits': data,
                # 'locations': locations,
                'mainreasons': mainreasons,
                'specificreasons': specificreasons,
                'servicetypes' : servicetypes,
                # 'selectedLocation': int(location),
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


class HouseholdVisitListSupervisorView(LoginRequiredMixin, TemplateView):
    """
    Provides the Household visit  page with lookup types in the context
    """

    model = HouseholdVisit
    template_name = 'hhvisit/list_supervisor.html'

    def get_context_data(self, **kwargs):
        data = []
        locations = Location.objects.all().filter(pilot_in_use=True).order_by('name')
        location = self.request.GET.get("location", 0)
        if location:
            data = self.model.objects.filter(registering_adult__school__location_id=location).order_by('-visit_status'
                                                                                                       , 'id')

        # get all teams
        teams = HouseholdVisitTeam.objects.all()

        return {
            'visits': data,
            'teams': teams,
            'locations': locations,
            'selectedLocation': int(location),
            'visit_form': HouseholdVisitForm
        }


class HouseholdVisitSaveViewSet(mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = HouseholdVisit
    lookup_field = 'id'
    queryset = HouseholdVisit.objects.all()
    serializer_class = HouseholdVisitRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)


def test(request):

    #result = LoadAbsences()
    import student_registration.hhvisit.management.commands.load_absences
    student_registration.hhvisit.management.commands.load_absences.LoadAbsences()

    result = 'Absences were loaded successfully.'

    return HttpResponse(result)


from django.conf import settings
import requests

from student_registration.registrations.models import (
    Registration
)


def LoadAbsences(request):

    received_data = requests.get(settings.ABSENCE_URL, headers={'Authorization': 'Token '+settings.ABSENCE_TOKEN})
    result = received_data

    # import json
    # received_json_data = json.loads(received_data.text)
    #
    # import pprint
    # result = pprint.pformat(received_json_data)
    #
    #
    #
    # import student_registration.hhvisit.management.commands.load_absences
    # lcd = student_registration.hhvisit.management.commands.load_absences.GetURLChildAbsences(received_json_data)
    #
    # import pprint
    # result = pprint.pformat(lcd)

    return HttpResponse(result)

def SaveAbsences(request):

    received_data = requests.get(settings.ABSENCE_URL, headers={'Authorization': 'Token '+settings.ABSENCE_TOKEN})

    import json
    received_json_data = json.loads(received_data.text)

    import student_registration.hhvisit.management.commands.load_absences
    student_registration.hhvisit.management.commands.load_absences.LoadAbsences(received_json_data)

    result = 'Absences were loaded successfully.'

    return HttpResponse(result)


class StudentAbsenceView(LoginRequiredMixin, TemplateView):

    template_name = 'hhvisit/StudentAbsence.html'

    def get_context_data(self, **kwargs):
        return {
        }



# class StudentSearch(FormView):
#     def get(self,request,*args,**kwargs):
#
#         data = request.GET
#         username = data.get("term")
#
#         if username:
#             users = []
#         else:
#             users = []
#             results = []
#
#         for user in users:
#             user_json = {}
#             user_json['id'] = user.id
#             user_json['label'] = user.username
#             user_json['value'] = user.username
#             results.append(user_json)
#
#         data = json.dumps(results)
#         mimetype = 'application/json'
#         return HttpResponse(data, mimetype)


# class StudentSearch(FormView):
#     def get(self, request, *args, **kwargs):
#         data = '[]'
#         mimetype = 'application/json'
#         return HttpResponse(data, mimetype)
