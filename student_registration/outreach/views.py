# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from rest_framework.response import Response
import requests
from requests.structures import CaseInsensitiveDict
import json
from django.db.models import Max
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from dal import autocomplete
from django.db.models import Q
from .models import HouseHold, Child
from .serializers import HouseHoldSerializer, ChildSerializer
import datetime


def outreach_import_data(request):
    last_loaded_identifier = 0

    # last_loaded_identifier = HouseHold.objects.aggregate(Max('u_id'))['u_id__max']
    # if last_loaded_identifier is None:
    #     last_loaded_identifier = 0
    last_loaded_identifier_str = str(last_loaded_identifier)
    url = "https://kobo.humanitarianresponse.info/api/v2/assets/aSg3ARiCkQ4fZCWQR3Wceo/data.json?sort=%7B%22_id%22%3A+1%7D&query=%7B%22_id%22%3A+%7B%22%24gt%22%3A+" + last_loaded_identifier_str + "%7D%7D"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Token 38ebfd9d7f948c67a1fb3d9249c4111c97bcb12d"
    resp = requests.get(url, headers=headers)
    data = json.loads(resp.text)

    for record in data["results"]:
        # for k, v in record.items():
        #     print(k, v)
        h = HouseHold()
        h.u_id = record["_id"]
        h.form_id = record["_xform_id_string"]
        record_value(h, "partner_name", record, "partner_name")
        record_value(h, "governorate", record, "Governorate")
        record_value(h, "district", record, "Districts")
        record_value(h, "cadaster", record, "Cadaster")
        record_value(h, "cadaster_other_specify", record, "cadaster_other_specify")
        record_value(h, "address", record, "address")
        record_value(h, "gps", record, "gps")
        record_value(h, "phone_number", record, "primary_phone")
        record_value(h, "secondary_phone", record, "secondary_phone")
        record_value(h, "father_name", record, "father_name")
        record_value(h, "mother_fullname", record, "mother_full_name")
        record_value(h, "last_name", record, "last_name")
        record_value(h, "main_caregiver", record, "main_caregiver")
        record_value(h, "caregiver_nationality", record, "caregiver_nationality")
        record_value(h, "caregiver_nationality_other", record, "caregiver_nationality_other")
        record_value(h, "caregiver_first_name", record, "caregiver_first_name")
        record_value(h, "caregiver_father_name", record, "caregiver_father_name")
        record_value(h, "caregiver_mother_name", record, "caregiver_mother")
        record_value(h, "caregiver_last_name", record, "caregiver_last_name")
        record_value(h, "caregiver_dob", record, "caregiver_dob")
        record_value(h, "gps", record, "id_type")
        record_value(h, "gps", record, "cash_assistance")
        record_value(h, "gps", record, "caretaker_personal_id")
        record_value(h, "gps", record, "other_education_level")
        record_value(h, "number_of_children", record, "DC_count")
        record_value(h, "interview_comment", record, "child_notes")
        record_value(h, "geolocation", record, "_geolocation")
        record_value(h, "interview_date", record, "_submission_time")
        record_value(h, "submitted_by", record, "_submitted_by")
        h.save()
        # caregiver_id = h.id
        if record.has_key("DC"):
            for c in record["DC"]:
                st = Child()
                st.household = h
                st.first_name = c["DC/first_name"]
                st.dob = c["DC/date_of_birth"]
                st.sex = c["DC/gender"]
                # "DC/nationality": "other",
                # "DC/nationality_other": "س",
                # "DC/child_personal_id": "3",
                # "DC/family_status": "Separated",
                # "DC/disability": "Other",
                # "DC/disability_other": "ص",
                # "DC/education_status": "Previously_enrolled_in_Non-formal_educat",
                # "DC/dropout_date": "2022-11-30",
                # "DC/dropout_reason": "other_reasons",
                # "DC/dropout_reason_other": "س",
                # "DC/working_status": "yes",
                # "DC/work_type": "others",
                # "DC/work_type_other": "س",
                # "DC/child_referral": "TEVET"

                st.disability_type = c["DC/dis"]
                st.save()

    return HttpResponse("records saved successfully")

def record_value(household,household_field,record, field):
    if record.has_key(field):
        household.household_field = record[field]

class HouseHoldViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):

    model = HouseHold
    queryset = HouseHold.objects.all()
    serializer_class = HouseHoldSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        term = self.request.GET.get('term', 0)
        if term:
            qs = self.queryset.filter(barcode_number=term).distinct()
            return qs
        return []


class ChildViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):

    model = Child
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        term = self.request.GET.get('term', 0)
        if term:
            qs = self.queryset.filter(barcode_subset__contains=term).distinct()
            return qs
        return []



