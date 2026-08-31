# -*- coding: utf-8 -*-
"""Capture MSCC changes as they are saved.

Hooking the models rather than the views means every path that writes a
replicated record is covered -- the MSCC forms, the Django admin, the import
tools and any management command -- so a partner never has to think about
whether a particular screen is "the one that syncs".

Receivers are intentionally defensive. Replication is a background concern:
a failure here is logged and swallowed so it can never break a partner's
save.
"""

from __future__ import unicode_literals, absolute_import, division

import logging

from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.mscc.models import Registration
from student_registration.students.models import Teacher

from .constants import RESOURCE_ATTENDANCE, RESOURCE_REGISTRATION, RESOURCE_TEACHER
from .outbox import enqueue, enqueue_delete, enqueue_instance, sync_enabled
from .serializers import REGISTRY

logger = logging.getLogger(__name__)


def _safe(action, description):
    """Run ``action``, logging and swallowing anything it raises."""
    try:
        action()
    except Exception:  # noqa: BLE001 - replication must never break a save
        logger.exception('datasync: could not queue %s', description)


def _replicated_saved(sender, instance, created, raw=False, **kwargs):
    """Queue an upsert for any directly replicated model."""
    if raw or not sync_enabled():
        return
    _safe(
        lambda: enqueue_instance(instance),
        '{} #{}'.format(sender.__name__, instance.pk),
    )


def _replicated_deleted(sender, instance, **kwargs):
    """Queue a delete for any directly replicated model."""
    if not sync_enabled():
        return
    _safe(
        lambda: enqueue_delete(instance),
        'deletion of {} #{}'.format(sender.__name__, instance.pk),
    )


@receiver(post_save, sender=Child, dispatch_uid='datasync_child_saved')
def child_saved(sender, instance, raw=False, **kwargs):
    """Re-push every registration of a child whose details changed.

    Children travel embedded in their registration rather than as a resource
    of their own, so a change to the child is published through each
    registration that carries it.
    """
    if raw or not sync_enabled():
        return

    def push():
        ids = Registration.objects.filter(child=instance).values_list('pk', flat=True)
        for registration_id in ids:
            enqueue(RESOURCE_REGISTRATION, registration_id)

    _safe(push, 'registrations of child #{}'.format(instance.pk))


@receiver(post_save, sender=MSCCAttendanceChild,
          dispatch_uid='datasync_attendance_child_saved')
@receiver(post_delete, sender=MSCCAttendanceChild,
          dispatch_uid='datasync_attendance_child_deleted')
def attendance_child_changed(sender, instance, raw=False, **kwargs):
    """Re-push the attendance day when one of its child rows changes.

    An attendance day and its rows are replicated as a single event, so any
    row-level change republishes the whole day.
    """
    if raw or not sync_enabled():
        return
    if not instance.attendance_day_id:
        return
    _safe(
        lambda: enqueue(RESOURCE_ATTENDANCE, instance.attendance_day_id),
        'attendance day #{}'.format(instance.attendance_day_id),
    )


@receiver(m2m_changed, sender=Teacher.trainings.through,
          dispatch_uid='datasync_teacher_trainings_changed')
def teacher_trainings_changed(sender, instance, action, reverse=False, **kwargs):
    """Re-push a teacher when their training topics change."""
    if not sync_enabled() or reverse:
        return
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    _safe(
        lambda: enqueue(RESOURCE_TEACHER, instance.pk),
        'trainings of teacher #{}'.format(instance.pk),
    )


def connect():
    """Wire the receivers for every directly replicated model.

    Called from :meth:`DataSyncConfig.ready`. Connecting by ``dispatch_uid``
    makes the call idempotent, which matters because Django can import an app
    config more than once in some management commands.
    """
    for model, resource, _serializer in REGISTRY:
        post_save.connect(
            _replicated_saved,
            sender=model,
            dispatch_uid='datasync_saved_{}'.format(resource),
        )
        post_delete.connect(
            _replicated_deleted,
            sender=model,
            dispatch_uid='datasync_deleted_{}'.format(resource),
        )
