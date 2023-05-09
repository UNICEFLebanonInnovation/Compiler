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
        print(ex.message)
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
        print(ex.message)
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


class SchoolResource(resources.ModelResource):
    class Meta:
        model = School
        fields = (
            'id',

            'id',
            'number',
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
            'is_first_shift',
            'working_days',
            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'number_dirasa_children_disability',
            'number_total_children_disability',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )
        export_order = fields

