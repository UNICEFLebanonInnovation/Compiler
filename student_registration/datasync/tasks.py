# -*- coding: utf-8 -*-
"""Celery tasks that move the replication outbox.

``deliver_sync_event`` is queued the moment a record is saved, which is what
makes the copy in BMA-NFE appear immediately. ``flush_sync_outbox`` runs on a
schedule and is the safety net: it re-sends anything that failed, anything
queued while BMA-NFE was unreachable, and anything a dead worker dropped.
"""

from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task

from .outbox import sync_enabled

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='datasync.deliver_sync_event', ignore_result=True)
def deliver_sync_event(self, event_pk):
    """Deliver one outbox row to BMA-NFE.

    Failures are recorded on the event itself with a retry time, so the task
    does not raise: the periodic sweep owns retrying, and a Celery-level retry
    on top of that would double the backoff.

    Args:
        event_pk: Primary key of the ``SyncEvent`` to deliver.

    Returns:
        dict: ``{"sent": n, "failed": n, "abandoned": n}``.
    """
    if not sync_enabled():
        return {'sent': 0, 'failed': 0, 'abandoned': 0}

    from .dispatch import deliver_event

    return deliver_event(event_pk)


@shared_task(name='datasync.flush_sync_outbox', ignore_result=True)
def flush_sync_outbox(limit=None):
    """Send every event whose retry time has come.

    Args:
        limit (int): Maximum events per batch; the configured batch size by
            default.

    Returns:
        dict: Totals across the batches that ran.
    """
    if not sync_enabled():
        return {'sent': 0, 'failed': 0, 'abandoned': 0, 'batches': 0}

    from .dispatch import flush_outbox

    totals = flush_outbox(limit=limit)
    if totals['batches']:
        logger.info(
            'datasync: swept the outbox -- %s sent, %s failed, %s abandoned',
            totals['sent'], totals['failed'], totals['abandoned'],
        )
    return totals
