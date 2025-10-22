# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import datetime as dt
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
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db import models
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
    PSSService,
    HealthNutritionService,
    HealthNutritionReferral,
    EducationProgrammeAssessment,
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


REGISTRATION_WELLBEING_FIELDS = [
    'registration_date',
    'type',
    'have_labour',
    'labour_type',
    'labour_type_specify',
    'labour_hours',
    'labour_weekly_income',
    'labour_condition',
    'cash_support_programmes',
    'mscc_packages',
    'source_of_identification',
    'source_of_identification_specify',
    'child_outreach',
    'student_old',
    'partner',
    'center',
    'round',
    'partner_unique_number',
]


EDUCATION_GRADE_LABELS = {
    'arabic_grade': 'Arabic',
    'language_grade': 'Foreign Language',
    'math_grade': 'Mathematics',
    'science_grade': 'Sciences',
    'biology_grade': 'Biology',
    'chemistry_grade': 'Chemistry',
    'physics_grade': 'Physics',
    'social_emotional_grade': 'Social-Emotional Development',
    'artistic_grade': 'Artistic Development',
    'psychomotor_grade': 'Psychomotor Development',
}


def _coerce_numeric_value(raw):
    if raw in (None, '', [], {}):
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    if isinstance(raw, (list, tuple)):
        for item in raw:
            value = _coerce_numeric_value(item)
            if value is not None:
                return value
        return None

    try:
        text = str(raw).strip()
    except Exception:  # pragma: no cover - defensive
        return None

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def _coerce_text_value(raw):
    if raw in (None, '', [], {}):
        return None

    if isinstance(raw, (list, tuple)):
        for item in raw:
            value = _coerce_text_value(item)
            if value:
                return value
        return None

    return str(raw)


def _summarize_education_assessment(assessment):
    if not assessment:
        return None

    pre_data = dict(assessment.pre_test or {})
    post_data = dict(assessment.post_test or {})
    subjects = []
    pre_scores = []
    post_scores = []
    changes = []

    for field, label in EDUCATION_GRADE_LABELS.items():
        pre_value = _coerce_numeric_value(pre_data.get(field))
        post_value = _coerce_numeric_value(post_data.get(field))

        if pre_value is None and post_value is None:
            continue

        change = None
        if pre_value is not None and post_value is not None:
            change = round(post_value - pre_value, 2)
            changes.append(change)

        if pre_value is not None:
            pre_scores.append(pre_value)
        if post_value is not None:
            post_scores.append(post_value)

        subjects.append({
            'field': field,
            'label': label,
            'pre': pre_value,
            'post': post_value,
            'change': change,
        })

    average_change = None
    if changes:
        average_change = round(sum(changes) / len(changes), 2)

    pre_average = None
    if pre_scores:
        pre_average = round(sum(pre_scores) / len(pre_scores), 2)

    post_average = None
    if post_scores:
        post_average = round(sum(post_scores) / len(post_scores), 2)

    if not subjects and not any([
        _coerce_text_value(post_data.get('participation')),
        _coerce_text_value(post_data.get('barriers')),
        _coerce_text_value(post_data.get('post_test_done')),
        _coerce_text_value(post_data.get('school_year_completed')),
    ]):
        return None

    trend = None
    if average_change is not None:
        if average_change >= 5:
            trend = 'improved'
        elif average_change <= -5:
            trend = 'declined'
        else:
            trend = 'stable'

    summary = {
        'programme_type': assessment.programme_type
        or _coerce_text_value(pre_data.get('programme_type')),
        'pre_average': pre_average,
        'post_average': post_average,
        'average_change': average_change,
        'trend': trend,
        'subjects': subjects,
        'participation': _coerce_text_value(post_data.get('participation')),
        'barriers': _coerce_text_value(post_data.get('barriers')),
        'barriers_other': _coerce_text_value(post_data.get('barriers_other')),
        'post_test_done': _coerce_text_value(post_data.get('post_test_done')),
        'school_year_completed': _coerce_text_value(post_data.get('school_year_completed')),
        'last_updated': assessment.modified.isoformat()
        if getattr(assessment, 'modified', None)
        else None,
    }

    if summary['barriers'] and summary['barriers_other'] and summary['barriers'].lower() == 'other':
        summary['barriers_detail'] = summary['barriers_other']

    return summary


def _format_field_value(instance, field, value):
    if value in (None, '', []):
        return None

    if isinstance(field, ArrayField):
        if not value:
            return None

        base_field = getattr(field, 'base_field', None)
        if base_field and getattr(base_field, 'choices', None):
            choice_map = dict(getattr(base_field, 'flatchoices', base_field.choices))
            formatted = [choice_map.get(item, item) for item in value if item not in (None, '')]
        else:
            formatted = [item for item in value if item not in (None, '')]

        return ', '.join(str(item) for item in formatted if item not in (None, '')) or None

    if field.choices:
        display_method = getattr(instance, f'get_{field.name}_display', None)
        if callable(display_method):
            return display_method()
        choice_map = dict(getattr(field, 'flatchoices', field.choices))
        return choice_map.get(value, value)

    if isinstance(field, (models.DateField, models.DateTimeField)):
        return value.isoformat()

    if isinstance(field, models.ForeignKey):
        return str(value)

    return value


def _summarize_model_fields(instance, include_fields=None, exclude_fields=None):
    if not instance:
        return []

    include_fields = set(include_fields or []) if include_fields else None
    base_exclude = {'id', 'registration', 'created', 'modified'}
    if exclude_fields:
        base_exclude |= set(exclude_fields)
    exclude_fields = base_exclude

    summary = []
    for field in instance._meta.fields:
        if include_fields is not None and field.name not in include_fields:
            continue
        if field.name in exclude_fields:
            continue

        value = getattr(instance, field.name)
        display_value = _format_field_value(instance, field, value)
        if display_value in (None, '', []):
            continue

        label = str(field.verbose_name or field.name).strip()
        summary.append({'field': field.name, 'label': label, 'value': display_value})

    return summary


def _summarize_registration(registration):
    return _summarize_model_fields(
        registration,
        include_fields=REGISTRATION_WELLBEING_FIELDS,
        exclude_fields={'owner', 'modified_by', 'deleted', 'deleted_by', 'child'},
    )


def _resolve_registration_date(registration):
    """Return the best available date for a registration record."""

    if getattr(registration, 'registration_date', None):
        return registration.registration_date

    created = getattr(registration, 'created', None)
    if isinstance(created, dt.datetime):
        return created.date()
    if isinstance(created, dt.date):
        return created

    return None


def _summarize_registration_history(registration, history_records):
    """Summarise a child's participation across registrations and rounds."""

    if not history_records:
        return None

    entries = []
    unique_round_ids = set()
    years_counter = Counter()
    first_date = None
    latest_date = None
    previous_year = None
    consecutive_streak = 0
    longest_streak = 0
    recorded_years = []
    gap_years = []

    sorted_history = sorted(
        history_records,
        key=lambda record: (
            _resolve_registration_date(record) or dt.date.min,
            record.id,
        ),
    )

    for record in sorted_history:
        resolved_date = _resolve_registration_date(record)
        round_name = record.round.name if getattr(record, 'round', None) else None
        round_year = getattr(record.round, 'year', None) if getattr(record, 'round', None) else None
        participation_year = round_year
        if participation_year is None and resolved_date:
            participation_year = resolved_date.year

        if resolved_date:
            if first_date is None or resolved_date < first_date:
                first_date = resolved_date
            if latest_date is None or resolved_date > latest_date:
                latest_date = resolved_date

        if record.round_id:
            unique_round_ids.add(record.round_id)

        if participation_year is not None:
            years_counter[participation_year] += 1
            recorded_years.append(participation_year)

            if previous_year is None or participation_year == previous_year:
                consecutive_streak = max(consecutive_streak, 1)
            elif participation_year == previous_year + 1:
                consecutive_streak += 1
            else:
                gap_years.append(participation_year - previous_year)
                consecutive_streak = 1

            longest_streak = max(longest_streak, consecutive_streak)
            previous_year = participation_year

        entries.append(
            {
                'registration_id': record.id,
                'round': round_name,
                'round_year': round_year,
                'registration_date': resolved_date.isoformat() if resolved_date else None,
                'package_type': record.type,
                'center': str(record.center) if getattr(record, 'center', None) else None,
                'is_current': record.id == registration.id,
            }
        )

    unique_years = sorted(set(recorded_years))
    if unique_years:
        # recompute longest streak to ensure gaps reset correctly when duplicate years appear
        current_streak = 0
        previous = None
        longest_streak = 0
        for year in unique_years:
            if previous is None or year == previous + 1:
                current_streak += 1
            else:
                current_streak = 1
            longest_streak = max(longest_streak, current_streak)
            previous = year

    return {
        'total_registrations': len(entries),
        'distinct_rounds': len(unique_round_ids),
        'years_active': unique_years,
        'yearly_counts': [
            {'year': year, 'registrations': years_counter[year]} for year in sorted(years_counter)
        ],
        'first_registration_date': first_date.isoformat() if first_date else None,
        'latest_registration_date': latest_date.isoformat() if latest_date else None,
        'engagement_span_years': (unique_years[-1] - unique_years[0]) if len(unique_years) >= 2 else 0,
        'largest_gap_years': max(gap_years) if gap_years else 0,
        'longest_consecutive_years': longest_streak,
        'entries': entries,
    }


def _extract_wellbeing_flags(pss, health, referral, registration=None, education=None):
    flags = []

    if pss:
        if pss.child_vulnerability:
            flags.append(f"PSS vulnerability: {pss.get_child_vulnerability_display()}")
        if pss.child_protection_concern:
            flags.append(
                f"Protection concern reported: {pss.get_child_protection_concern_display()}"
            )
        if pss.child_distress == 'Yes':
            flags.append('Caregiver reports children experiencing distress')
        if pss.caregivers_distress == 'Yes':
            flags.append('Caregiver reports distress and anxiety')
        if pss.child_know_seek_help == 'No':
            flags.append('Child does not know where to seek help for violence or abuse')
        if pss.child_additional_parenting == 'Yes':
            flags.append('Caregiver requested additional parenting support')
        if pss.caregivers_additional_parenting == 'Yes':
            flags.append('Caregiver requested additional psychosocial support')
        if pss.child_out_school_reasons:
            flags.append(
                f"Reason for being out of school: {pss.get_child_out_school_reasons_display()}"
            )

    if health:
        if health.muac_malnutrition_screening and health.muac_malnutrition_screening != 'No malnutrition screening':
            flags.append(
                f"MUAC screening result: {health.get_muac_malnutrition_screening_display()}"
            )
        if health.child_malnutrition_screening and health.child_malnutrition_screening != 'No malnutrition screening':
            flags.append(
                f"Child MUAC screening result: {health.get_child_malnutrition_screening_display()}"
            )
        if health.eating_minimum_meals == 'No':
            flags.append('Child not eating minimum meals per day')
        if health.child_vaccinated == 'No':
            flags.append('Child not vaccinated as per the national calendar')
        if health.missing_vaccine:
            flags.append(f"Missing vaccines noted: {health.missing_vaccine}")
        if health.positive_parenting == 'No':
            flags.append('Caregiver lacks positive parenting practices')
        if health.physical_activity == 'No':
            flags.append('Child lacks regular physical activity')
        if health.accessing_reproductive_health == 'Yes':
            flags.append('Child accessing reproductive health services (possible child marriage risk)')

    if referral:
        if referral.referred_development_delays == 'Yes':
            destination = referral.get_development_delays_display() or 'unspecified location'
            flags.append(f"Referred for developmental delays: {destination}")
        if referral.referred_malnutrition == 'Yes':
            destination = (
                referral.get_malnutrition_treatment_center_display() or 'unspecified center'
            )
            flags.append(f"Referred for malnutrition treatment: {destination}")

    if registration:
        if registration.have_labour and registration.have_labour.startswith('Yes'):
            display = getattr(registration, 'get_have_labour_display', lambda: registration.have_labour)()
            flags.append(f"Child engaged in labour: {display}")
        if getattr(registration, 'labour_type', None):
            display = getattr(registration, 'get_labour_type_display', lambda: registration.labour_type)()
            flags.append(f"Labour type recorded: {display}")
        if getattr(registration, 'labour_hours', None):
            flags.append(f"Working {registration.labour_hours} hours per week")
        if getattr(registration, 'labour_weekly_income', None):
            display = getattr(
                registration,
                'get_labour_weekly_income_display',
                lambda: registration.labour_weekly_income,
            )()
            flags.append(f"Weekly labour income reported: {display}")
        labour_conditions = getattr(registration, 'labour_condition', None) or []
        if labour_conditions:
            flags.append(
                'Labour conditions: ' + ', '.join(str(item) for item in labour_conditions if item)
            )
    if education:
        trend = education.get('trend')
        if trend == 'declined':
            flags.append('Learning outcomes declined across programme assessments')
        elif trend == 'improved':
            flags.append('Learning outcomes improved across programme assessments')

        if education.get('post_test_done') == 'No':
            flags.append('Education post-tests not completed')
        if education.get('school_year_completed') == 'No':
            flags.append('School year not completed')
        barriers = education.get('barriers')
        if barriers and barriers.lower() not in {'', 'no barriers'}:
            if barriers.lower() == 'other' and education.get('barriers_detail'):
                flags.append(f"Learning barrier reported: {education['barriers_detail']}")
            else:
                flags.append(f"Learning barrier reported: {barriers}")

    return flags


def _calculate_risk_score(
    age,
    attendance_summary,
    services_summary,
    wellbeing_flags=None,
    registration=None,
    education_progress=None,
    registration_history=None,
):
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

    if wellbeing_flags:
        score += len(wellbeing_flags) * 2

    if registration:
        if registration.have_labour and registration.have_labour.startswith('Yes'):
            score += 3
        hours = getattr(registration, 'labour_hours', None) or 0
        if hours >= 40:
            score += 3
        elif hours >= 20:
            score += 2
        elif hours >= 10:
            score += 1
        if getattr(registration, 'labour_weekly_income', None):
            score += 1

    if education_progress:
        avg_change = education_progress.get('average_change')
        if avg_change is not None:
            if avg_change <= -5:
                score += 3
            elif avg_change <= -2:
                score += 1
            elif avg_change >= 5:
                score = max(score - 1, 0)

        if education_progress.get('post_test_done') == 'No':
            score += 1
        if education_progress.get('school_year_completed') == 'No':
            score += 2

        participation = (education_progress.get('participation') or '').lower()
        if 'more than 25' in participation:
            score += 3
        elif '15-25' in participation:
            score += 2
        elif '10-15' in participation:
            score += 1

    if registration_history:
        total_registrations = registration_history.get('total_registrations') or 0
        longest_streak = registration_history.get('longest_consecutive_years') or 0
        largest_gap = registration_history.get('largest_gap_years') or 0

        if total_registrations >= 3:
            score += 1
        if largest_gap >= 2:
            score += 1
        if longest_streak >= 3:
            score = max(score - 1, 0)

    return score


def _build_alerts(
    attendance_summary,
    services_summary,
    wellbeing_flags=None,
    education_progress=None,
    registration_history=None,
):
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

    if wellbeing_flags:
        alerts.extend(wellbeing_flags)

    if education_progress:
        avg_change = education_progress.get('average_change')
        if avg_change is not None and avg_change <= -5:
            alerts.append('Significant decline in education grading outcomes')
        if education_progress.get('post_test_done') == 'No':
            alerts.append('Education post-tests not completed')
        if education_progress.get('school_year_completed') == 'No':
            alerts.append('School year not completed')

    if registration_history:
        largest_gap = registration_history.get('largest_gap_years') or 0
        if largest_gap >= 2:
            alerts.append(f'Gap of {largest_gap} years between registrations detected')

    return alerts


def _assess_life_quality(
    attendance_summary,
    pss=None,
    health=None,
    referral=None,
    registration=None,
    education_progress=None,
    registration_history=None,
):
    """Derive a sentiment-style signal for a child's quality of life."""

    score = 0
    signals = []

    def record(weight, message):
        nonlocal score
        score += weight
        signals.append({'weight': weight, 'message': message})

    rate = attendance_summary.get('attendance_rate')
    missed = attendance_summary.get('missed_sessions', 0) or 0

    if rate is not None:
        if rate >= 0.9:
            record(2, 'Consistent attendance (≥90%)')
        elif rate < 0.6:
            record(-3, 'Attendance below 60%')
        elif rate < 0.75:
            record(-2, 'Attendance below 75%')
        elif rate < 0.85:
            record(-1, 'Attendance below 85%')
    if missed >= 3:
        record(-1, f'{missed} recent absences recorded')

    if pss:
        if pss.child_distress == 'Yes':
            record(-3, 'Child showing distress symptoms')
        if pss.caregivers_distress == 'Yes':
            record(-2, 'Caregiver reports distress or anxiety')
        if pss.child_protection_concern:
            record(-3, 'Child protection concern reported')
        if pss.child_vulnerability:
            record(-2, 'Vulnerability flagged in PSS assessment')
        if pss.child_know_seek_help == 'No':
            record(-2, 'Child unsure where to seek help for abuse or violence')
        elif pss.child_know_seek_help == 'Yes':
            record(1, 'Child knows how to seek help when needed')
        if pss.child_additional_parenting == 'Yes':
            record(-1, 'Additional support requested for child caregiving')
        if pss.caregivers_additional_parenting == 'Yes':
            record(-1, 'Caregiver requested more psychosocial support')
        if pss.child_registered == 'Yes':
            record(1, 'Child has birth registration documentation')

    if health:
        if health.eating_minimum_meals == 'No':
            record(-3, 'Child not meeting minimum daily meals')
        elif health.eating_minimum_meals == 'Yes':
            record(2, 'Child eating the recommended daily meals')
        if health.child_vaccinated == 'No':
            record(-3, 'Child missing required vaccinations')
        elif health.child_vaccinated == 'Yes':
            record(2, 'Child fully vaccinated per schedule')
        if health.muac_malnutrition_screening and health.muac_malnutrition_screening != 'No malnutrition screening':
            record(-2, 'Malnutrition risk identified during screening')
        if getattr(health, 'child_malnutrition_screening', None) and health.child_malnutrition_screening != 'No malnutrition screening':
            record(-2, 'Child MUAC screening indicates malnutrition risk')
        if health.positive_parenting == 'No':
            record(-1, 'Caregiver lacks positive parenting practices')
        elif health.positive_parenting == 'Yes':
            record(1, 'Caregiver practices positive parenting')
        if health.physical_activity == 'No':
            record(-1, 'Child lacks regular physical activity')
        elif health.physical_activity == 'Yes':
            record(1, 'Child engages in regular physical activity')
        if health.accessing_reproductive_health == 'Yes':
            record(-2, 'Child accessing reproductive health services (possible early marriage risk)')
        if health.baby_breastfed == 'Yes':
            record(1, 'Baby receiving breastfeeding support')
        if health.infant_exclusively_breastfed == 'Yes':
            record(1, 'Infant exclusively breastfed (0-6 months)')

    if referral:
        if referral.referred_development_delays == 'Yes':
            record(-1, 'Referred for developmental delay follow-up')
        if referral.referred_malnutrition == 'Yes':
            record(-1, 'Referred to malnutrition treatment services')
        if referral.referred_anc_pnc == 'Yes':
            record(-1, 'ANC/PNC follow-up required for caregiver or child')

    if registration:
        if registration.have_labour and registration.have_labour.startswith('Yes'):
            display = getattr(registration, 'get_have_labour_display', lambda: registration.have_labour)()
            record(-2, f'Child engaged in labour: {display}')
        hours = getattr(registration, 'labour_hours', None) or 0
        if hours >= 40:
            record(-2, 'Working 40+ hours per week')
        elif hours >= 20:
            record(-1, 'Working 20+ hours per week')
        cash_support = getattr(registration, 'cash_support_programmes', None) or []
        if cash_support:
            record(1, 'Cash support in place: ' + ', '.join(str(item) for item in cash_support if item))
        assigned_packages = getattr(registration, 'mscc_packages', None) or []
        if assigned_packages:
            record(1, 'MSCC packages assigned: ' + ', '.join(str(item) for item in assigned_packages if item))

    if education_progress:
        avg_change = education_progress.get('average_change')
        if avg_change is not None:
            change_display = f"{avg_change:+.1f}" if isinstance(avg_change, (int, float)) else avg_change
            if avg_change >= 5:
                record(2, f'Learning outcomes improved on average ({change_display})')
            elif avg_change >= 2:
                record(1, f'Slight learning gains recorded ({change_display})')
            elif avg_change <= -5:
                record(-3, f'Learning outcomes declined on average ({change_display})')
            elif avg_change <= -2:
                record(-1, f'Slight decline in learning outcomes ({change_display})')

        participation = education_progress.get('participation')
        if participation and isinstance(participation, str):
            lower_participation = participation.lower()
            if 'more than 25' in lower_participation:
                record(-2, f'Extended absences reported ({participation})')
            elif '15-25' in lower_participation:
                record(-1, f'Repeated absences reported ({participation})')
            elif 'no absence' in lower_participation:
                record(1, 'No absences reported during programme participation')

        barriers = education_progress.get('barriers')
        if barriers and isinstance(barriers, str) and barriers.lower() not in {'', 'no barriers'}:
            detail = education_progress.get('barriers_detail')
            if barriers.lower() == 'other' and detail:
                record(-1, f'Learning barrier reported: {detail}')
            else:
                record(-1, f'Learning barrier reported: {barriers}')

        if education_progress.get('school_year_completed') == 'Yes':
            record(1, 'Child completed the school year')
        elif education_progress.get('school_year_completed') == 'No':
            record(-2, 'Child did not complete the school year')

        if education_progress.get('post_test_done') == 'No':
            record(-1, 'Post-tests not completed to measure learning outcomes')

    if registration_history:
        total_registrations = registration_history.get('total_registrations') or 0
        longest_streak = registration_history.get('longest_consecutive_years') or 0
        largest_gap = registration_history.get('largest_gap_years') or 0

        if total_registrations >= 2:
            record(1, f'Re-engaged with programme {total_registrations} times')
        if longest_streak >= 3:
            record(2, f'Sustained participation across {longest_streak} consecutive years')
        if largest_gap >= 2:
            record(-1, f'Break of {largest_gap} years between registrations')

    if score <= -6:
        label = 'Critical concern'
    elif score <= -3:
        label = 'Needs attention'
    elif score <= 1:
        label = 'Monitor'
    elif score <= 4:
        label = 'Stable'
    else:
        label = 'Thriving'

    signals.sort(key=lambda entry: entry['weight'])

    return {
        'score': score,
        'label': label,
        'signals': signals,
    }


def _evaluate_programme_impact(
    attendance_summary,
    education_progress=None,
    registration_history=None,
    life_quality=None,
    risk_score=None,
):
    """Assess the Makani programme's longitudinal impact on a child."""

    attendance_snapshot = attendance_summary or {}
    has_longitudinal_data = any(
        [
            education_progress,
            registration_history,
            life_quality,
            risk_score is not None,
            attendance_snapshot.get('attendance_rate') is not None,
        ]
    )

    if not has_longitudinal_data:
        return None

    score = 0
    factors = []

    def record(weight, message):
        nonlocal score
        if not message:
            return
        score += weight
        factors.append({'weight': weight, 'message': message})

    rate = attendance_snapshot.get('attendance_rate')
    if rate is not None:
        if rate >= 0.9:
            record(2, 'Consistently high attendance across programme activities')
        elif rate < 0.6:
            record(-2, 'Very low attendance limits positive programme impact')
        elif rate < 0.75:
            record(-1, 'Attendance challenges reduce programme impact')

    if education_progress:
        avg_change = education_progress.get('average_change')
        numeric_change = avg_change if isinstance(avg_change, (int, float)) else None
        trend = education_progress.get('trend')
        if numeric_change is not None:
            if numeric_change >= 5:
                record(3, f'Education outcomes improved markedly (+{numeric_change:.1f})')
            elif numeric_change >= 2:
                record(1, f'Moderate gains in education outcomes (+{numeric_change:.1f})')
            elif numeric_change <= -5:
                record(-3, f'Significant decline in education outcomes ({numeric_change:.1f})')
            elif numeric_change <= -2:
                record(-1, f'Slight decline in education outcomes ({numeric_change:.1f})')
        if trend == 'improved':
            record(1, 'Learning assessments show improvement over time')
        elif trend == 'declined':
            record(-1, 'Learning assessments declined over time')
        if education_progress.get('school_year_completed') == 'Yes':
            record(1, 'Child completed the school year during programme participation')
        elif education_progress.get('school_year_completed') == 'No':
            record(-2, 'School year not completed despite programme support')

    years_active = []
    if registration_history:
        total_registrations = registration_history.get('total_registrations') or 0
        longest_streak = registration_history.get('longest_consecutive_years') or 0
        largest_gap = registration_history.get('largest_gap_years') or 0
        engagement_span = registration_history.get('engagement_span_years') or 0
        years_active = registration_history.get('years_active') or []

        if total_registrations >= 4:
            record(3, f'{total_registrations} registrations show sustained engagement')
        elif total_registrations >= 2:
            record(1, f'{total_registrations} registrations reflect repeated engagement')

        if longest_streak >= 3:
            record(2, f'Participated for {longest_streak} consecutive years')
        elif longest_streak == 2:
            record(1, 'Participated across two consecutive years')

        if engagement_span >= 4:
            record(1, f'Programme support spans {engagement_span} years')

        if largest_gap >= 3:
            record(-2, f'Gap of {largest_gap} years between registrations')
        elif largest_gap == 2:
            record(-1, 'Two-year gap between registrations observed')

        yearly_counts = registration_history.get('yearly_counts') or []
        if yearly_counts:
            first_year_count = yearly_counts[0].get('registrations')
            last_year_count = yearly_counts[-1].get('registrations')
            if isinstance(first_year_count, int) and isinstance(last_year_count, int):
                if last_year_count > first_year_count:
                    record(1, 'Participation intensity increased in recent years')
                elif last_year_count + 1 < first_year_count:
                    record(-1, 'Participation intensity decreased in recent years')

        first_date_raw = registration_history.get('first_registration_date')
        latest_date_raw = registration_history.get('latest_registration_date')

        def _to_date(value):
            if not value:
                return None
            if isinstance(value, dt.datetime):
                return value.date()
            if isinstance(value, dt.date):
                return value
            try:
                return dt.datetime.fromisoformat(value).date()
            except (TypeError, ValueError):
                return None

        first_date = _to_date(first_date_raw)
        latest_date = _to_date(latest_date_raw)
        if first_date and latest_date and latest_date > first_date:
            span_years = latest_date.year - first_date.year
            if span_years >= 3:
                record(1, 'Progress tracked across multiple programme years')

    if life_quality:
        label = life_quality.get('label')
        if label in {'Thriving', 'Stable'}:
            record(1, 'Recent wellbeing indicators are stable or improving')
        elif label in {'Needs attention', 'Critical concern'}:
            record(-2, 'Wellbeing indicators highlight ongoing risks')

    if risk_score is not None:
        if risk_score >= 8:
            record(-3, 'High current risk score offsets positive programme outcomes')
        elif risk_score <= 2:
            record(1, 'Low current risk score suggests positive programme results')

    factors.sort(key=lambda entry: entry['weight'], reverse=True)

    if score >= 5:
        label = 'Positive impact'
        direction = 'positive'
    elif score <= -3:
        label = 'Negative impact'
        direction = 'negative'
    else:
        label = 'Mixed impact'
        direction = 'mixed'

    summary_lookup = {
        'positive': 'Makani engagement appears to be driving positive change over the years.',
        'negative': 'Challenges persist despite Makani engagement, signalling a negative impact trend.',
        'mixed': 'Makani impact is mixed with both gains and setbacks observed over the years.',
    }

    return {
        'score': score,
        'label': label,
        'direction': direction,
        'summary': summary_lookup.get(direction),
        'factors': factors,
        'years_engaged': years_active,
        'total_registrations': registration_history.get('total_registrations') if registration_history else None,
        'engagement_span_years': registration_history.get('engagement_span_years') if registration_history else None,
    }


def _build_child_context(
    registration,
    services,
    attendance_records,
    pss_assessment,
    health_assessment,
    health_referral,
    education_assessment,
    registration_history=None,
):
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
    pss_details = _summarize_model_fields(pss_assessment)
    health_details = _summarize_model_fields(health_assessment)
    referral_details = _summarize_model_fields(health_referral)
    registration_details = _summarize_registration(registration)
    education_progress = _summarize_education_assessment(education_assessment)
    registration_history_summary = _summarize_registration_history(
        registration,
        registration_history or [],
    )
    wellbeing_flags = _extract_wellbeing_flags(
        pss_assessment,
        health_assessment,
        health_referral,
        registration=registration,
        education=education_progress,
    )
    alerts = _build_alerts(
        attendance_summary,
        services_summary,
        wellbeing_flags,
        education_progress=education_progress,
        registration_history=registration_history_summary,
    )
    risk_score = _calculate_risk_score(
        age,
        attendance_summary,
        services_summary,
        wellbeing_flags,
        registration=registration,
        education_progress=education_progress,
        registration_history=registration_history_summary,
    )
    life_quality = _assess_life_quality(
        attendance_summary,
        pss_assessment,
        health_assessment,
        health_referral,
        registration=registration,
        education_progress=education_progress,
        registration_history=registration_history_summary,
    )
    programme_impact = _evaluate_programme_impact(
        attendance_summary,
        education_progress=education_progress,
        registration_history=registration_history_summary,
        life_quality=life_quality,
        risk_score=risk_score,
    )

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
        'pss_details': pss_details,
        'health_details': health_details,
        'health_referral_details': referral_details,
        'registration_details': registration_details,
        'wellbeing_flags': wellbeing_flags,
        'life_quality': life_quality,
        'education_progress': education_progress,
        'registration_history': registration_history_summary,
        'programme_impact': programme_impact,
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
        question = request.GET.get('question')
        return self._generate_response(registration_ids, limit, question)

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body or '{}')
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON payload')

        registration_ids = payload.get('registration_ids')
        limit = payload.get('limit')
        question = payload.get('question')
        return self._generate_response(registration_ids, limit, question)

    def _generate_response(self, registration_ids, limit, question):
        normalized_ids = self._normalize_ids(registration_ids)
        limit_value = self._normalize_limit(limit)
        question_text = self._normalize_question(question)
        focus_topics = HealthSupportAgent.infer_focus_topics(question_text)

        queryset = Registration.objects.filter(
            deleted=False,
            type__in=['Core-Package', 'Core Package'],
        )

        pss_exists = PSSService.objects.filter(registration_id=OuterRef('pk'))
        health_service_exists = HealthNutritionService.objects.filter(
            registration_id=OuterRef('pk')
        )
        health_referral_exists = HealthNutritionReferral.objects.filter(
            registration_id=OuterRef('pk')
        )

        queryset = queryset.annotate(
            has_pss=Exists(pss_exists),
            has_health_service=Exists(health_service_exists),
            has_health_referral=Exists(health_referral_exists),
        ).filter(
            has_pss=True,
        ).filter(
            Q(has_health_service=True) | Q(has_health_referral=True)
        )
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

        registrations = list(queryset.select_related('child', 'round')[:fetch_limit])

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
        child_ids = [registration.child_id for registration in registrations if registration.child_id]

        services_map = {}
        for service in ProvidedServices.objects.filter(registration_id__in=registration_ids_list):
            services_map.setdefault(service.registration_id, []).append(service)

        attendance_map = {}
        attendance_qs = MSCCAttendanceChild.objects.filter(
            registration_id__in=registration_ids_list
        ).select_related('attendance_day').order_by('attendance_day__attendance_date', 'id')
        for attendance in attendance_qs:
            attendance_map.setdefault(attendance.registration_id, []).append(attendance)

        pss_map = {}
        for pss in PSSService.objects.filter(registration_id__in=registration_ids_list).order_by('-id'):
            pss_map.setdefault(pss.registration_id, pss)

        health_service_map = {}
        for health_service in HealthNutritionService.objects.filter(registration_id__in=registration_ids_list).order_by('-id'):
            health_service_map.setdefault(health_service.registration_id, health_service)

        health_referral_map = {}
        for health_referral in HealthNutritionReferral.objects.filter(registration_id__in=registration_ids_list).order_by('-id'):
            health_referral_map.setdefault(health_referral.registration_id, health_referral)

        education_assessment_map = {}
        education_qs = (
            EducationProgrammeAssessment.objects.filter(registration_id__in=registration_ids_list)
            .order_by('-modified', '-id')
        )
        for education_assessment in education_qs:
            education_assessment_map.setdefault(education_assessment.registration_id, education_assessment)

        registration_history_map = {}
        if child_ids:
            history_qs = (
                Registration.objects.filter(child_id__in=child_ids, deleted=False)
                .select_related('round', 'center')
                .order_by('child_id', 'registration_date', 'created', 'id')
            )
            for history_record in history_qs:
                registration_history_map.setdefault(history_record.child_id, []).append(history_record)

        children_context = [
            _build_child_context(
                registration,
                services_map.get(registration.id, []),
                attendance_map.get(registration.id, []),
                pss_map.get(registration.id),
                health_service_map.get(registration.id),
                health_referral_map.get(registration.id),
                education_assessment_map.get(registration.id),
                registration_history=registration_history_map.get(registration.child_id, []),
            )
            for registration in registrations
        ]

        if focus_topics:
            for child in children_context:
                child['focus_topics'] = sorted(focus_topics)

        children_context.sort(key=lambda child: child['risk_score'], reverse=True)
        children_context = children_context[:limit_value]

        analysis = ''
        error = None
        model_name = getattr(settings, 'OPENAI_HEALTH_AGENT_MODEL', None)

        if children_context:
            try:
                agent = HealthSupportAgent()
                analysis = agent.analyze_children(
                    children_context,
                    question=question_text,
                    focus_topics=focus_topics,
                )
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
        if question_text:
            response_payload['question'] = question_text
        if focus_topics:
            response_payload['focus_topics'] = sorted(focus_topics)
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

    @staticmethod
    def _normalize_question(question):
        if not isinstance(question, str):
            return ''
        return question.strip()


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
        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=dt.datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
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
