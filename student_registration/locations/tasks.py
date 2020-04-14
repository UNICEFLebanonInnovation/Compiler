
from student_registration.taskapp.celery import app

import json
from django.core.serializers.json import DjangoJSONEncoder
from openpyxl import load_workbook
from student_registration.backends.utils import post_data


@app.task
def push_cadaster_data(file_name, base_url, token, protocol='HTTPS'):
    wb = load_workbook(filename='test.XLSX', read_only=True)
    ws = wb['Cadasters']

    for row in ws.rows:
        if row[0].value == 'skip':
            continue
        try:
            data = {}
            data['name'] = row[1].value
            data['id'] = row[2].value
            data['name_en'] = row[3].value
            data['type_id'] = row[4].value
            data['parent_id'] = row[5].value
            print("---------------")
            result = post_data(protocol=protocol, url=base_url, apifunc='/api/locations', token=token, data=data)
            print(result)
            result = json.loads(result)
            print(result)

        except Exception as ex:
            print("---------------")
            print("error: ", ex.message)
            print(json.dumps(data, cls=DjangoJSONEncoder))
            print("---------------")
            continue


