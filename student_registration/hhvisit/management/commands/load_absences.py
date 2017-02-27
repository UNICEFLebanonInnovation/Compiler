__author__ = 'ybaydoun'

from django.core.management.base import BaseCommand

from student_registration.hhvisit.tasks import *

from student_registration.hhvisit.models import (
    HouseholdVisit,
    HouseholdVisitAttempt,
    ChildVisit,
    ChildAttendanceMonitoring,
    AttendanceMonitoringDate,
    #StudentAbsence
)

from student_registration.attendances.models import (
    Attendance
)
from student_registration.registrations.models import (
    Registration
)


from student_registration.locations.models import (
    Location
)

from student_registration.students.models import (
    Student
)

from datetime import datetime
import datetime as datetime2

class Command(BaseCommand):
    help = 'Load absence data'

    def handle(self, *args, **options):
        load_absences()



def LoadAbsences(absencesData) :
    lastRunDate = AttendanceMonitoringDate.objects.filter() \
                  .order_by('-date_monitoring').values_list('date_monitoring', flat=True).first()

    if lastRunDate is None:
        lastRunDateText = ''
    else:
        lastRunDateText = lastRunDate.strftime('%Y-%m-%d')

    #lcd = GetChildrenAbsences(lastRunDateText)
    #lcd = GetDBChildrenAbsences(lastRunDateText)
    lcd = GetURLChildAbsences(absencesData)

    SaveChildAbsences(lcd)

    result = True

    return result

def SaveChildAbsences(childAbsences):

    result = ''

    for childAbsence in childAbsences:
        registering_adult_id = Registration.objects.filter(student_id=childAbsence.StudentID).values_list('registering_adult_id', flat=True).first()

        result += '<br/>'
        import pprint
        result += pprint.pformat(registering_adult_id)

        # isFirstAbsence = not ChildAttendanceMonitoring.objects.filter( \
        #     student_id=childAbsence.StudentID \
        #     ).exists()
        isFirstAbsence = False


        result += pprint.pformat(isFirstAbsence)

        houseHoldVisit = None

        if not isFirstAbsence:

            houseHoldVisit = HouseholdVisit.objects.filter( \
                registering_adult_id=registering_adult_id \
                ).first()

            if houseHoldVisit is None:

                houseHoldVisit = HouseholdVisit.objects.create( \
                    visit_status="pending", \
                    registering_adult_id = registering_adult_id \
                    )

                houseHoldVisit.save()

            houseHoldVisit = HouseholdVisit.objects.filter(registering_adult_id=registering_adult_id).first()



        childVisit = ChildVisit.objects.filter( \
            student_id=childAbsence.StudentID
            ).first()

        if (childVisit is None) and (not isFirstAbsence):

            childVisit = ChildVisit.objects.create( \
                household_visit_id=houseHoldVisit.id, \
                student_id=childAbsence.StudentID \
                )

            childVisit.save()


        attendanceMonitoringExists = ChildAttendanceMonitoring.objects.filter( \
            student_id=childAbsence.StudentID, \
            date_from=childAbsence.FromDate, \
            date_to=childAbsence.ToDate \
            ).exists()


        if not attendanceMonitoringExists :

            visitAttemptID = None

            if not isFirstAbsence :
                attemptExists = HouseholdVisitAttempt.objects.filter( \
                    household_visit_id=houseHoldVisit.id \
                    ).exists()
                requiresNewAttempt = (houseHoldVisit.visit_status == "completed") or (not attemptExists)

                if requiresNewAttempt and (not isFirstAbsence):

                    visitAttempt = HouseholdVisitAttempt.objects.create( \
                        household_visit_id=houseHoldVisit.id, \
                        date=datetime.now(), \
                        comment='' \
                        )

                    visitAttempt.save()

                    houseHoldVisit.visit_status = "pending"
                    houseHoldVisit.save()

                visitAttemptID = HouseholdVisitAttempt.objects.filter(household_visit_id=houseHoldVisit.id) \
                                 .order_by('-id').values_list('id', flat=True).first()

            attendanceMonitoring = ChildAttendanceMonitoring.objects.create( \
                student_id=childAbsence.StudentID, \
                is_first_visit = isFirstAbsence, \
                date_from=childAbsence.FromDate, \
                date_to=childAbsence.ToDate, \
                visit_attempt_id=visitAttemptID
                )

            if not childVisit is None:
                attendanceMonitoring.child_visit_id = childVisit.id
                childVisit.child_status = "pending"
                childVisit.child_absence_period = childAbsence.GetPeriod()
                childVisit.save()

            attendanceMonitoring.save()


    attendanceMonitoringDate = AttendanceMonitoringDate.objects.create( \
        date_monitoring=datetime.now()
    )

    attendanceMonitoringDate.save()

    return result


def GetURLChildAbsences(absencesData):

    childAbsences = []

    locationIdentifiers = Location.objects.filter(pilot_in_use=True) \
                          .values_list('id', flat=True)

    studentIdentifiersList = Registration.objects\
                             .values_list('student__number', 'student__id')

    studentIdentifiersDictionary = {studentIdentifier[0]: studentIdentifier[1]
                                    for studentIdentifier in studentIdentifiersList}


    studentFieldsList = Registration.objects\
                             .values_list\
                             ( \
                                'student__first_name',\
                                'student__father_name',\
                                'student__last_name',\
                                'student__birthday_month',\
                                'student__birthday_day',\
                                'student__birthday_year',\
                                'student__id'\
                             )

    studentFieldsDictionary = { \
                                 studentFields[0]+'-'+ \
                                 studentFields[1]+'-'+ \
                                 studentFields[2]+'-'+ \
                                 studentFields[3]+'-'+ \
                                 studentFields[4]+'-'+ \
                                 studentFields[5]: studentFields[6]\
                                 for studentFields in studentFieldsList}

    for studentAbsence in absencesData:

        numberOfDays = studentAbsence['absent_days']

        if numberOfDays is None:
            numberOfDays = 0

        childAbsence = ChildAbsence()

        attendanceDate = datetime.strptime(studentAbsence['last_attendance_date'], "%Y-%m-%d").date()

        fromDate = attendanceDate
        toDate = attendanceDate + datetime2.timedelta(days=numberOfDays)

        studentID = None

        # studentAbsence['student_number'] = '101052532398M'

        if studentIdentifiersDictionary.has_key(studentAbsence['student_number']):

            studentID = studentIdentifiersDictionary[studentAbsence['student_number']]
        else:

            concatenatedFields = studentAbsence['student_first_name'] + '-' + \
                                 studentAbsence['student_father_name'] + '-' + \
                                 studentAbsence['student_last_name'] + '-' + \
                                 studentAbsence['student_birthday_month'] + '-' + \
                                 studentAbsence['student_birthday_day'] + '-' + \
                                 studentAbsence['student_birthday_year'] \

            if studentFieldsDictionary.has_key(concatenatedFields):
                studentID = studentFieldsDictionary[concatenatedFields]

        childAbsence.StudentID = studentID
        childAbsence.FromDate = fromDate
        childAbsence.ToDate = toDate
        childAbsence.NumberOfDays = numberOfDays
        childAbsence.Index = 1
        if (childAbsence.StudentID is not None) and \
            (childAbsence.FromDate > datetime.strptime('2010-01-01', '%Y-%m-%d').date()) and \
            ((studentAbsence['reattend_date'] is None)):
            childAbsences.append(childAbsence)


    return childAbsences

# def GetDBChildrenAbsences(lastCheckDateString):
#
#     childAbsences = []
#
#     lastCheckDate = None
#
#     if lastCheckDateString:
#         lastCheckDate = datetime.strptime(lastCheckDateString, "%Y-%m-%d").date()
#
#         studentAbsences = StudentAbsence.objects.filter(date_entry__gte=lastCheckDate).order_by('date_from')
#     else:
#         studentAbsences = StudentAbsence.objects.order_by('date_from').all()
#
#     for studentAbsence in studentAbsences:
#
#         childAbsence = ChildAbsence()
#
#         childAbsence.StudentID =studentAbsence.student_id
#         childAbsence.FromDate =studentAbsence.date_from
#         childAbsence.ToDate =studentAbsence.date_to
#         childAbsence.NumberOfDays = 10
#
#         childAbsences.append(childAbsence)
#
#     return childAbsences


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
                     .order_by('attendance_date').values('attendance_date', "status").distinct()

    else :

       attendances = Attendance.objects.filter(attendance_date__gte=firstAttendanceDate, student_id=studentID) \
                     .order_by('attendance_date').values('attendance_date', "status").distinct()

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
        self.Index = 0

    def Reset(self, studentID):
        self.StudentID = studentID
        self.FromDate = None
        self.ToDate = None
        self.NumberOfDays = 0
        self.Index = 0

    def AddAbsenceDate(self, absenceDate):
        if self.FromDate is None :
            self.FromDate = absenceDate

        self.ToDate = absenceDate
        self.NumberOfDays += 1

    def GetPeriod(self):

        import pprint

        return pprint.pformat(self.NumberOfDays)


    def __repr__(self):
        import pprint
        return 'StudentID: '+pprint.pformat(self.StudentID) + ' ' \
               'FromDate: ' +pprint.pformat(self.FromDate) + ' ' \
               'ToDate: ' +pprint.pformat(self.ToDate) + ' ' \
               'NumberOfDays: ' +pprint.pformat(self.NumberOfDays) + ' '
