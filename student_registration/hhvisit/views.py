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
from django.db.models import Q
from student_registration.hhvisit.models import (
    HouseholdVisit,
    MainReason,
    SpecificReason,
    ServiceType,
    HouseholdVisitAttempt,
    ChildService,
    ChildVisit,
    HouseholdVisitComment,
    HouseholdVisitTeam,
    ChildAttendanceMonitoring,
    AttendanceMonitoringDate,
    Student
)
from .serializers import SpecificReasonSerializer , HouseholdVisitSerializer, VisitAttemptSerializer, ChildVisitSerializer, ChildServiceSerializer, HouseholdVisitCommentSerializer, HouseholdVisitRecordSerializer
from student_registration.hhvisit.forms import (
    HouseholdVisitForm
)

from student_registration.locations.models import Location

from .models import HouseholdVisit , SpecificReason
from .models import ChildVisit

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from student_registration.attendances.models import (
    Attendance
)

from student_registration.registrations.models import (
    Registration
)

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
            data = self.model.objects.filter(Q(household_visit_team__first_enumerator = self.request.user.id) | Q(household_visit_team__second_enumerator = self.request.user.id)).order_by('id')
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
        locations = Location.objects.all().filter(type_id=2).order_by('name')
        location = self.request.GET.get("location", 0)
        if location:
            data = self.model.objects.filter(registering_adult__school__location_id=location).order_by('id')

        # get all teams
        teams = HouseholdVisitTeam.objects.all()

        return {
            'visits': data,
            'teams': teams,
            'locations': locations,
            'selectedLocation': int(location),
            'visit_form': HouseholdVisitForm
        }

# class HouseholdVisitSaveView(LoginRequiredMixin,APIView):
#     renderer_classes = (JSONRenderer, )
#
#     def put(self, request, format='json'):
#
#         content = {'user_count': 0}
#         return Response(content)


class HouseholdVisitSaveViewSet(mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    model = HouseholdVisit
    lookup_field = 'id'
    queryset = HouseholdVisit.objects.all()
    serializer_class = HouseholdVisitRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)



from datetime import date

def test(request):

    lcd = GetChildrenAbsences('2016-11-21')
    #lcd = GetChildrenAbsences("")

    SaveChildAbsences(lcd)

    result = dumpobjectcontent(lcd)

    return HttpResponse(result)


def SaveChildAbsences(childAbsences):

    for childAbsence in childAbsences:
        registering_adult_id = Registration.objects.filter(student_id=childAbsence.StudentID).values_list('registering_adult_id', flat=True).first()

        houseHoldVisit = HouseholdVisit.objects.create( \
            visit_status="pending", \
            registering_adult_id = registering_adult_id \
            )

        houseHoldVisit.save()

        childVisit = ChildVisit.objects.create( \
            household_visit_id=houseHoldVisit.id, \
            student_id=childAbsence.StudentID \
            )

        childVisit.save()


        attendanceMonitoring = ChildAttendanceMonitoring.objects.create( \
            student_id=childAbsence.StudentID, \
            is_first_visit = False, \
            date_from=childAbsence.FromDate, \
            date_to=childAbsence.ToDate \
            )
        attendanceMonitoring.child_visit_id = childVisit.id

        attendanceMonitoring.save()



def GetChildrenAbsences(lastCheckDateString):

    lastCheckDate = None

    if lastCheckDateString:
        lastCheckDate = datetime.strptime(lastCheckDateString, "%Y-%m-%d").date()
        absentChildIdentifiers =  Attendance.objects.filter(attendance_date__gte=lastCheckDate,status=False)\
                                  .values_list('student_id',flat=True).distinct()
    else:
        absentChildIdentifiers =  Attendance.objects.filter(status=False)\
                                  .values_list('student_id',flat=True).distinct()


    sm = AbsenceMonitoring()

    for studentID in absentChildIdentifiers:

        firstAttendanceDate = None

        if lastCheckDate:
           firstAttendanceDate = Attendance.objects.filter(attendance_date__lte=lastCheckDate, student_id=studentID, status=True) \
                                 .order_by('-attendance_date').values_list('attendance_date',flat=True).first()

        studentAttendances = GetChildAttendances(studentID,firstAttendanceDate)

        for studentAttendance in studentAttendances:

            sm.MonitorAttendance(studentID, studentAttendance['attendance_date'], studentAttendance['status'])

    return sm.GetChildAbsences()


def GetChildAttendances(studentID,firstAttendanceDate):

    attendances = None

    if(firstAttendanceDate == None) :

       attendances = Attendance.objects.filter(student_id=studentID) \
                     .order_by('attendance_date').values('attendance_date', "status")

    else :

       attendances = Attendance.objects.filter(attendance_date__gte=firstAttendanceDate, student_id=studentID) \
                     .order_by('attendance_date').values('attendance_date', "status")

    return attendances



class AbsenceMonitoring:

    def __init__(self, *args, **kwargs):

        self.StudentAbsenceMonitorings = {}


    def MonitorAttendance(self, studentID, attendanceDate, isPresent):

        sm = self.CheckGetStudentMonitor(studentID)

        sm.MonitorAttendance(attendanceDate, isPresent)

        return sm


    def CheckGetStudentMonitor(self, studentID):

        result = None

        if studentID in self.StudentAbsenceMonitorings:
            result = self.StudentAbsenceMonitorings[studentID]
        else:
            result = StudentAbsenceMonitoring()
            result.StudentID = studentID
            self.StudentAbsenceMonitorings[studentID] = result

        return result

    def GetChildAbsences(self):

        result = None

        childAbsenceLists = [[z for z in y.ChildAbsences] for (x,y) in self.StudentAbsenceMonitorings.items()]
        result = [val for sublist in childAbsenceLists for val in sublist]

        return result


class StudentAbsenceMonitoring:

    numberOfAbsenceDays = 10

    def __init__(self, *args, **kwargs):

        self.StudentID = None
        self.CurrentChildAbsence = None
        self.ChildAbsences = []
        self.CurrentChildAbsence = ChildAbsence()

    def MonitorAttendance(self, attendanceDate, isPresent):

       if isPresent:

           self.CurrentChildAbsence.Reset(self.StudentID)

       else :

           self.CurrentChildAbsence.AddAbsenceDate(attendanceDate)

           if self.CurrentChildAbsence.NumberOfDays >= self.numberOfAbsenceDays:
              self.CreateNewChildAbsence()

    def CreateNewChildAbsence(self):

        self.ChildAbsences.append(self.CurrentChildAbsence)

        self.CurrentChildAbsence = ChildAbsence()




class ChildAbsence:

    def __init__(self, *args, **kwargs):

        self.StudentID = None
        self.FromDate = None
        self.ToDate = None
        self.NumberOfDays = 0

    def Reset(self, studentID):
        self.StudentID = studentID
        self.FromDate = None
        self.ToDate = None
        self.NumberOfDays = 0

    def AddAbsenceDate(self, absenceDate):
        if self.FromDate is None :
            self.FromDate = absenceDate

        self.ToDate = absenceDate
        self.NumberOfDays += 1


def dumpobject(obj, level=0):

    result = ''


    import pprint
    if isinstance(obj, (int, float, str, unicode, date, datetime)) | (obj is None):
        result = pprint.pformat(obj)

    for attr in dir(obj):
        try:
            val = getattr(obj, attr)

            if attr in ('StudentID', 'FromDate', 'ToDate', 'NumberOfDays', 'CurrentChildAbsence', 'ChildAbsences','StudentAbsenceMonitorings'):

                result += dumpobjectcontent(val,level,attr)

        except Exception as exp:
            test = 0


    return result


def dumpobjectcontent(obj, level=0,attr=''):

    result = ''

    spaces = ''

    val=obj

    for i in xrange(level):
        spaces += '&nbsp;&nbsp;&nbsp;&nbsp;'

    import pprint

    if isinstance(val, (int, float, str, unicode, date, datetime)) | (val is None):
        result += spaces + attr + " : " + pprint.pformat(val) + "<br/>"

    elif isinstance(val, (dict)):

        result += spaces + attr + "<br/>"

        for x, y in val.items():
            result += spaces + pprint.pformat(x) + ":" + "<br/>"
            result += spaces + dumpobject(y, level=level + 1) + "<br/>"

    elif isinstance(val, (list, set)):

        result += spaces + attr + "<br/>"

        for x in val:
            result += dumpobject(x, level=level + 1) + "<br/>"

    else:
        if level < 10:
            test = 0
            result += spaces + attr + "<br/>"
            result += dumpobject(val, level=level + 1) + "<br/>"

    return result
