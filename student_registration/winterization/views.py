# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from rest_framework import status
from .models import Beneficiary
from .serializers import BeneficiarySerializer


class BeneficiaryViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    model = Beneficiary
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        string = request.GET.get("term", 0)
        limit = request.GET.get("limit", 0)
        offset = 0

        queryset = self.queryset.filter(case_number__contains=string)[offset:limit]

        data = []
        for item in queryset:
            data.append({
                "case_number": item.case_number,
                "registration_status": item.registration_status,
                "location_type": item.location_type,
                "governorate": item.governorate,
                "district": item.district,
                "cadastral": item.cadastral,
                "phone_number": item.phone_number,
                "total_children": item.total_children,
                "card_distributed": item.card_distributed,
                "card_loaded": item.card_loaded,
                "amount": item.amount,
            })

        return JsonResponse({'data': data})
