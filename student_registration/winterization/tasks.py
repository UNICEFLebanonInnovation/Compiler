
import json
import os
import tablib

import requests
from django.conf import settings
from django.db import connection
from requests.auth import HTTPBasicAuth
from import_export.formats import base_formats
from student_registration.taskapp.celery import app


@app.task
def cleanup_old_data():
    from .models import Beneficiary

    registrations = Beneficiary.objects.all()
    print(registrations.count())
    registrations.delete()


def set_docs(docs):

    payload_json = json.dumps(
        {
            'docs': docs,
            'all_or_nothing': True
        }
    )
    path = os.path.join(settings.COUCHBASE_URL, '_bulk_docs')
    response = requests.post(
        path,
        headers={'content-type': 'application/json'},
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS),
        data=payload_json,
    )
    return response


@app.task
def set_app_user(username, password):

    user_docs = []
    user_docs.append(
        {
            "_id": username,
            "type": "user",
            "username": username,
            "password": password,
            "organisation": username,
        }
    )

    response = set_docs(user_docs)
    return response.text


@app.task
def import_docs(**kwargs):
    """
    Imports docs from couch base
    """
    from .models import Assessment
    from .serializers import AssessmentSerializer

    data = requests.get(
        os.path.join(settings.COUCHBASE_URL, '_all_docs?include_docs=true'),
        auth=HTTPBasicAuth(settings.COUCHBASE_USER, settings.COUCHBASE_PASS)
    ).json()

    for row in data['rows']:
        if 'doc' in row:
            doc = row['doc']
            doc['site_type'] = doc['site-type'] if 'site-type' in doc else ''
            # todo assistance_type fix the return type
            serializer = AssessmentSerializer(data=doc)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.save()
            else:
                print(serializer.errors)
                print(json.dumps(doc))


@app.task
def calculate_disaggregation():
    from .models import Assessment

    queryset = Assessment.objects.filter(child_list__isnull=False)
    print(queryset.count())

    for line in queryset:
        data = line.child_list
        line._0_to_3_months = find_total(data=data, name='age', value='0 to 3 months')
        line._3_to_12_months = find_total(data=data, name='age', value='3 to 12 months')
        line._1_year_old = find_total(data=data, name='age', value='1 year old')
        line._2_years_old = find_total(data=data, name='age', value='2 years old')
        line._3_years_old = find_total(data=data, name='age', value='3 years old')
        line._4_years_old = find_total(data=data, name='age', value='4 years old')
        line._5_years_old = find_total(data=data, name='age', value='5 years old')
        line._6_years_old = find_total(data=data, name='age', value='6 years old')
        line._7_years_old = find_total(data=data, name='age', value='7 years old')
        line._8_years_old = find_total(data=data, name='age', value='8 years old')
        line._9_years_old = find_total(data=data, name='age', value='9 years old')
        line._10_years_old = find_total(data=data, name='age', value='10 years old')
        line._11_years_old = find_total(data=data, name='age', value='11 years old')
        line._12_years_old = find_total(data=data, name='age', value='12 years old')
        line._13_years_old = find_total(data=data, name='age', value='13 years old')
        line._14_years_old = find_total(data=data, name='age', value='14 years old')
        line.male = find_total(data=data, name='gender', value='Boy')
        line.female = find_total(data=data, name='gender', value='Girl')
        line._3_months_kit = find_total(data=data, name='kit', value='3 months')
        line._12_months_kit = find_total(data=data, name='kit', value='12 months')
        line._2_years_kit = find_total(data=data, name='kit', value='2 years')
        line._3_years_kit = find_total(data=data, name='kit', value='3 years')
        line._5_years_kit = find_total(data=data, name='kit', value='5 years')
        line._7_years_kit = find_total(data=data, name='kit', value='7 years')
        line._9_years_kit = find_total(data=data, name='kit', value='9 years')
        line._12_years_kit = find_total(data=data, name='kit', value='12 years')
        line._14_years_kit = find_total(data=data, name='kit', value='14 years')
        line._3_months_kit_completed = find_total(data=data, name='kit', value='3 months', status_condition='COMPLETED')
        line._12_months_kit_completed = find_total(data=data, name='kit', value='12 months', status_condition='COMPLETED')
        line._2_years_kit_completed = find_total(data=data, name='kit', value='2 years', status_condition='COMPLETED')
        line._3_years_kit_completed = find_total(data=data, name='kit', value='3 years', status_condition='COMPLETED')
        line._5_years_kit_completed = find_total(data=data, name='kit', value='5 years', status_condition='COMPLETED')
        line._7_years_kit_completed = find_total(data=data, name='kit', value='7 years', status_condition='COMPLETED')
        line._9_years_kit_completed = find_total(data=data, name='kit', value='9 years', status_condition='COMPLETED')
        line._12_years_kit_completed = find_total(data=data, name='kit', value='12 years', status_condition='COMPLETED')
        line._14_years_kit_completed = find_total(data=data, name='kit', value='14 years', status_condition='COMPLETED')
        line.Q1 = find_total(data=data, name='age', value='Q1')
        line.Q2 = find_total(data=data, name='age', value='Q2')
        line.Q3 = find_total(data=data, name='age', value='Q3')

        line.save()


def find_total(data, name, value, status_condition=None):
    ctr = 0
    for item in data:
        if status_condition:
            if item['status'] == status_condition and item[name] == value:
                ctr += 1
        elif item[name] == value:
            ctr += 1
    return ctr


def export_data():
    from .models import Assessment
    # from student_registration.backends.

    queryset = Assessment.objects.all()

    data = tablib.Dataset()
    data.headers = [
        '_id',
        'p_code',
        'p_code_name',
        'district',
        'cadastral',
        'location_type',
        'assistance_type',
        'phone_number',
        'phone_owner',
        'latitude',
        'longitude',
        'first_name',
        'middle_name',
        'last_name',
        'mothers_name',
        'relationship_type',
        'family_count',
        'disabilities',
        'official_id',
        'gender',
        'dob',
        'marital_status',
        'creation_date',
        'completion_date',
        'partner_name',
        'moving_location',
        'new_district',
        'new_cadastral',
        '0 to 3 months',
        '3 to 12 months',
        '1 year old',
        '2 years old',
        '3 years old',
        '4 years old',
        '5 years old',
        '6 years old',
        '7 years old',
        '8 years old',
        '9 years old',
        '10 years old',
        '11 years old',
        '12 years old',
        '13 years old',
        '14 years old',
        'male',
        'female',
        '3 months kit',
        '12 months kit',
        '2 years kit',
        '3 years kit',
        '5 years kit',
        '7 years kit',
        '9 years kit',
        '12 years kit',
        '14 years kit',
        '3 months kit Completed',
        '12 months kit Completed',
        '2 years kit Completed',
        '3 years kit Completed',
        '5 years kit Completed',
        '7 years kit Completed',
        '9 years kit Completed',
        '12 years kit Completed',
        '14 years kit Completed',
        'Q1',
        'Q2',
        'Q3'
    ]

    content = []
    for line in queryset:
        content = [
            line._id,
            line.location_p_code,
            line.location_p_code_name,
            line.district,
            line.cadastral,
            line.location_type,
            line.locations_type,
            line.assistance_type,
            line.phone_number,
            line.phone_owner,
            line.latitude,
            line.longitude,
            line.first_name,
            line.middle_name,
            line.last_name,
            line.mothers_name,
            line.relationship_type,
            line.family_count,
            line.disabilities,
            line.official_id,
            line.gender,
            line.dob,
            line.marital_status,
            line.creation_date,
            line.completion_date,
            line.partner_name,
            line.moving_location,
            line.new_district,
            line.new_cadastral,
            line._0_to_3_months,
            line._3_to_12_months,
            line._1_year_old,
            line._2_years_old,
            line._3_years_old,
            line._4_years_old,
            line._5_years_old,
            line._6_years_old,
            line._7_years_old,
            line._8_years_old,
            line._9_years_old,
            line._10_years_old,
            line._11_years_old,
            line._12_years_old,
            line._13_years_old,
            line._14_years_old,
            line.male,
            line.female,
            line._3_months_kit,
            line._12_months_kit,
            line._2_years_kit,
            line._3_years_kit,
            line._5_years_kit,
            line._7_years_kit,
            line._9_years_kit,
            line._12_years_kit,
            line._14_years_kit,
            line._3_months_kit_completed,
            line._12_months_kit_completed,
            line._2_years_kit_completed,
            line._3_years_kit_completed,
            line._5_years_kit_completed,
            line._7_years_kit_completed,
            line._9_years_kit_completed,
            line._12_years_kit_completed,
            line._14_years_kit_completed,
            line.Q1,
            line.Q2,
            line.Q3,
        ]

        data.append(content)

    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    #'aafaour@unicef.org'
