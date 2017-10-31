
import datetime
import json
import os
from datetime import datetime

import requests
from django.conf import settings
from django.db import connection
from requests.auth import HTTPBasicAuth
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
