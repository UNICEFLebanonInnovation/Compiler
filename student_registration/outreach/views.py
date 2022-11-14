# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from rest_framework.response import Response
import requests
from requests.structures import CaseInsensitiveDict
import json
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
    last_loaded_identifier = 359960452
    last_loaded_identifier_str = str(last_loaded_identifier)

    url = "https://kobo.humanitarianresponse.info/api/v2/assets/a7op9fLp3qAhusYT4CgVvH/data.json?sort=%7B%22_id%22%3A+1%7D&query=%7B%22_id%22%3A+%7B%22%24gt%22%3A+" + last_loaded_identifier_str + "%7D%7D"

    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Token 38ebfd9d7f948c67a1fb3d9249c4111c97bcb12d"
    # sort = {"_id": 1} & query = {"_id": {"$gt": 359960452}}
    resp = requests.get(url, headers=headers)

    print(resp.status_code)

    data = json.loads(resp.text)
    for x in data["results"]:
        form_id = x["_id"]
        print(form_id)
        h = HouseHold(form_id=form_id)
        h.save()
        print('saves successfiulllly')
    return HttpResponse("Hello World")


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



