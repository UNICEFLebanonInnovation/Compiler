# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from rest_framework import viewsets, mixins, permissions

from .models import Location

from .serializers import LocationSerializer

#
# from dal import autocomplete
# from django.db.models import Q
#
# from .models import (
#     Student,
# )
# from .serializers import (
#     StudentSerializer,
# )
# from student_registration.enrollments.models import (
#     EducationYear
# )
# from student_registration.alp.models import ALPRound



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
