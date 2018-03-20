# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
from dal import autocomplete
from django.db.models import Q
from .models import HouseHold, Child, Child2
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

    model = Child2
    queryset = Child2.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats

        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        # items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            # 'partner_name',
            'governorate',
            # 'nationality',
            # 'sex',
            # 'age',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:
            qs = queryset.filter(
                # calculated_age=item[0],
                # household__partner_name=item[0]
                household__governorate=item[0]
                # nationality_id=item[0]
                # sex=item[0]
            )
            nbr_cls = qs.filter(
                Q(disability_type__contains=['Walking']) |
                Q(disability_type__contains=['Seeing']) |
                Q(disability_type__contains=['Hearing']) |
                Q(disability_type__contains=['Speaking']) |
                Q(disability_type__contains=['Self_Care']) |
                Q(disability_type__contains=['Learning']) |
                Q(disability_type__contains=['Interacting']) |
                Q(disability_type__contains=['Other'])
            ).count()

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


class Export1View(LoginRequiredMixin, ListView):

    model = Child2
    queryset = Child2.objects.all()

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

        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        # items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            'disability',
            # 'partner_name',
            'governorate',
            # 'nationality',
            # 'sex',
            # 'age',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:

            for bar in disabilities:
                nbr_cls = self.queryset.filter(
                    # household__partner_name=item[0],
                    household__governorate=item[0],
                    # nationality_id=item[0],
                    # sex=item[0],
                    # calculated_age=item[0],
                    disability_type__contains=[bar[0]]
                ).count()

                content = [
                    bar[0],
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


class Export2View(LoginRequiredMixin, ListView):

    model = Child2
    queryset = Child2.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats

        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        # items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            # 'partner_name',
            # 'governorate',
            # 'nationality',
            # 'sex',
            'age',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:
            qs = queryset.filter(
                # household__partner_name=item[0]
                # household__governorate=item[0]
                # nationality_id=item[0]
                # sex=item[0]
                calculated_age=item[0]
            )

            nbr_cls = qs.filter(
                Q(referral_reason__contains=['1']) |
                Q(referral_reason__contains=['2']) |
                Q(referral_reason__contains=['3']) |
                Q(referral_reason__contains=['4']) |
                Q(referral_reason__contains=['5']) |
                Q(referral_reason__contains=['6']) |
                Q(referral_reason__contains=['7']) |
                Q(referral_reason__contains=['8']) |
                Q(referral_reason__contains=['9']) |
                Q(referral_reason__contains=['10']) |
                Q(referral_reason__contains=['11']) |
                Q(referral_reason__contains=['12']) |
                Q(referral_reason__contains=['13']) |
                Q(referral_reason__contains=['14']) |
                Q(referral_reason__contains=['15'])
            ).count()

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


class Export2aView(LoginRequiredMixin, ListView):

    model = Child2
    queryset = Child2.objects.all()

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

        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        # items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            'referral',
            # 'partner_name',
            # 'governorate',
            # 'nationality',
            # 'sex',
            'age',
            'count',
        ]

        queryset = self.queryset

        content = []
        for item in items:
            for bar in referrals:
                nbr_cls = self.queryset.filter(
                    # household__partner_name=item[0],
                    # household__governorate=item[0],
                    # nationality_id=item[0],
                    # sex=item[0],
                    calculated_age=item[0],
                    referral_reason__contains=[bar[0]]
                ).count()

                content = [
                    bar[0],
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

    model = Child2
    queryset = Child2.objects.all()

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

        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        # items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            # 'partner_name',
            # 'governorate',
            # 'nationality',
            # 'sex',
            'age',
            'count',
        ]

        content = []
        for item in items:
            queryset = self.queryset.filter(
                # last_edu_system__in=['Prv. NFE prg. did not continue', 'Prv. formal edu., did not continue'],
                # last_edu_system='Never been to school',
                # household__partner_name=item[0]
                # household__governorate=item[0]
                # nationality_id=item[0]
                # sex=item[0]
                calculated_age=item[0]
            )

            nbr_cls = queryset.filter(
                Q(not_enrolled_reasons__contains=['1']) |
                Q(not_enrolled_reasons__contains=['2']) |
                Q(not_enrolled_reasons__contains=['3']) |
                Q(not_enrolled_reasons__contains=['4']) |
                Q(not_enrolled_reasons__contains=['5']) |
                Q(not_enrolled_reasons__contains=['6']) |
                Q(not_enrolled_reasons__contains=['7']) |
                Q(not_enrolled_reasons__contains=['8']) |
                Q(not_enrolled_reasons__contains=['9']) |
                Q(not_enrolled_reasons__contains=['10']) |
                Q(not_enrolled_reasons__contains=['11']) |
                Q(not_enrolled_reasons__contains=['12']) |
                Q(not_enrolled_reasons__contains=['13']) |
                Q(not_enrolled_reasons__contains=['14']) |
                Q(not_enrolled_reasons__contains=['15']) |
                Q(not_enrolled_reasons__contains=['16']) |
                Q(not_enrolled_reasons__contains=['17']) |
                Q(not_enrolled_reasons__contains=['18'])
            ).count()

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


class Export4aView(LoginRequiredMixin, ListView):

    model = Child2
    queryset = Child2.objects.all()

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

        items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('sex').values_list('sex').distinct()
        # items = Child2.objects.order_by('calculated_age').values_list('calculated_age').distinct()
        # items = HouseHold.objects.order_by('partner_name').values_list('partner_name').distinct()
        # items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            'barrier',
            # 'partner_name',
            # 'governorate',
            'nationality',
            # 'sex',
            # 'age',
            'count',
        ]

        content = []
        for item in items:
            for bar in barriers:
                nbr_cls = self.queryset.filter(
                    last_edu_system__in=['Prv. NFE prg. did not continue', 'Prv. formal edu., did not continue'],
                    # last_edu_system='Never been to school',
                    # household__partner_name=item[0],
                    # household__governorate=item[0],
                    nationality_id=item[0],
                    # sex=item[0],
                    # calculated_age=item[0],
                    not_enrolled_reasons__contains=[bar[0]]
                ).count()

                content = [
                    bar[0],
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


class Export5View(LoginRequiredMixin, ListView):

    model = Child2
    queryset = Child2.objects.all()

    def get(self, request, *args, **kwargs):
        import tablib
        from import_export.formats import base_formats
        from django.utils.translation import ugettext as _
        from student_registration.students.models import CrossMatching

        items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = Child2.objects.order_by('nationality_id').values_list('nationality_id').distinct()
        # items = HouseHold.objects.order_by('governorate').values_list('governorate').distinct()

        data = tablib.Dataset()
        data.headers = [
            'nationality',
            'count',
        ]

        queryset = CrossMatching.objects.all()

        content = []
        for item in items:
            nbr_cls = queryset.filter(
                program_type='2nd-shift',
                educatiob_level__in=['2', '3', '4', '5', '6', '7', '8', '9', '10'],
                child__nationality_id=item[0]
            ).count()

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
