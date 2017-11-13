
from student_registration.taskapp.celery import app

import json
import random
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from openpyxl import load_workbook

from student_registration.backends.utils import post_data


@app.task
def push_bln_data(file_name, base_url, token, protocol='HTTPS'):

    # from .models import BLN
    # objects = BLN.objects.all()
    # objects.delete()

    # LEARNING_RESULT = ['repeat_level', 'attended_public_school', 'dropout',
    #                    'referred_to_alp', 'ready_to_alp_but_not_possible',
    #                    'reenrolled_in_alp', 'not_enrolled_any_program']

    PARTICIPATION = ['less_than_5days', '5_10_days',
                     '10_15_days', 'more_than_15days']

    wb = load_workbook(filename=file_name, read_only=True)
    for ws in wb:
        for row in ws.rows:
            try:
                data = {}
                data['new_registry'] = 'yes'
                data['student_outreached'] = 'no'
                data['have_barcode'] = 'no'
                data['partner'] = row[0].value
                data['round_id'] = row[1].value if row[1].value else 1
                data['student_first_name'] = row[2].value if row[2].value else 'None'
                data['student_father_name'] = row[3].value if row[3].value else 'None'
                data['student_mother_fullname'] = row[4].value if row[4].value else 'None'
                data['student_last_name'] = row[5].value if row[5].value else 'None'
                data['student_sex'] = row[6].value if row[6].value else 'Male'
                data['student_nationality'] = row[7].value if row[7].value else 1
                data['student_birthday_year'] = row[8].value if row[8].value else 2009
                # birthday_year = datetime.strptime(data['student_birthday_year'], '%Y-%m-%d')
                # print(birthday_year.year)
                # print(birthday_year.month)
                # print(birthday_year.day)
                data['student_birthday_month'] = 1
                data['student_birthday_day'] = 1
                data['governorate'] = row[9].value
                data['district'] = row[10].value
                data['learning_result'] = row[19].value
                data['participation'] = random.choice(PARTICIPATION)

                result = post_data(protocol=protocol, url=base_url, apifunc='/api/clm-bln/', token=token, data=data)
                result = json.loads(result)

                try:
                    assessment = {}
                    assessment['status'] = 'pre_test'
                    assessment['enrollment_id'] = result['id']
                    assessment['enrollment_model'] = 'BLN'
                    assessment['BLN_ASSESSMENT/arabic'] = row[11].value if row[11].value else '0'
                    assessment['BLN_ASSESSMENT/english'] = row[12].value if row[12].value else '0'
                    assessment['BLN_ASSESSMENT/french'] = row[13].value if row[13].value else '0'
                    assessment['BLN_ASSESSMENT/math'] = row[14].value if row[14].value else '0'

                    post_data(protocol=protocol, url=base_url, apifunc='/clm/assessment-submission/', token=token,
                              data=assessment)
                except Exception as ex:
                    print("---------------")
                    print("error: ", ex.message)
                    print(json.dumps(assessment, cls=DjangoJSONEncoder))
                    print("---------------")
                    pass

                try:
                    assessment = {}
                    assessment['status'] = 'post_test'
                    assessment['enrollment_id'] = result['id']
                    assessment['enrollment_model'] = 'BLN'
                    assessment['BLN_ASSESSMENT/arabic'] = row[15].value if row[15].value else '0'
                    assessment['BLN_ASSESSMENT/english'] = row[16].value if row[16].value else '0'
                    assessment['BLN_ASSESSMENT/french'] = row[17].value if row[17].value else '0'
                    assessment['BLN_ASSESSMENT/math'] = row[18].value if row[18].value else '0'

                    post_data(protocol=protocol, url=base_url, apifunc='/clm/assessment-submission/', token=token,
                              data=assessment)
                except Exception as ex:
                    print("---------------")
                    print("error: ", ex.message)
                    print(json.dumps(assessment, cls=DjangoJSONEncoder))
                    print("---------------")
                    pass

            except Exception as ex:
                print("---------------")
                print("error: ", ex.message)
                print(json.dumps(data, cls=DjangoJSONEncoder))
                print("---------------")
                continue
