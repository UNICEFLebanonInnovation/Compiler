
from student_registration.taskapp.celery import app

import json
import datetime
from time import mktime


@app.task
def link_household_to_children():
    from .models import HouseHold, Child

    households = HouseHold.objects.all()
    for hh in households:
        ctr = 0
        children = Child.objects.filter(form_id=hh.form_id)
        for child in children:
            ctr += 1
            child.barcode_subset = '{}-{}'.format(hh.barcode_number, ctr)
            child.household = hh
            child.save()


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

    def decode(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)
