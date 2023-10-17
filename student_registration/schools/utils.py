import io
import xlwt
import csv
from datetime import date , datetime
from import_export import resources, fields
from django.http import HttpResponse, FileResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Color
from .models import (
    School,
    Club,
    Meeting,
    CommunityInitiative,
    HealthVisit
)
import copy

import logging

logger = logging.getLogger(__name__)


def is_allowed_create(programme):
    from .models import CLMRound
    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            current_round = current_round.get(current_round_bridging=True)
            if current_round.start_date_bridging < current < current_round.end_date_bridging:
                return True
            return False

    except Exception as ex:
        print(ex)
        return False


def is_allowed_edit(programme):
    from .models import CLMRound

    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            current_round = current_round.get(current_round_bridging=True)
            if current_round.start_date_bridging_edit < current < current_round.end_date_bridging_edit:
                return True
            return False

    except Exception as ex:
        print(ex)
        return False


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        if str1 == "":
            str1 += ele
        else:
            str1 += "," + ele

        # return string
    return str1


class MemorySavingQuerysetIterator(object):

    def __init__(self, queryset, max_obj_num=1000):
        self._base_queryset = queryset
        self._generator = self._setup()
        self.max_obj_num = max_obj_num

    def _setup(self):
        for i in xrange(0, self._base_queryset.count(), self.max_obj_num):
            # By making a copy of the queryset and using that to actually access
            # the objects we ensure that there are only `max_obj_num` objects in
            # memory at any given time
            smaller_queryset = copy.deepcopy(self._base_queryset)[i:i + self.max_obj_num]
            # logger.debug('Grabbing next %s objects from DB' % self.max_obj_num)
            for obj in smaller_queryset.iterator():
                yield obj

    def __iter__(self):
        return self

    def next(self):
        return self._generator.next()


def school_build_xls_extraction(qs_school, qs_club, qs_meeting, qs_community_initiative, qs_health_visit):
    buffer = io.BytesIO()

    # school
    wb_school = xlwt.Workbook(encoding='utf-8', style_compression=2)

    ws_school = wb_school.add_sheet('School')

    # Sheet header, first row
    row_num_school = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        'school ID',
        'School CERD Number',
        'Type',
        'School name',
        'School director name',
        'School land phone number',
        'School email',
        'Governorate',
        'District',
        'Cadaster',
        'School GPS (longitude)',
        'School GPS (latitude)',
        'Grade level',
        'School capacity',
        'Available empty building/closed campus',
        'Total Number of children enrolled (excluding Dirasa)',
        'Total Number of children enrolled (male)',
        'Total Number of children enrolled (female)',
        'Total Number of children enrolled (Lebanese)',
        'Total Number of children enrolled (non Lebanese)',
        'Total Number of children enrolled (Dirasa only)',
        'Total Number of children enrolled (male, Dirasa only)',
        'Total Number of children enrolled (female, Dirasa only)',
        'Total Number of children enrolled (Lebanese, Dirasa only)',
        'Total Number of children enrolled (non Lebanese, Dirasa only)',
        'Is the school accessible for CW',
        'Availability of Internet',
        'School Digital Capacity',
        'Working Days',
        'School year start date',
        'School year end date',
        'Did the school receive school supplies/stationery',
        'Total number of Children With Disability (Dirasa only)',
        'Total number of Children With Disability (Excluding Dirasa)',
        'School benefiting from WFP services',
        'Service Type',
        'Owner',
        'Modified By',
        'Created',
        'Modified'
    ]

    for col_num in range(len(columns)):
        ws_school.write(row_num_school, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = qs_school.order_by('id').values_list(
        'id',
        'number',
        'type',
        'name',
        'director_name',
        'land_phone_number',
        'email',
        'governorate__name',
        'district__name',
        'cadaster__name',
        'longitude',
        'latitude',
        'registration_level',
        'school_capacity',
        'empty_building',
        'number_children',
        'number_children_male',
        'number_children_female',
        'number_children_lebanese',
        'number_children_non_lebanese',
        'number_children_sbp',
        'number_children_male_sbp',
        'number_children_female_sbp',
        'number_children_lebanese_sbp',
        'number_children_non_lebanese_sbp',
        'CWD_accessible',
        'internet_available',
        'school_digital_capacity',
        'working_days',
        'academic_year_start',
        'academic_year_end',
        'receive_supplies',
        'number_dirasa_children_disability',
        'number_total_children_disability',
        'benefit_wfp_service',
        'wfp_service_type',
        'owner__username',
        'modified_by__username',
        'created',
        'modified'
    )
    for row in rows:
        row_num_school += 1
        for col_num in range(len(row)):
            ws_school.write(row_num_school, col_num, row[col_num], font_style)

    # Club
    ws_club = wb_school.add_sheet('Club')
    row_num_club = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column_header_club = [
        'id',
        'School ID',
        'School Name',
        'Club Name',
        'Number of Clubs',
        'Club Type',
        'Total Number of Children',
        'Owner',
        'Modified By',
        'Created',
        'Modified'
    ]

    for col_num in range(len(column_header_club)):
        ws_club.write(row_num_club, col_num, column_header_club[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows_club = qs_club.values_list(
        'id',
        'school',
        'school__name',
        'club_name',
        'number_clubs',
        'club_type',
        'number_children',
        'owner__username',
        'modified_by__username',
        'created',
        'modified'
    )

    for row in rows_club:
        row_num_club += 1
        for col_num in range(len(row)):
            ws_club.write(row_num_club, col_num, row[col_num], font_style)


    # Meeting
    ws_meeting = wb_school.add_sheet('Meeting')
    row_num_meeting = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column_header_meeting = [
        'id',
        'School ID',
        'School Name',
        'Meeting Name',
        'Meeting Date',
        'Number of Participants',
        'Owner',
        'Modified By',
        'Created',
        'Modified'
    ]

    for col_num in range(len(column_header_meeting)):
        ws_meeting.write(row_num_meeting, col_num, column_header_meeting[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows_meeting = qs_meeting.values_list(
        'id',
        'school',
        'school__name',
        'meeting_name',
        'meeting_date',
        'number_participants',
        'owner__username',
        'modified_by__username',
        'created',
        'modified'
    )

    for row in rows_meeting:
        row_num_meeting += 1
        for col_num in range(len(row)):
            ws_meeting.write(row_num_meeting, col_num, row[col_num], font_style)

    # Community Initiative
    ws_community_initiative = wb_school.add_sheet('Community Initiative')
    row_num_community_initiative = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column_header_community_initiative = [
        'id',
        'School ID',
        'School Name',
        'Community Group Name',
        'Number of Initiatives',
        'Owner',
        'Modified By',
        'Created',
        'Modified'
    ]

    for col_num in range(len(column_header_community_initiative)):
        ws_community_initiative.write(row_num_community_initiative, col_num, column_header_community_initiative[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows_community_initiative = qs_community_initiative.values_list(
        'id',
        'school',
        'school__name',
        'community_group_name',
        'number_initiatives',
        'owner__username',
        'modified_by__username',
        'created',
        'modified'
    )

    for row in rows_community_initiative:
        row_num_community_initiative += 1
        for col_num in range(len(row)):
            ws_community_initiative.write(row_num_community_initiative, col_num, row[col_num], font_style)

    # Health Visit
    ws_health_visit = wb_school.add_sheet('Health Visit')
    row_num_health_visit = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    column_header_health_visit = [
        'id',
        'School ID',
        'School Name',
        'Health Focal Point Name',
        'Number of Visits',
        'Date of First Visit',
        'Date of Last Visit',
        'Summary',
        'Owner',
        'Modified By',
        'Created',
        'Modified'
    ]

    for col_num in range(len(column_header_health_visit)):
        ws_health_visit.write(row_num_health_visit, col_num, column_header_health_visit[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows_health_visit = qs_health_visit.values_list(
        'id',
        'school',
        'school__name',
        'focal_point_name',
        'number_visits',
        'date_first_visit',
        'date_last_visit',
        'summary',
        'owner__username',
        'modified_by__username',
        'created',
        'modified'
    )

    for row in rows_health_visit:
        row_num_health_visit += 1
        for col_num in range(len(row)):
            ws_health_visit.write(row_num_health_visit, col_num, row[col_num], font_style)
    wb_school.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = FileResponse(buffer, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="School.xls"'

    return response

