# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import datetime
import json

from django.views import View
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render

from braces.views import GroupRequiredMixin
from rest_framework import viewsets, mixins, permissions
from rest_framework.generics import ListAPIView
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):

    model = Notification
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # def update(self, request, *args, **kwargs):
    #     if 'pk' not in kwargs:
    #         return super(NotificationViewSet, self).update(request)
    #     instance = self.model.objects.get(id=kwargs['pk'])
    #     print(request)
    #     instance.status = True
    #     instance.save()
    #     return JsonResponse({'status': status.HTTP_200_OK, 'data': instance.id})
