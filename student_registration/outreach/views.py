# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from dal import autocomplete
from django.db.models import Q
from .models import HouseHold, Child
from .serializers import HouseHoldSerializer, ChildSerializer


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


class ExportView(LoginRequiredMixin, ListView):

    model = Child
    queryset = Child.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats
        from django.utils.translation import ugettext as _

        disabilities = (
                ('Walking', _('Walking')),
                ('Seeing', _('Seeing')),
                ('Hearing', _('Hearing')),
                ('Speaking', _('Speaking')),
                ('Self_Care', _('Self Care')),
                ('Learning', _('Learning')),
                ('Interacting', _('Interacting')),
                ('Other', _('Other')),
            )

        partners = Child.objects.order_by('sex').values_list('sex').distinct()
        print(partners)
        print(len(partners))

        data = tablib.Dataset()
        data.headers = [
            'sex',
            'disability',
            'count',
        ]

        queryset = self.queryset

        content = []
        for partner in partners:
            for cls in disabilities:
                nbr_cls = self.queryset.filter(
                    disability_type__contains=[cls[0]],
                    sex=partner[0]).count()

                content = [
                    partner[0],
                    cls[0],
                    nbr_cls,
                ]
                data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        return response


class Export2View(LoginRequiredMixin, ListView):

    model = Child
    queryset = Child.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats
        from django.utils.translation import ugettext as _

        referrals = (
                ('1', _('Referral_Reason 1')),
                ('2', _('Referral_Reason 2')),
                ('3', _('Referral_Reason 3')),
                ('4', _('Referral_Reason 4')),
                ('5', _('Referral_Reason 5')),
                ('6', _('Referral_Reason 6')),
                ('7', _('Referral_Reason 7')),
                ('8', _('Referral_Reason 8')),
                ('9', _('Referral_Reason 9')),
                ('10', _('Referral_Reason 10')),
                ('11', _('Referral_Reason 11')),
                ('12', _('Referral_Reason 12')),
                ('13', _('Referral_Reason 13')),
                ('14', _('Referral_Reason 14')),
                ('15', _('Referral_Reason 15')),
            )

        partners = Child.objects.order_by('sex').values_list('sex').distinct()
        print(partners)
        print(len(partners))

        data = tablib.Dataset()
        data.headers = [
            'sex',
            'referrals',
            'count',
        ]

        queryset = self.queryset

        content = []
        for partner in partners:
            for cls in referrals:
                nbr_cls = self.queryset.filter(
                    referral_reason__contains=[cls[0]],
                    sex=partner[0]).count()

                content = [
                    partner[0],
                    cls[0],
                    nbr_cls,
                ]
                data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        return response


class Export3View(LoginRequiredMixin, ListView):

    model = Child
    queryset = Child.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats
        from django.utils.translation import ugettext as _

        items = Child.objects.order_by('nationality').values_list('nationality').distinct()

        data = tablib.Dataset()
        data.headers = [
            'nationality',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:
            nbr_cls = HouseHold.objects.filter(outreach_children__nationality=item[0]).distinct().count()

            content = [
                item[0],
                nbr_cls,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        return response


class Export4View(LoginRequiredMixin, ListView):

    model = Child
    queryset = Child.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats
        from django.utils.translation import ugettext as _

        barriers = (
                ('1', _('Reason 1')),
                ('2', _('Reason 2')),
                ('3', _('Reason 3')),
                ('4', _('Reason 4')),
                ('5', _('Reason 5')),
                ('6', _('Reason 6')),
                ('7', _('Reason 7')),
                ('8', _('Reason 8')),
                ('9', _('Reason 9')),
                ('10', _('Reason 10')),
                ('11', _('Reason 11')),
                ('12', _('Reason 12')),
                ('13', _('Reason 13')),
                ('14', _('Reason 14')),
                ('15', _('Reason 15')),
                ('16', _('Reason 16')),
                ('17', _('Reason 17')),
                ('18', _('Reason 18')),
            )

        items = Child.objects.order_by('nationality').values_list('nationality').distinct()

        data = tablib.Dataset()
        data.headers = [
            'nationality',
            'barriers',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:
            for cls in barriers:
                nbr_cls = self.queryset.filter(
                    last_edu_system__in=['Prv. NFE prg. did not continue', 'Prv. formal edu., did not continue'],
                    not_enrolled_reasons__contains=[cls[0]],
                    nationality=item[0]).count()

                content = [
                    item[0],
                    cls[0],
                    nbr_cls,
                ]
                data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        return response
