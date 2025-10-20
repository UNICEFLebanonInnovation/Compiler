# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
from collections import Counter

from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    TemplateView,
    FormView,
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Count, F
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection
import csv
import io
import zipfile
import codecs
from django.utils import timezone
from django.utils.encoding import smart_str
import traceback

from rest_framework import status
from django.db.models import F, Q, OuterRef, Exists, Subquery, IntegerField
from django.db.models.functions import Coalesce
from django.urls import reverse, reverse_lazy
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from fuzzywuzzy import fuzz
from django.shortcuts import redirect, render
import uuid
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from student_registration.students.utils import generate_one_unique_id
from student_registration.students.models import Nationality
from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.backends.utils import (
    ExportStorage,
    download_file,
    is_valid_filename,
)

from .filters import (
    MainFilter,
    FullFilter
)
from .tables import (
    BootstrapTable,
    MainTable,
    YouthMainTable,
    FullTable,
    PartnerTable,
)
from .models import (
    Round,
    ProvidedServices,
    Registration,
)
from student_registration.backends.models import ExportHistory

from .forms import (
    MainForm,
    ReferralForm
)
from .serializers import (
    MainSerializer
)
from django.conf import settings

from .utils import *

from student_registration.mscc.templatetags.simple_tags import education_history_model, education_history_programmes
from .tasks import queue_mscc_export, queue_filtered_mscc_export
from student_registration.users.templatetags.custom_tags import has_group
from .ai_agent import HealthSupportAgent, AgentConfigurationError, AgentAPIError

logger = logging.getLogger(__name__)


def chart_data(request):
    """Return aggregated MSCC registration data for charts."""
    metric = request.GET.get('chart', 'nationality')
    qs = Registration.objects.filter(deleted=False)

    package_type = request.GET.get('package_type')
    if package_type:
        qs = qs.filter(type=package_type)

    partner = request.GET.get('partner')
    if partner:
        qs = qs.filter(partner_id=partner)

    governorate = request.GET.get('governorate')
    if governorate:
        qs = qs.filter(center__governorate_id=governorate)

    caza = request.GET.get('caza')
    if caza:
        qs = qs.filter(center__caza_id=caza)

    cadaster = request.GET.get('cadaster')
    if cadaster:
        qs = qs.filter(center__cadaster_id=cadaster)

    programme_type = request.GET.get('programme_type')
    if programme_type:
        qs = qs.filter(education_service__education_program=programme_type)

    start = validate_date(request.GET.get('start'))
    if start:
        qs = qs.filter(created__date__gte=start)

    end = validate_date(request.GET.get('end'))
    if end:
        qs = qs.filter(created__date__lte=end)

    if metric == 'gender':
        data = (
            qs.values(label=F('child__gender'))
            .exclude(child__gender__isnull=True)
            .annotate(value=Count('id'))
            .order_by('label')
        )
    else:
        data = (
            qs.values(label=F('child__nationality__name'))
            .exclude(child__nationality__isnull=True)
            .annotate(value=Count('id'))
            .order_by('label')
        )
    return JsonResponse(list(data), safe=False)


def _service_to_dict(service):
    return {
        'id': service.id,
        'name': service.name,
        'type': service.type,
        'category': service.category,
        'required': service.required,
        'completed': service.completed,
        'completion_date': service.completion_date.isoformat() if service.completion_date else None,
        'service_id': service.service_id,
    }


def _classify_service(service_dict):
    name = (service_dict.get('name') or '').lower()
    category = (service_dict.get('category') or '').lower()

    if 'pss' in name or 'psychosocial' in name or 'child protection' in category:
        return 'pss'
    if 'health' in name or 'nutrition' in name or 'health' in category or 'nutrition' in category:
        return 'health'
    if 'support' in name or 'support' in category or 'social protection' in category or 'caregiver' in name:
        return 'support'
    return 'other'


def _summarize_services(services):
    buckets = {
        'pss': [],
        'health': [],
        'support': [],
        'other': [],
    }

    for service in services:
        data = _service_to_dict(service)
        buckets[_classify_service(data)].append(data)

    summary = {}
    overall_pending = 0
    for key, items in buckets.items():
        required_total = sum(1 for item in items if item['required'])
        required_pending = sum(1 for item in items if item['required'] and not item['completed'])
        completed = sum(1 for item in items if item['completed'])
        summary[key] = {
            'total': len(items),
            'completed': completed,
            'required_total': required_total,
            'required_pending': required_pending,
            'items': items,
        }
        overall_pending += required_pending

    summary['overall_pending_required'] = overall_pending
    return summary


def _summarize_attendance(records):
    total = len(records)
    attended = sum(1 for record in records if record.attended == 'Yes')
    missed = sum(1 for record in records if record.attended == 'No')
    attendance_rate = round(attended / total, 2) if total else None
    last_absence = None

    for record in records:
        if record.attended == 'No' and getattr(record, 'attendance_day', None):
            attendance_date = getattr(record.attendance_day, 'attendance_date', None)
            if attendance_date and (last_absence is None or attendance_date > last_absence):
                last_absence = attendance_date

    return {
        'total_sessions': total,
        'attended_sessions': attended,
        'missed_sessions': missed,
        'attendance_rate': attendance_rate,
        'most_recent_absence': last_absence.isoformat() if last_absence else None,
    }


def _calculate_risk_score(age, attendance_summary, services_summary):
    score = 0
    missed = attendance_summary.get('missed_sessions', 0) or 0
    rate = attendance_summary.get('attendance_rate')

    if missed >= 4:
        score += 4
    elif missed >= 2:
        score += 2
    elif missed == 1:
        score += 1

    if rate is not None:
        if rate < 0.5:
            score += 4
        elif rate < 0.75:
            score += 3
        elif rate < 0.9:
            score += 1

    pss_pending = services_summary['pss']['required_pending']
    health_pending = services_summary['health']['required_pending']
    support_pending = services_summary['support']['required_pending']

    score += pss_pending * 3
    score += health_pending * 2
    score += support_pending

    if age is not None:
        if age < 6:
            score += 1
            if health_pending:
                score += 1
        if age < 12 and pss_pending:
            score += 1

    return score


def _build_alerts(attendance_summary, services_summary):
    alerts = []
    rate = attendance_summary.get('attendance_rate')
    missed = attendance_summary.get('missed_sessions', 0) or 0

    if rate is not None and rate < 0.75:
        alerts.append('Attendance below 75%')
    if missed >= 3:
        alerts.append(f'{missed} absences recorded')

    if services_summary['pss']['required_pending']:
        alerts.append('Pending required PSS services')
    if services_summary['health']['required_pending']:
        alerts.append('Pending required health services')
    if services_summary['support']['required_pending']:
        alerts.append('Pending required support services')

    return alerts


def _build_child_context(registration, services, attendance_records):
    child = getattr(registration, 'child', None)
    age = None
    gender = None
    child_name = None
    child_id = None

    if child:
        child_id = child.id
        child_name = child.full_name
        gender = child.gender
        age_value = child.age
        age = age_value if age_value else None

    services_summary = _summarize_services(services)
    attendance_summary = _summarize_attendance(attendance_records)
    alerts = _build_alerts(attendance_summary, services_summary)
    risk_score = _calculate_risk_score(age, attendance_summary, services_summary)

    return {
        'registration_id': registration.id,
        'child_id': child_id,
        'child_name': child_name,
        'gender': gender,
        'age': age,
        'package_type': registration.type,
        'attendance': attendance_summary,
        'services': services_summary,
        'alerts': alerts,
        'risk_score': risk_score,
        'education_programme': registration.education_program,
    }


class HealthSupportAgentView(LoginRequiredMixin, View):
    """Return an AI-assisted assessment of MSCC registrations."""

    http_method_names = ['get', 'post']
    DEFAULT_LIMIT = 5
    MIN_LIMIT = 1
    MAX_LIMIT = 20

    def get(self, request, *args, **kwargs):
        registration_ids = request.GET.getlist('registration_id')
        single_id = request.GET.get('registration_id')
        if single_id and not registration_ids:
            registration_ids = [single_id]
        limit = request.GET.get('limit')
        return self._generate_response(registration_ids, limit)

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body or '{}')
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON payload')

        registration_ids = payload.get('registration_ids')
        limit = payload.get('limit')
        return self._generate_response(registration_ids, limit)

    def _generate_response(self, registration_ids, limit):
        normalized_ids = self._normalize_ids(registration_ids)
        limit_value = self._normalize_limit(limit)

        queryset = Registration.objects.filter(deleted=False)
        fetch_limit = limit_value

        if normalized_ids:
            queryset = queryset.filter(id__in=normalized_ids)
            fetch_limit = max(limit_value, len(normalized_ids))
        else:
            absence_subquery = Subquery(
                MSCCAttendanceChild.objects.filter(
                    registration_id=OuterRef('pk'),
                    attended='No'
                ).values('registration_id').annotate(total=Count('id')).values('total'),
                output_field=IntegerField(),
            )
            pending_subquery = Subquery(
                ProvidedServices.objects.filter(
                    registration_id=OuterRef('pk'),
                    required=True,
                    completed=False,
                ).values('registration_id').annotate(total=Count('id')).values('total'),
                output_field=IntegerField(),
            )
            queryset = queryset.annotate(
                absent_days=Coalesce(absence_subquery, 0, output_field=IntegerField()),
                pending_required=Coalesce(pending_subquery, 0, output_field=IntegerField()),
            ).order_by('-absent_days', '-pending_required', '-id')
            fetch_limit = max(limit_value * 3, limit_value)

        registrations = list(queryset.select_related('child')[:fetch_limit])

        if not registrations:
            return JsonResponse({
                'generated_at': timezone.now().isoformat(),
                'children': [],
                'analysis': '',
                'model': getattr(settings, 'OPENAI_HEALTH_AGENT_MODEL', None),
                'limit': limit_value,
                'count': 0,
                'filters': {'registration_ids': normalized_ids} if normalized_ids else {},
            })

        registration_ids_list = [registration.id for registration in registrations]

        services_map = {}
        for service in ProvidedServices.objects.filter(registration_id__in=registration_ids_list):
            services_map.setdefault(service.registration_id, []).append(service)

        attendance_map = {}
        attendance_qs = MSCCAttendanceChild.objects.filter(
            registration_id__in=registration_ids_list
        ).select_related('attendance_day').order_by('attendance_day__attendance_date', 'id')
        for attendance in attendance_qs:
            attendance_map.setdefault(attendance.registration_id, []).append(attendance)

        children_context = [
            _build_child_context(
                registration,
                services_map.get(registration.id, []),
                attendance_map.get(registration.id, []),
            )
            for registration in registrations
        ]

        children_context.sort(key=lambda child: child['risk_score'], reverse=True)
        children_context = children_context[:limit_value]

        analysis = ''
        error = None
        model_name = getattr(settings, 'OPENAI_HEALTH_AGENT_MODEL', None)

        if children_context:
            try:
                agent = HealthSupportAgent()
                analysis = agent.analyze_children(children_context)
                model_name = agent.model
            except AgentConfigurationError as exc:
                error = str(exc)
            except AgentAPIError as exc:
                error = str(exc)
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.exception('Unexpected error while running HealthSupportAgent')
                error = 'Unexpected error while generating AI analysis.'

        response_payload = {
            'generated_at': timezone.now().isoformat(),
            'children': children_context,
            'analysis': analysis,
            'model': model_name,
            'limit': limit_value,
            'count': len(children_context),
        }

        if normalized_ids:
            response_payload['filters'] = {'registration_ids': normalized_ids}
        if error:
            response_payload['error'] = error

        return JsonResponse(response_payload)

    @staticmethod
    def _normalize_ids(registration_ids):
        if not registration_ids:
            return []
        if isinstance(registration_ids, (str, int)):
            registration_ids = [registration_ids]

        normalized = []
        for value in registration_ids:
            if value is None:
                continue
            value_str = str(value).strip()
            if not value_str:
                continue
            try:
                normalized.append(int(value_str))
            except ValueError:
                continue
        return normalized

    @staticmethod
    def _normalize_limit(limit):
        try:
            limit_value = int(limit)
        except (TypeError, ValueError):
            limit_value = HealthSupportAgentView.DEFAULT_LIMIT
        return max(
            HealthSupportAgentView.MIN_LIMIT,
            min(HealthSupportAgentView.MAX_LIMIT, limit_value),
        )


class HealthSupportAgentPageView(LoginRequiredMixin, TemplateView):
    """Render the interactive dashboard for the health support agent."""

    template_name = 'mscc/health_agent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_limit = HealthSupportAgentView.DEFAULT_LIMIT
        context.update(
            {
                'default_limit': default_limit,
                'max_limit': HealthSupportAgentView.MAX_LIMIT,
                'endpoint': reverse('mscc:health_agent'),
                'is_agent_configured': bool(getattr(settings, 'OPENAI_API_KEY', '')),
                'configured_model': getattr(settings, 'OPENAI_HEALTH_AGENT_MODEL', ''),
            }
        )
        return context


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'mscc/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        generate_services(instance.child.age, instance)
        current_tab = self.request.GET.get('current_tab', 'info')

        rounds_registered = EducationService.objects.filter(
            registration__child_id=instance.child.id,
            registration__deleted=False
        ).values_list('round_id', flat=True)

        # Remove any None values
        rounds_registered = [r for r in rounds_registered if r is not None]

        # Query for available rounds
        available_rounds = Round.objects.filter(current_year=True).exclude(id__in=rounds_registered)

        # Check if any exist
        new_round = available_rounds.exists()

        services = ProvidedServices.objects.filter(registration=instance)
        services_dict = {service.name: service for service in services}

        return {
            'instance': instance,
            'new_round': new_round,
            'current_tab': current_tab,
            'provided_services': services_dict,
        }


class DashboardView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'mscc/dashboard.html'

    def get_context_data(self, **kwargs):

        return {}


class DashboardCustomView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'mscc/dashboard_d3.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization
        from .models import Round

        instances = Registration.objects.filter(deleted=False)
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()
        rounds = Round.objects.all()

        # Children registered in more than one round
        moved_qs = (
            instances.values(
                'child__first_name',
                'child__father_name',
                'child__last_name',
            )
            .annotate(
                rounds=ArrayAgg('round__name', distinct=True),
                programmes=ArrayAgg('education_service__education_program', distinct=True),
                num_rounds=Count('round', distinct=True),
            )
            .filter(num_rounds__gt=1)
        )

        moved_children = [
            {
                'name': f"{row['child__first_name']} {row['child__father_name']} {row['child__last_name']}",
                'rounds': [r for r in row['rounds'] if r],
                'programmes': [p for p in row['programmes'] if p],
            }
            for row in moved_qs
        ]

        return {
            'total': instances.count(),
            'total_corepackage': instances.filter(type='Core-Package').count(),
            'total_walkin': instances.filter(type='Walk-in').count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners,
            'rounds': rounds,
            'moved_children': moved_children,
        }


class DashboardYouthView(LoginRequiredMixin,
                         TemplateView):
    template_name = 'mscc/dashboard_youth.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization

        instances = Registration.objects.all()
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()

        return {
            'total': instances.count(),
            'total_corepackage': instances.filter(type='Core-Package').count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners
        }


class DashboardDataView(LoginRequiredMixin, View):
    """Return aggregated data for dashboard charts."""

    def get(self, request):
        from django.db.models import Count
        from .models import (
            Registration,
            YouthKitService,
            PSSService,
        )
        cash_support_programmes = Registration.CASH_SUPPORT_PROGRAMMES

        qs = Registration.objects.filter(deleted=False)

        centers = request.GET.getlist('centers')
        if centers:
            qs = qs.filter(center_id__in=centers)
        rounds = request.GET.getlist('rounds')
        if rounds:
            qs = qs.filter(round_id__in=rounds)
        governorates = request.GET.getlist('governorates')
        if governorates:
            qs = qs.filter(center__governorate_id__in=governorates)
        partners = request.GET.getlist('partners')
        if partners:
            qs = qs.filter(partner_id__in=partners)

        def aggregate(queryset, field):
            results = queryset.values(field).annotate(total=Count('id')).order_by(field)
            data = []
            for row in results:
                name = row.get(field) or 'N/A'
                data.append({'name': name, 'y': row['total']})
            return data

        pss_qs = PSSService.objects.filter(registration__in=qs)
        ys_qs = YouthKitService.objects.filter(registration__in=qs)

        data = {
            'children_per_gender': aggregate(qs, 'child__gender'),
            'children_per_status': aggregate(qs, 'child__marital_status'),
            'children_per_programme': aggregate(qs, 'type'),
            'children_per_nationality': aggregate(qs, 'child__nationality__name'),
            'children_per_source': aggregate(qs, 'source_of_identification'),
            'children_per_disability': aggregate(qs, 'child__disability__name'),
            'children_per_vulnerability': aggregate(pss_qs, 'child_vulnerability'),
        }

        programme_counts = Counter()
        for programmes in qs.values_list('cash_support_programmes', flat=True):
            if programmes:
                programme_counts.update(programmes)

        cash = []
        for value, _ in cash_support_programmes:
            if value:
                cash.append({'name': value, 'y': programme_counts.get(value, 0)})
        data['children_cash_support'] = cash

        data['children_volunteering'] = aggregate(ys_qs, 'participate_volunteering')

        # Number of unique children per round
        per_round = (
            qs.values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        round_names = [row.get('round__name') or 'N/A' for row in per_round]
        per_round_dict = {name: row['total'] for name, row in zip(round_names, per_round)}
        data['children_per_round'] = [
            {'name': name, 'y': per_round_dict[name]}
            for name in round_names
        ]

        # Children registered in more than one round
        multi_round_children = list(
            qs.values('child')
            .annotate(round_count=Count('round', distinct=True))
            .filter(round_count__gt=1)
            .values_list('child', flat=True)
        )
        moved_per_round = (
            qs.filter(child__in=multi_round_children)
            .values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        moved_dict = {row.get('round__name') or 'N/A': row['total'] for row in moved_per_round}

        data['children_moved_rounds'] = {
            'categories': round_names,
            'moved': [moved_dict.get(name, 0) for name in round_names],
            'new': [per_round_dict[name] - moved_dict.get(name, 0) for name in round_names],
        }

        return JsonResponse(data, safe=False)


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(MainAddView, self).get_initial()
        data = {
            'type': self.request.GET.get('type', ''),
        }
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(MainAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=None, request=self.request)
        else:
            return MainForm(None, instance=None, request=self.request, initial=self.get_initial())


class MainEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = MainSerializer(instance).data
            data['child_nationality'] = data['child_nationality_id'] if 'child_nationality_id' in data else ''
            data['child_disability'] = data['child_disability_id'] if 'child_disability_id' in data else ''
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']if 'main_caregiver_nationality_id' in data else ''
            data['father_educational_level'] = data['father_educational_level_id']if 'father_educational_level_id' in data else ''
            data['mother_educational_level'] = data['mother_educational_level_id']if 'mother_educational_level_id' in data else ''
            data['id_type'] = data['id_type_id']if 'id_type_id' in data else ''
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)


class NewRoundView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):

    group_required = [u"MSCC", u"MSCC_CENTER"]
    template_name = 'mscc/new_round.html'

    def get_context_data(self, **kwargs):
        registry = kwargs.get('pk')
        return {
            'registry': registry
        }


class NewRoundRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):

        registry = self.request.GET.get('registry')
        type = self.request.GET.get('registrationType')

        if self.request.GET.get('new_round_confirmation', None) == 'confirmed':
            import copy
            registration = Registration.objects.get(id=registry)
            new_registration = copy.copy(registration)
            new_registration.pk = None
            new_registration.round = None
            new_registration.owner = self.request.user
            new_registration.modified_by = self.request.user
            new_registration.type = type
            if self.request.user.center:
                new_registration.center = self.request.user.center
            if self.request.user.partner:
                new_registration.partner = self.request.user.partner
            new_registration.save()

            generate_services(new_registration.child.age, new_registration, self.request.user)
            return reverse('mscc:service_education_add', kwargs={'registry': new_registration.id, 'package_type': type})

        return reverse('mscc:new_round', kwargs={'registry': registry})


def main_mark_delete_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.deleted_by = request.user
            registration.save()
            result = {"isSuccessful": True}
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = MainTable
    model = Registration
    template_name = 'mscc/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u"MSCC"]

    filterset_class = MainFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id

        qs = (Registration.objects
              .select_related(
            'child',
            'child__nationality',
            'partner',
            'center',
            'center__governorate',
            'center__caza',
            'center__cadaster',
            'owner',
            'modified_by',
            'round',
        )
              .prefetch_related('education_service')
              .filter(deleted=False))

        previous_registration = Registration.objects.filter(
            child_id=OuterRef('child_id'),
            created__lt=OuterRef('created'),
        )

        absent_days = (
            MSCCAttendanceChild.objects
                .filter(registration_id=OuterRef('pk'), attended='No')
                .values('registration')
                .annotate(count=Count('id'))
                .values('count')
        )

        qs = qs.annotate(
            has_previous=Exists(previous_registration),
            _total_absent_days=Coalesce(Subquery(absent_days, output_field=IntegerField()), 0),
        )

        round_filter = Q(round__isnull=True) | Q(round__current_year=True)

        if has_group(user, 'MSCC_UNICEF'):
            return qs.filter(round_filter).order_by('-id')

        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            return qs.filter(round_filter, partner=partner_id).order_by('-id')

        elif has_group(user, 'MSCC_CENTER') and center_id:
            return qs.filter(round_filter, center=center_id).order_by('-id')

        return Registration.objects.none()

    def get_table_class(self):

        """
        Return the class to use for the table.
        """
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullTable
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return PartnerTable
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.table_class

        if not has_group(self.request.user, 'MSCC_FULL'):
            return YouthMainTable
        return self.table_class

    def get_filterset_class(self):
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullFilter
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return self.filterset_class
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.filterset_class

        return self.filterset_class


class MainViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    model = Registration
    queryset = Registration.objects.all()
    serializer_class = MainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')

        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


def main_registration_cancel_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            return redirect('mscc:list')
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


def outreach_child_search(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    form_str = '{} {} {}'.format(first_name, father_name, last_name)
    filtered_results = OutreachChild.objects.filter(
        birthday_year=birthday_year
    )

    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )
    if birthday_day:
        filtered_results = filtered_results.filter(
            birthday_day=birthday_day
        )

    filtered_results = filtered_results.values(
        'id',
        'first_name',
        'outreach_caregiver__father_name',
        'outreach_caregiver__last_name',
        'outreach_caregiver__mother_full_name',
        'gender',
        'nationality',
        'date_of_birth',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['outreach_caregiver__father_name'],
                                       result['outreach_caregiver__last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 80:
            result['score'] = fuzzy_match
            result_match.append(result)

    if filtered_results != '':
        return JsonResponse({'result': result_match})

    return JsonResponse({'result': []})


def outreach_child(request):

    outreach_id = request.GET.get('outreach_id')
    result = get_outreach_child(outreach_id)
    return JsonResponse(result)


class ReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/referral_form.html'
    form_class = ReferralForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(ReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return ReferralForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = Referral.objects.get(id=pk)

                return ReferralForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return ReferralForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(ReferralFormView, self).form_valid(form)


def old_child_search(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    form_str = '{} {} {}'.format(first_name, father_name, last_name)

    # filtered_results = Student.objects.filter(
    #     birthday_year=birthday_year
    # )
    # if filtered_results.count() > 1000 and not birthday_month and not birthday_day:
    #     return JsonResponse({'result': {'error': 'Too many records. Please select the Birthday '
    #                                              'month to get more accurate result'}})
    #
    # if birthday_month:
    #     filtered_results = filtered_results.filter(
    #         birthday_month=birthday_month
    #     )
    #
    # if filtered_results.count() > 1000 and not birthday_day:
    #     return JsonResponse({'result': {'error': 'Too many records. Please select the Birthday '
    #                                              'day to get more accurate result'}})
    #
    # if birthday_day:
    #     filtered_results = filtered_results.filter(
    #         birthday_day=birthday_day
    #     )
    #
    # filtered_results = filtered_results.values(
    #     'id',
    #     'first_name',
    #     'father_name',
    #     'last_name',
    #     'mother_fullname',
    #     'sex',
    #     'nationality__name',
    #     'birthday_year',
    #     'birthday_month',
    #     'birthday_day',
    # ).distinct()
    #
    # result_match = []
    # for result in filtered_results:
    #     result_str = '{} {} {}'.format(result['first_name'], result['father_name'],
    #                                    result['last_name'])
    #     fuzzy_match = fuzz.ratio(form_str, result_str)
    #     if fuzzy_match > 70:
    #         result['score'] = fuzzy_match
    #         result['programmes'] = education_history_programmes(result['id'])
    #         result_match.append(result)
    #
    # return JsonResponse({'result': result_match})

    filtered_results = Student.objects.filter(
        birthday_year=birthday_year
    )

    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )

    filtered_results = filtered_results.filter(
        Q(first_name__contains=first_name, last_name__contains=last_name) |
        Q(first_name__contains=first_name, father_name__contains=last_name)
    ).values(
        'id',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'sex',
        'nationality__name',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['father_name'],
                                       result['last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 70:
            result['score'] = fuzzy_match
            result['programmes'] = education_history_programmes(result['id'])
            result_match.append(result)

    return JsonResponse({'result': result_match})


def old_child_data(request):

    student_id = request.GET.get('student_id')
    result = get_old_child(student_id)
    return JsonResponse(result)


def child_duplication_check(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        birthday_year = body.get('birthday_year')
        birthday_month = body.get('birthday_month')
        birthday_day = body.get('birthday_day')
        first_name = body.get('first_name')
        father_name = body.get('father_name')
        last_name = body.get('last_name')
        mother_fullname = body.get('mother_fullname')
        sex = body.get('sex')
        nationality_id = body.get('nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(birthday_year, birthday_month, birthday_day)
        unicef_id = generate_one_unique_id(
            '0',
            first_name,
            father_name,
            last_name,
            mother_fullname,
            birthdate,
            nationality,
            sex
        )

        if unicef_id:
            qs = Registration.objects.filter(
                child__unicef_id=unicef_id,
                deleted=False
            )
            if registration_id:
                qs = qs.exclude(pk=registration_id)
            qs = qs.values('id', 'center__name')
            return JsonResponse({'result': list(qs)})

    return JsonResponse({'result': []})


def quick_search(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    term = request.GET.get('term', 0).strip()
    terms = request.GET.get('term', 0).strip()
    qs = {}

    if terms:
        user = request.user
        if user.is_authenticated:
            center_id = user.center_id
            partner_id = user.partner_id

            if has_group(user, 'MSCC_UNICEF'):
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False
                ).order_by('-id')
            elif has_group(user, 'MSCC_PARTNER') and partner_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, partner=partner_id
                ).order_by('-id')
            elif has_group(user, 'MSCC_CENTER') and center_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, center=center_id
                ).order_by('-id')
            else:
                qs = Registration.objects.none()

            if len(terms.split()) > 1:
                qs = qs.annotate(fullname=Concat('child__first_name', Value(' '), 'child__father_name',
                                                 Value(' '), 'child__last_name')) \
                    .filter(fullname__icontains=terms) \
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()

            else:
                # for term in terms:
                qs = qs.filter(
                    Q(child__first_name__icontains=term) |
                    Q(child__last_name__icontains=term))\
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'result': json.dumps(list(qs))})


class ProgrammeDetails(LoginRequiredMixin,
                       TemplateView):

    template_name = 'mscc/programme_details.html'

    def get_context_data(self, **kwargs):

        programme_id = self.request.GET.get('programme_id')
        programme_type = self.request.GET.get('programme_type')

        instance = education_history_model(programme_id, programme_type)

        return {
            'instance': instance,
            'programme_type': programme_type
        }


class ChildProfilePreview(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ChildProfilePreview, self).get_context_data(**kwargs)

        registry_id = self.request.GET.get('registry_id')

        if not registry_id:
            context['error'] = 'No id provided.'
            return context

        try:
            instance = Registration.objects.get(id=registry_id)
        except Registration.DoesNotExist:
            context['error'] = 'Registration with id' + str(registry_id) + ' not found.'
            return context
        except ValueError:
            context['error'] = 'Invalid registry_id ' + str(registry_id)
            return context

        context['instance'] = instance
        return context


@login_required(login_url='/users/login')
def export_list_background(request):
    user = request.user
    nationality = request.GET.get('nationality', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    father_name = request.GET.get('father_name', '')
    mother_fullname = request.GET.get('mother_fullname', '')
    round = request.GET.get('round', '')
    if not round:
        return JsonResponse({'error': 'Round is not selected. Please select a round before exporting data.'},
                            status=400)

    export_record = ExportHistory.objects.create(
        export_type='Makani List',
        created_by=user,
        partner_name=user.partner.name if user.partner else ''
    )
    queue_filtered_mscc_export(
        export_record.id,
        nationality,
        first_name,
        last_name,
        father_name,
        mother_fullname,
        round,
    )
    return JsonResponse({'status': 'started'})


def export_child_list_background(request):
    try:
        cursor = connection.cursor()

        vw_mscc_data_str = "SELECT * FROM vw_mscc_child "
        cursor.execute(vw_mscc_data_str)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for vw_mscc_data
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)

            # Add BOM to handle Arabic text correctly
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)  # Write headers

            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)

            # Add CSV to ZIP
            zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = "out_file_{}.zip".format(unique_id)
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/users/login')
def export_list_async(request):
    fields = None
    file_format = 'csv'
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (ValueError, AttributeError):
            payload = request.POST
        if isinstance(payload, dict):
            file_format = payload.get('format', 'csv')
            fields = payload.get('fields') or None
        else:
            file_format = payload.get('format', 'csv') if payload else 'csv'
    else:
        file_format = request.GET.get('format', 'csv')
    export_record = ExportHistory.objects.create(
        export_type='Makani List',
        created_by=request.user,
        partner_name=request.user.partner.name if request.user.partner else '',
        fields=fields,
        file_format=file_format,
    )
    queue_mscc_export(export_record.id, fields, file_format)
    return JsonResponse({'status': 'started'})


@login_required(login_url='/users/login')
def get_file(request, file_name):
    if is_valid_filename(file_name, 'zip'):
        return download_file(file_name, 'output_file.zip')
    return HttpResponse("Invalid file.")


@login_required(login_url='/users/login')
def get_file_csv(request, file_name):
    if is_valid_filename(file_name, 'csv'):
        return download_file(file_name, 'exported_data.csv', content_type='text/csv')
    return HttpResponse("Invalid file.", status=400)
