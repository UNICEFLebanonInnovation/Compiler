"""The Makani wellbeing API, for NeuroDB (the only reader): BMA calculates, NeuroDB shows.

    GET  /api/wellbeing/flags/?modified_since=<ISO>&after=<id>&limit=<n>   flags, oldest change first
    POST /api/wellbeing/flags/<id>/follow-up/                              record a follow-up
    GET  /api/wellbeing/summaries/?month=YYYY-MM-01                        centre summaries (counts)
    POST /api/wellbeing/runs/ {"center": optional id}                      calculate now (queued)
    GET  /api/wellbeing/runs/<id>/                                         how that calculation went

NeuroDB decides when the flags are calculated (it holds the schedule); BMA keeps none.

Children are identified by their BMA registration number only: no name, no contact detail, no
date of birth (an age band). Only the NeuroDB service account (the group named by
YOUTH_FIGURES_API_GROUP, "NeuroDB API") or a superuser may call it.
"""

import datetime

from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from student_registration.youth.indicator_figures_api import CanReadIndicatorFigures

from .engine import _age_band
from .models import CenterSummary, Flag, FlagSettings, today

MAX_LIMIT = 1000
SETTINGS_FIELDS = ('absence_streak', 'attendance_window_days', 'attendance_min_days', 'attendance_rate_below',
                   'drop_recent_days', 'drop_previous_days', 'drop_points', 'service_weeks', 'followup_days',
                   'all_present_min_children')


class IsNeuroDB(CanReadIndicatorFigures):
    message = 'Only the NeuroDB service account can use the wellbeing API.'


class WellbeingThrottle(UserRateThrottle):
    scope = 'neurodb_wellbeing'

    def get_rate(self):
        return getattr(settings, 'WELLBEING_API_RATE', '600/hour')


class Base(APIView):
    permission_classes = (permissions.IsAuthenticated, IsNeuroDB)
    throttle_classes = (WellbeingThrottle,)


def _date(value):
    return value.isoformat() if value else None


def flag_json(flag, when=None):
    child = flag.child
    return {
        'id': flag.id,
        'registration': flag.registration_id,
        'kind': flag.kind,
        'kind_label': flag.get_kind_display(),
        'status': flag.status,
        'urgent': flag.urgent,
        'priority': flag.priority,
        'reason': flag.reason,
        'evidence': flag.evidence,
        'as_of': _date(flag.as_of),
        'opened_on': _date(flag.opened_on),
        'last_seen_on': _date(flag.last_seen_on),
        'resolved_on': _date(flag.resolved_on),
        'follow_up': {
            'on': _date(flag.followed_up_on),
            'type': flag.follow_up_type,
            'result': flag.result,
            'result_label': flag.get_result_display() if flag.result else '',
            'note': flag.note,
            'by': flag.followed_up_by_name or (flag.followed_up_by.get_full_name() if flag.followed_up_by_id else ''),
        } if flag.followed_up_on else None,
        'center': {'id': flag.center_id, 'name': flag.center.name if flag.center_id else ''},
        'partner': {'id': flag.partner_id, 'name': flag.partner.name if flag.partner_id else ''},
        'round': {'id': flag.round_id, 'name': flag.round.name if flag.round_id else ''},
        'child': {
            'gender': (child.gender if child else '') or '',
            'age_band': _age_band(child, when or today()) if child else 'Unknown',
            'nationality': (child.nationality.name if child and child.nationality_id else '') or '',
        },
        'bma_path': reverse('mscc:child_profile', args=[flag.registration_id]),
        'modified': flag.modified.isoformat(),
    }


class FlagsView(Base):
    def get(self, request):
        qs = (Flag.objects.select_related('child', 'child__nationality', 'center', 'partner', 'round',
                                          'followed_up_by')
              .order_by('id'))
        since = request.query_params.get('modified_since')
        if since:
            moment = parse_datetime(since)
            if moment is None:
                return Response({'detail': 'modified_since must be an ISO date-time'}, status=400)
            qs = qs.filter(modified__gte=moment)
        after = request.query_params.get('after', '')
        if after.isdigit():
            qs = qs.filter(id__gt=int(after))
        try:
            limit = max(1, min(int(request.query_params.get('limit', 500)), MAX_LIMIT))
        except ValueError:
            limit = 500
        rows = list(qs[:limit + 1])
        more = len(rows) > limit
        rows = rows[:limit]
        current = FlagSettings.current()
        return Response({
            'flags': [flag_json(f) for f in rows],
            'next_after': rows[-1].id if more else None,
            'kinds': dict(Flag.KINDS),
            'results': dict(Flag.RESULTS),
            'settings': {name: getattr(current, name) for name in SETTINGS_FIELDS},
            'served_at': datetime.datetime.now().isoformat(),
        })


class FollowUpSerializer(serializers.Serializer):
    follow_up_type = serializers.CharField(max_length=40)
    result = serializers.ChoiceField(choices=Flag.RESULTS)
    followed_up_on = serializers.DateField()
    note = serializers.CharField(max_length=2000, allow_blank=True, required=False, default='')
    by = serializers.CharField(max_length=150)

    def validate_followed_up_on(self, value):
        if value > today():
            raise serializers.ValidationError('The date is in the future.')
        return value


class FollowUpView(Base):
    def post(self, request, pk):
        flag = (Flag.objects.select_related('child', 'child__nationality', 'center', 'partner', 'round')
                .filter(pk=pk).first())
        if flag is None:
            return Response({'detail': 'No such flag'}, status=404)
        if flag.status != Flag.OPEN:
            return Response({'detail': 'This flag is no longer open.', 'flag': flag_json(flag)}, status=409)
        data = FollowUpSerializer(data=request.data)
        if not data.is_valid():
            return Response(data.errors, status=400)
        values = data.validated_data
        if values['followed_up_on'] < flag.opened_on:
            return Response({'followed_up_on': ['The date is before the flag was raised.']}, status=400)
        flag.status = Flag.FOLLOWED_UP
        flag.follow_up_type = values['follow_up_type']
        flag.result = values['result']
        flag.followed_up_on = values['followed_up_on']
        flag.note = values['note']
        flag.followed_up_by_name = values['by']
        flag.save()
        return Response({'flag': flag_json(flag)})


class SummariesView(Base):
    def get(self, request):
        months = list(CenterSummary.objects.values_list('month', flat=True).distinct().order_by('-month'))
        try:
            month = datetime.date.fromisoformat(request.query_params.get('month', ''))
        except ValueError:
            month = months[0] if months else None
        rows = (CenterSummary.objects.filter(month=month).select_related('center', 'partner', 'round')
                .order_by('center__name') if month else [])
        return Response({
            'month': _date(month),
            'months': [_date(m) for m in months],
            'summaries': [{
                'center': {'id': s.center_id, 'name': s.center.name,
                           'governorate': s.center.governorate.name if s.center.governorate_id else ''},
                'partner': {'id': s.partner_id, 'name': s.partner.name if s.partner_id else ''},
                'round': {'id': s.round_id, 'name': s.round.name if s.round_id else ''},
                'figures': s.figures,
                'computed_at': s.computed_at.isoformat(),
            } for s in rows],
            'kinds': dict(Flag.KINDS),
        })


class RunsView(Base):
    def post(self, request):
        center = request.data.get('center')
        if center not in (None, '') and not str(center).isdigit():
            return Response({'detail': 'center must be a centre id'}, status=400)
        from . import runs

        run, created = runs.start([int(center)] if center not in (None, '') else [],
                                  requested_by=request.user.get_username())
        return Response(run.as_dict(), status=202 if created else 200)


class RunView(Base):
    def get(self, request, pk):
        from .models import WellbeingRun

        run = WellbeingRun.objects.filter(pk=pk).first()
        if run is None:
            return Response({'detail': 'No such run'}, status=404)
        return Response(run.as_dict())
