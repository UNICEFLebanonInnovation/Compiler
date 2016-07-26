# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions

from .models import (
    Student,
    School,
    ClassRoom,
    Section,
    Grade
)

from .serializers import (
    StudentSerializer,
    SchoolSerializer,
    ClassRoomSerializer,
    SectionSerializer,
    GradeSerializer
)


class SchoolDetailJson(LoginRequiredMixin, DetailView):
    model = School

    def get(self, request, *args, **kwargs):
        instance = School.objects.get(id=request.GET.get('id'))
        return JsonResponse({'result': 'OK', 'number': instance.number})


class StudentViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Student
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SchoolViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    model = School
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ClassRoomViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    model = ClassRoom
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SectionViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    model = Section
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class GradeViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    model = Grade
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = (permissions.IsAuthenticated,)
