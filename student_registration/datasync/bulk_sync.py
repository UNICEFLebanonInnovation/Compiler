"""Partner/round selection and durable queueing through the existing outbox."""
import logging

from django.db import transaction
from django.db.models import Count, F, Q

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round

from .bulk_types import ALL_CATEGORIES, CATEGORY_LABELS, normalize_categories, requires_round, selection_kind
from .constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_EDUCATION_SERVICE,
    RESOURCE_ORDER, RESOURCE_REGISTRATION, RESOURCE_ROUND, RESOURCE_TEACHER,
)
from .models import BulkSyncRun
from .outbox import enqueue_many, sync_enabled
from .serializers import MODEL_FOR_RESOURCE
from .partner_scope import available_partners
from .makani_scope import scoped_queryset, registrations as makani_registrations

logger = logging.getLogger(__name__)


class PlanError(ValueError):
    pass


class RoundSyncPlan:
    """Selected categories plus the parents needed by the current wire contract."""

    def __init__(self, round_object, category, partner=None):
        if partner is None:
            raise PlanError('Choose a partner before starting a bulk sync.')
        self.partner = partner
        try:
            self.categories = normalize_categories(category)
        except ValueError as error:
            raise PlanError(str(error)) from error
        if requires_round(self.categories) and round_object is None:
            raise PlanError('Choose a round for the selected categories.')
        self.round = round_object if requires_round(self.categories) else None
        round_object = self.round
        self.category = selection_kind(self.categories)
        self.selected = set(RESOURCE_ORDER if self.categories == [ALL_CATEGORIES] else self.categories)
        registrations = (makani_registrations().filter(round=round_object, partner=partner)
                         if round_object else Registration.objects.none())
        attendance = (scoped_queryset(RESOURCE_ATTENDANCE).filter(round_id=round_object.pk, center__partner=partner)
                      if round_object else MSCCAttendance.objects.none())
        # Makani staff belong directly to centres, independently of rounds.
        teachers = scoped_queryset(RESOURCE_TEACHER).filter(center__partner=partner)
        teacher_centers = teachers.order_by().values('center_id')
        centers = scoped_queryset(RESOURCE_CENTER).filter(partner=partner)
        self.queries = {
            RESOURCE_ROUND: (Round.objects.filter(pk=round_object.pk) if round_object else Round.objects.none()),
            RESOURCE_CENTER: centers,
            RESOURCE_TEACHER: teachers,
            RESOURCE_REGISTRATION: registrations,
            RESOURCE_ATTENDANCE: attendance,
        }
        for resource in RESOURCE_ORDER:
            if resource not in self.queries:
                self.queries[resource] = scoped_queryset(resource).filter(
                    registration__round=round_object, registration__partner=partner,
                ) if round_object else MODEL_FOR_RESOURCE[resource].objects.none()

        # Keep dependencies narrow: selecting one assessment does not queue
        # every registration, teacher or centre in the round.
        selected_queries = {key: self.queries[key] for key in self.selected}
        registration_filter = Q(pk__in=[])
        if RESOURCE_REGISTRATION in self.selected and round_object:
            registration_filter |= Q(pk__in=registrations.order_by().values('pk'))
        for resource, query in selected_queries.items():
            if resource not in (RESOURCE_ROUND, RESOURCE_CENTER, RESOURCE_TEACHER,
                                RESOURCE_REGISTRATION, RESOURCE_ATTENDANCE):
                registration_filter |= Q(pk__in=query.order_by().values('registration_id'))
        self.attendance_rows = MSCCAttendanceChild.objects.filter(
            attendance_day_id__in=attendance.order_by().values('pk'),
        ) if RESOURCE_ATTENDANCE in self.selected else MSCCAttendanceChild.objects.none()
        registration_filter |= Q(pk__in=self.attendance_rows.order_by().values('registration_id'))
        required_registrations = makani_registrations().filter(registration_filter, partner=partner)
        self.queries[RESOURCE_REGISTRATION] = required_registrations

        center_filter = Q(pk__in=required_registrations.order_by().values('center_id'))
        if RESOURCE_CENTER in self.selected:
            center_filter |= Q(pk__in=centers.order_by().values('pk'))
        if RESOURCE_TEACHER in self.selected:
            center_filter |= Q(pk__in=teacher_centers)
        if RESOURCE_ATTENDANCE in self.selected:
            center_filter |= Q(pk__in=attendance.order_by().values('center_id'))
        self.queries[RESOURCE_CENTER] = Center.objects.filter(center_filter, partner=partner)
        included = self.selected | {RESOURCE_ROUND, RESOURCE_CENTER, RESOURCE_REGISTRATION}
        self.queries = {key: self.queries[key].order_by('pk')
                        for key in RESOURCE_ORDER if key in included}

    def summary(self):
        return [dict(resource=key, label=CATEGORY_LABELS[key], count=query.count(),
                     supporting=key not in self.selected, scope=self.resource_scope(key))
                for key, query in self.queries.items()]

    def resource_scope(self, resource):
        if resource == RESOURCE_TEACHER:
            return 'Selected partner — all rounds'
        if resource == RESOURCE_CENTER:
            return 'Selected partner — all rounds' if resource in self.selected else 'Referenced centres of selected partner'
        return 'Shared round metadata' if resource == RESOURCE_ROUND else 'Selected partner and round'

    def errors(self):
        errors = []
        if not any(self.queries[resource].exists() for resource in self.selected):
            errors.append('No records were found for the selected categories in this scope.')
        if self.queries[RESOURCE_REGISTRATION].exclude(center__isnull=True).exclude(center__partner=self.partner).exists():
            errors.append('Some registration centres belong to another partner. Correct those links first.')
        if self.attendance_rows.exclude(registration__isnull=True).exclude(registration__partner=self.partner).exists():
            errors.append('Attendance includes registrations from another partner. Correct those links first.')
        if self.attendance_rows.exclude(registration__isnull=True).exclude(child_id=F('registration__child_id')).exists():
            errors.append('Attendance child differs from its registration. Correct those links first.')
        if self.attendance_rows.exclude(registration__isnull=True).exclude(
                registration__round=self.round).exists():
            errors.append('Attendance includes registrations from another round. Correct those links first.')
        if RESOURCE_EDUCATION_SERVICE in self.selected:
            if self.queries[RESOURCE_EDUCATION_SERVICE].exclude(round__isnull=True).exclude(
                    round=self.round).exists():
                errors.append('Some education services use a different round from their registration. Correct those links first.')
        return errors

    def preview(self, offset, limit):
        """Slice across categories without loading the entire round into memory."""
        rows = []
        for resource, query in self.queries.items():
            count = query.count()
            if offset >= count:
                offset -= count
                continue
            if resource == RESOURCE_REGISTRATION:
                query = query.select_related('child', 'center')
            elif resource == RESOURCE_TEACHER:
                query = query.select_related('center')
            for instance in query[offset:offset + limit - len(rows)]:
                rows.append(dict(source_id=instance.pk, label=CATEGORY_LABELS[resource],
                                 description=record_description(resource, instance),
                                 supporting=resource not in self.selected, scope=self.resource_scope(resource)))
            offset = 0
            if len(rows) == limit:
                break
        return rows


def record_description(resource, instance):
    if resource in (RESOURCE_ROUND, RESOURCE_CENTER):
        return instance.name
    if resource == RESOURCE_REGISTRATION:
        child = instance.child
        name = ' '.join(filter(None, [child.first_name, child.last_name])) if child else 'No child linked'
        return '{} · {}'.format(name, instance.center or 'No centre linked')
    if resource == RESOURCE_TEACHER:
        return '{} · {}'.format(instance.facilitator_name, instance.center or 'No centre linked')
    if resource == RESOURCE_ATTENDANCE:
        return 'Attendance on {}'.format(instance.attendance_date or 'No date')
    return 'Registration #{}'.format(instance.registration_id or '—')


def prepare_run(run_id):
    """One transaction creates the complete outbox set, once, with no HTTP."""
    if not sync_enabled():
        return
    try:
        with transaction.atomic():
            run = (BulkSyncRun.objects.select_for_update(skip_locked=True)
                   .filter(pk=run_id, preparation='waiting').first())
            if run is None:
                return
            if run.requested_by_id and not available_partners(run.requested_by).filter(pk=run.partner_id).exists():
                raise PlanError('The requesting operator no longer has access to this partner.')
            plan = RoundSyncPlan(run.round, run.selected_categories, run.partner)
            errors = plan.errors()
            if errors:
                raise PlanError(' '.join(errors))
            run.queued_counts = {
                resource: enqueue_many(resource, query.values_list('pk', flat=True).iterator(chunk_size=1000), run)
                for resource, query in plan.queries.items()
            }
            run.preparation = 'ready'
            run.last_error = ''
            run.save(update_fields=['queued_counts', 'preparation', 'last_error', 'modified'])
    except Exception as error:
        logger.exception('datasync: could not prepare bulk run %s', run_id)
        detail = str(error) if isinstance(error, PlanError) else 'Could not queue records. Check Compiler logs, correct the problem, and retry queueing.'
        BulkSyncRun.objects.filter(pk=run_id, preparation='waiting').update(
            preparation='failed', last_error=detail,
        )


def prepare_waiting_runs(limit=1):
    for run_id in list(BulkSyncRun.objects.filter(preparation='waiting')
                       .order_by('created').values_list('pk', flat=True)[:limit]):
        prepare_run(run_id)


def schedule_bulk_sweep():
    """Broker outages leave the durable request for the next periodic sweep."""
    from .tasks import flush_sync_outbox
    try:
        flush_sync_outbox.delay()
    except Exception:
        logger.warning('datasync: bulk request saved; scheduled sweep will queue it when the broker recovers')


def run_progress(run):
    counts = dict(run.events.order_by().values_list('status').annotate(total=Count('pk')))
    total = sum(counts.values())
    sent = counts.get('sent', 0)
    if run.preparation != 'ready':
        status = run.get_preparation_display()
    elif counts.get('abandoned'):
        status = 'Needs attention'
    elif counts.get('failed'):
        status = 'Retrying failed deliveries'
    elif total and sent == total:
        status = 'Completed'
    elif total:
        status = 'Syncing'
    else:
        status = 'No records queued'
    return dict(status=status, total=total, sent=sent, pending=counts.get('pending', 0),
                failed=counts.get('failed', 0), abandoned=counts.get('abandoned', 0),
                percent=round(100 * sent / total) if total else 0)
