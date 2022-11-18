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
    last_loaded_identifier = HouseHold.objects.aggregate(Max('u_id'))['u_id__max']
    if last_loaded_identifier is None:
        last_loaded_identifier = 0
    last_loaded_identifier_str = str(last_loaded_identifier)
    url = "https://kobo.humanitarianresponse.info/api/v2/assets/a7op9fLp3qAhusYT4CgVvH/data.json?sort=%7B%22_id%22%3A+1%7D&query=%7B%22_id%22%3A+%7B%22%24gt%22%3A+" + last_loaded_identifier_str + "%7D%7D"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Token 38ebfd9d7f948c67a1fb3d9249c4111c97bcb12d"
    resp = requests.get(url, headers=headers)
    data = json.loads(resp.text)
    for x in data["results"]:
        h = HouseHold()
        h.u_id = x["_id"]
        h.form_id = x["_xform_id_string"]
        h.governorate = x["Governorate"]
        h.district = x["Districts"]
        h.cadaster = x["Cadaster"]
        h.address = x["address"]
        if x.has_key('gps'):
            h.gps = x["gps"]
        elif x.has_key('GPS'):
            h.gps = x["GPS"]
        h.phone_number = x["primary_phone"]
        h.main_caregiver = x["caretaker"]
        h.caregiver_nationality = x["caretaker_nationality"]
        h.caregiver_first_name = x["father"]
        h.caretaker_middle_name = x["caretaker_father"]
        h.caretaker_last_name = x["family"]
        h.caretaker_mother_name = x["caretaker_mother"]
        h.caretaker_dob = x["caretaker_dob"]
        h.mother_fullname = x["mother"]
        # h.number_of_children = x["Q1"]
        h.geolocation = x["_geolocation"]
        h.interview_date = x["_submission_time"]
        h.submitted_by = x["_submitted_by"]
        h.interview_comment = x["_notes"]
        h.save()
        caregiver__id = h.id
        for c in x["DC"]:
            st = Child()
            st.household = h
            st.first_name = c["DC/name"]
            st.dob = c["DC/date_of_birth"]
            st.sex = c["DC/gender"]
            st.disability_type = c["DC/dis"]
            st.save()

    return HttpResponse("records saved successfully")


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



