# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from datetime import datetime
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats

from .models import Attribute, Value
from .serializers import AttributeSerializer, ValueSerializer


class AttributeViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):

    model = Attribute
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        try:
            queryset = self.queryset.filter(type=self.request.GET['type'], shared=True)
        except Exception as exp:
            print exp.message
            queryset = []

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        data = []
        for item in queryset:
            data.append({
                "id": item.id,
                "name": item.slug,
                "label": item.name,
                "original_id": item.id,
                "owner": item.owner.id
            })

        return JsonResponse({'status': status.HTTP_200_OK, 'data': data})

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        data = {
            "name": request.data['label'],
            "slug": request.data['name'],
            "type": request.data['type'],
            "datatype": "text",
            "site": 1,
            "owner": request.data['owner']
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})


class ValueViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):

    model = Value
    queryset = Value.objects.all()
    serializer_class = ValueSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        :return: JSON
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance = serializer.save()

        return JsonResponse({'status': status.HTTP_201_CREATED, 'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def update(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        return JsonResponse({'status': status.HTTP_200_OK})
