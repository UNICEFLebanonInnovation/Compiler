"""Remove unstarted bulk requests under the same row locks as preparation."""
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Exists, OuterRef

from .models import BulkSyncRun, SyncEvent
from .partner_scope import available_partners


def pending_for_user(user, partner):
    runs = BulkSyncRun.objects.filter(
        partner=partner, partner__in=available_partners(user),
        preparation='waiting', queued_counts={},
    )
    if not user.is_superuser:
        runs = runs.filter(requested_by=user)
    return runs.annotate(_has_events=Exists(
        SyncEvent.objects.filter(bulk_run_id=OuterRef('pk')),
    )).filter(_has_events=False)


def remove_pending(user, partner, run_ids):
    if not (user.is_active and user.is_staff and user.has_perm('datasync.add_bulksyncrun')):
        raise PermissionDenied
    confirmed = set(run_ids)
    with transaction.atomic():
        # Preparation takes these row locks too. Skip busy rows instead of
        # waiting for a worker or removing a request that it has already begun.
        locked = list(pending_for_user(user, partner).filter(pk__in=confirmed)
                      .select_for_update(skip_locked=True))
        removable = [run.pk for run in locked
                     if run.preparation == 'waiting' and not run.queued_counts and not run.events.exists()]
        if removable:
            BulkSyncRun.objects.filter(pk__in=removable).delete()
    return len(removable), len(confirmed) - len(removable)
