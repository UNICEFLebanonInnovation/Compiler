import datetime
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pathlib
import sys
import os

import django
from django.conf import settings
from django.db.utils import OperationalError

import pytest
os.environ['DATABASE_URL'] = 'sqlite:///test.sqlite3'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

from rest_framework.test import APIRequestFactory, force_authenticate

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

django.setup()

import student_registration.mscc.attendance_views as attendance_views

settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

from student_registration.mscc.attendance_views import AttendanceHeatmapViewSet
from student_registration.mscc.utils import parse_attendance_date, create_attendance


def test_attendance_heatmap_api_monthly_percentages():
    request = APIRequestFactory().get('/attendance-heatmap-data/percentage/', {'year': '2024'})
    request.user = SimpleNamespace(is_authenticated=True, is_active=True)
    force_authenticate(request, request.user)

    base_qs = MagicMock(name='base_qs')
    base_qs.filter.return_value = base_qs
    base_qs.filter.return_value = base_qs

    with patch(
        'student_registration.mscc.attendance_views.MSCCAttendanceChild.objects'
    ) as mock_manager:
        mock_manager.filter.return_value = base_qs
        mock_manager.dates.return_value = [datetime.date(2023, 1, 1), datetime.date(2024, 1, 1)]
        mock_manager.all.return_value = base_qs

        def aggregate_side_effect(qs, *groups):
            assert qs is base_qs
            if groups == ('attendance_day__attendance_date__month',):
                return [
                    {'attendance_day__attendance_date__month': 1, 'total': 3, 'absent': 1},
                    {'attendance_day__attendance_date__month': 2, 'total': 1, 'absent': 1},
                ]
            if groups == (
                'attendance_day__attendance_date__month',
                'registration__education_service__education_program',
            ):
                return [
                    {
                        'attendance_day__attendance_date__month': 1,
                        'registration__education_service__education_program': 'BLN Level 1',
                        'total': 1,
                        'absent': 0,
                    },
                    {
                        'attendance_day__attendance_date__month': 2,
                        'registration__education_service__education_program': 'BLN Level 1',
                        'total': 1,
                        'absent': 1,
                    },
                    {
                        'attendance_day__attendance_date__month': 1,
                        'registration__education_service__education_program': 'YFS Level 1',
                        'total': 2,
                        'absent': 1,
                    },
                ]
            raise AssertionError(f'Unexpected grouping: {groups!r}')

        with patch(
            'student_registration.mscc.attendance_views._aggregate_attendance',
            side_effect=aggregate_side_effect,
        ) as mock_aggregate, patch(
            'student_registration.mscc.attendance_views._get_service_program_mapping',
            return_value=[],
        ):
            attendance_views._programme_category_lookup.cache_clear()
            view = AttendanceHeatmapViewSet.as_view({'get': 'percentage'})
            response = view(request)

    mock_manager.filter.assert_called_once()
    mock_manager.dates.assert_called_once_with('attendance_day__attendance_date', 'year')

    assert response.status_code == 200
    payload = json.loads(response.content)

    monthly = [entry for entry in payload if entry['record_type'] == 'monthly']
    programme_entries = [entry for entry in payload if entry['record_type'] == 'programme_monthly']

    january = next(entry for entry in monthly if entry['month'] == 1)
    february = next(entry for entry in monthly if entry['month'] == 2)

    assert january['attendance_percentage'] == pytest.approx(66.67, rel=1e-3)
    assert january['present'] == 2
    assert january['absent'] == 1
    assert january['total'] == 3
    assert january['month_name'] == 'January'

    assert february['attendance_percentage'] == 0.0
    assert february['present'] == 0
    assert february['absent'] == 1
    assert february['total'] == 1
    assert february['month_name'] == 'February'

    grouped_programmes = {}
    for entry in programme_entries:
        grouped_programmes.setdefault(entry['programme'], []).append(entry)

    assert set(grouped_programmes.keys()) == {'BLN Level 1', 'YFS Level 1'}

    bln_entries = sorted(grouped_programmes['BLN Level 1'], key=lambda item: item['month'])
    assert [entry['attendance_percentage'] for entry in bln_entries] == [100.0, 0.0]
    assert [entry['month'] for entry in bln_entries] == [1, 2]

    yfs_entries = grouped_programmes['YFS Level 1']
    assert [entry['attendance_percentage'] for entry in yfs_entries] == [50.0]
    assert [entry['month'] for entry in yfs_entries] == [1]

    assert all(entry['year'] == 2024 for entry in monthly)
    assert all(entry['available_years'] == '2023,2024' for entry in monthly)


def test_attendance_heatmap_disability_percentages():
    request = APIRequestFactory().get(
        '/attendance-heatmap-data/disability-percentage/',
        {'round_id': '7'},
    )
    request.user = SimpleNamespace(is_authenticated=True, is_active=True)
    force_authenticate(request, request.user)

    base_qs = MagicMock(name='base_qs')
    base_qs.filter.return_value = base_qs

    with patch(
        'student_registration.mscc.attendance_views.MSCCAttendanceChild.objects'
    ) as mock_manager:
        mock_manager.filter.return_value = base_qs
        mock_manager.all.return_value = base_qs

        def aggregate_side_effect(qs, *groups):
            assert qs is base_qs
            assert groups == (
                'registration__round_id',
                'registration__round__name',
                'registration__education_service__education_program',
                'child__disability__name',
            )
            return [
                {
                    'registration__round_id': 1,
                    'registration__round__name': 'Cycle 1',
                    'registration__education_service__education_program': 'BLN Level 1',
                    'child__disability__name': 'Visual',
                    'total': 3,
                    'absent': 1,
                },
                {
                    'registration__round_id': 1,
                    'registration__round__name': 'Cycle 1',
                    'registration__education_service__education_program': 'BLN Level 1',
                    'child__disability__name': 'Hearing',
                    'total': 2,
                    'absent': 0,
                },
            ]

        with patch(
            'student_registration.mscc.attendance_views._aggregate_attendance',
            side_effect=aggregate_side_effect,
        ), patch(
            'student_registration.mscc.attendance_views._get_service_program_mapping',
            return_value=[],
        ):
            attendance_views._programme_category_lookup.cache_clear()
            view = AttendanceHeatmapViewSet.as_view({'get': 'disability_percentage'})
            response = view(request)

    base_qs.filter.assert_called_once_with(attendance_day__round_id='7')

    assert response.status_code == 200
    payload = json.loads(response.content)

    assert [entry['disability'] for entry in payload] == ['Hearing', 'Visual']
    assert [entry['attendance_percentage'] for entry in payload] == [100.0, 66.67]
    assert all(entry['programme'] == 'BLN Level 1' for entry in payload)
    assert all(entry['cycle'] == 'Cycle 1' for entry in payload)


def test_attendance_heatmap_disability_child_percentages():
    request = APIRequestFactory().get(
        '/attendance-heatmap-data/disability-child-percentage/',
        {'year': '2025'},
    )
    request.user = SimpleNamespace(is_authenticated=True, is_active=True)
    force_authenticate(request, request.user)

    base_qs = MagicMock(name='base_qs')

    with patch(
        'student_registration.mscc.attendance_views.MSCCAttendanceChild.objects'
    ) as mock_manager:
        mock_manager.filter.return_value = base_qs

        def aggregate_side_effect(qs, *groups):
            assert qs is base_qs
            assert groups == (
                'child_id',
                'child__full_name',
                'child__disability__name',
            )
            return [
                {
                    'child_id': 1,
                    'child__full_name': 'Alice',
                    'child__disability__name': 'Hearing',
                    'total': 3,
                    'absent': 1,
                },
                {
                    'child_id': 2,
                    'child__full_name': None,
                    'child__disability__name': None,
                    'total': 2,
                    'absent': 0,
                },
            ]

        with patch(
            'student_registration.mscc.attendance_views._aggregate_attendance',
            side_effect=aggregate_side_effect,
        ):
            view = AttendanceHeatmapViewSet.as_view({'get': 'disability_child_percentage'})
            response = view(request)

    mock_manager.filter.assert_called_once_with(
        attendance_day__attendance_date__year=2025,
        child__disability__isnull=False,
    )

    assert response.status_code == 200
    payload = json.loads(response.content)

    assert [entry['child_name'] for entry in payload] == ['Alice', 'Unknown']
    assert [entry['disability'] for entry in payload] == ['Hearing', 'Unknown']
    assert [entry['attendance_percentage'] for entry in payload] == [66.67, 100.0]
    assert all(entry['record_type'] == 'disability_child' for entry in payload)
    assert all(entry['year'] == 2025 for entry in payload)


def test_parse_attendance_date_handles_trailing_characters():
    parsed = parse_attendance_date('07/01/20241')
    assert parsed == datetime.date(2024, 7, 1)


def test_parse_attendance_date_handles_iso_timestamps():
    parsed = parse_attendance_date('2024-07-01T00:00:00Z')
    assert parsed == datetime.date(2024, 7, 1)


def test_parse_attendance_date_invalid_input():
    with pytest.raises(ValueError):
        parse_attendance_date('not-a-date')


def test_create_attendance_retries_admin_terminated_connection():
    payload = {
        'attendance_date': '07/01/2024',
        'attendance_day_off': 'No',
        'close_reason': '',
        'round_id': 1,
        'education_program': 'BLN Level 1',
        'class_section': 'A',
        'children_attendance': []
    }

    attendance_obj = MagicMock()

    with patch(
        'student_registration.mscc.utils.MSCCAttendance.objects.get_or_create',
        side_effect=[
            OperationalError('terminating connection due to administrator command'),
            (attendance_obj, True),
        ],
    ) as mock_get_or_create, patch(
        'student_registration.mscc.utils.close_old_connections'
    ) as mock_close_old_connections:
        result = create_attendance(payload, center_id=1)

    assert result is True
    assert mock_get_or_create.call_count == 2
    mock_close_old_connections.assert_called_once()
