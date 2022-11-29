# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from rest_framework import viewsets, mixins, permissions

from .models import Location

from .serializers import LocationSerializer

####################### API VIEWS #############################


class LocationViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset


def load_districts(request):
    id_governorate = request.GET.get('id_governorate')
    cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    id_district = request.GET.get('id_district')
    cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    id_governorate = request.GET.get('id_governorate')
    schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})
