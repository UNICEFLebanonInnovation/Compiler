"""Persistent photo-export batches, executed by the existing export pool."""

import datetime
import logging
import uuid
from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .child_photo_export import build_photo_roster
from .models import ExportHistory
from .utils import ExportStorage


logger = logging.getLogger(__name__)
BATCH_SIZE = 2000
STALE_AFTER = datetime.timedelta(minutes=30)
JOB_KIND = 'child_photo_job'
BATCH_KIND = 'child_photo_batch'


def scoped_registrations(user, programme):
    """Recheck the list's current role and row scope in workers and downloads."""
    if programme == 'makani':
        from student_registration.mscc.views import ChildPhotoExportView
        view, group = ChildPhotoExportView(), 'MSCC'
    elif programme == 'dirasa':
        from student_registration.clm.bridging_views import BridgingChildPhotoExportView
        view, group = BridgingChildPhotoExportView(), 'CLM_Bridging'
    else:
        raise Http404
    if not user or not user.is_active or not user.is_authenticated:
        raise PermissionDenied
    if not (user.is_superuser or user.groups.filter(name=group).exists()):
        raise PermissionDenied
    view.request = SimpleNamespace(user=user)
    return view.get_queryset()


def schedule_batch(batch_id, attempt):
    from student_registration.mscc.tasks import _get_executor, _run_with_new_db_connection
    try:
        _get_executor().submit(_run_with_new_db_connection, generate_batch, batch_id, attempt)
    except Exception:
        ExportHistory.objects.filter(pk=batch_id, fields__attempt=attempt).update(status='failed')
        logger.exception('Could not queue photo export batch %s', batch_id)
        batch = ExportHistory.objects.filter(pk=batch_id).first()
        if batch:
            update_job_status(batch.fields['job_id'])


def create_job(user, programme, queryset, filters):
    person = 'child' if programme == 'makani' else 'student'
    ids = list(queryset.filter(**{person + '__isnull': False}).order_by('pk')
               .values_list('pk', flat=True).distinct())
    export_type = 'Makani List' if programme == 'makani' else 'Bridging List'
    with transaction.atomic():
        # Repeated clicks should reopen the existing job, not queue the same
        # expensive photo downloads again. Serialize starts for this requester.
        get_user_model().objects.select_for_update().get(pk=user.pk)
        candidates = ExportHistory.objects.filter(
            created_by=user, status='pending', fields__kind=JOB_KIND,
            fields__programme=programme, fields__filters=filters,
            fields__total=len(ids), fields__batch_size=BATCH_SIZE)
        for existing in candidates:
            snapshots = ExportHistory.objects.filter(
                created_by=user, fields__kind=BATCH_KIND, fields__job_id=existing.pk).order_by('pk')
            if [pk for part in snapshots for pk in part.fields['ids']] == ids:
                return existing
        job = ExportHistory.objects.create(
            created_by=user, export_type=export_type, file_format='xlsx',
            status='pending' if ids else 'done', fields={
                'kind': JOB_KIND, 'programme': programme, 'filters': filters,
                'total': len(ids), 'batch_size': BATCH_SIZE,
            })
        job.file_url = reverse('backends:photo_batch_progress', args=[job.pk])
        job.save(update_fields=['file_url', 'modified'])
        for start in range(0, len(ids), BATCH_SIZE):
            attempt = uuid.uuid4().hex
            batch = ExportHistory.objects.create(
                created_by=user, export_type=export_type, file_format='xlsx', fields={
                    'kind': BATCH_KIND, 'job_id': job.pk, 'programme': programme,
                    'number': start // BATCH_SIZE + 1, 'ids': ids[start:start + BATCH_SIZE],
                    'state': 'queued', 'attempt': attempt,
                })
            transaction.on_commit(lambda pk=batch.pk, token=attempt: schedule_batch(pk, token))
    return job


def batch_queryset(batch):
    fields = batch.fields
    qs = scoped_registrations(batch.created_by, fields['programme']).filter(pk__in=fields['ids'])
    if set(qs.values_list('pk', flat=True)) != set(fields['ids']):
        raise PermissionDenied('Some registrations are no longer available within your access scope.')
    return qs.order_by('pk')


def update_job_status(job_id):
    with transaction.atomic():
        job = ExportHistory.objects.select_for_update().get(pk=job_id, fields__kind=JOB_KIND)
        states = list(ExportHistory.objects.filter(
            created_by_id=job.created_by_id, fields__kind=BATCH_KIND,
            fields__job_id=job_id).values_list('status', flat=True))
        job.status = ('pending' if 'pending' in states else
                      'failed' if 'failed' in states else 'done')
        job.save(update_fields=['status', 'modified'])


def generate_batch(batch_id, attempt):
    batch = ExportHistory.objects.select_related('created_by').filter(
        pk=batch_id, fields__kind=BATCH_KIND, fields__attempt=attempt,
        fields__state='queued', status='pending',
    ).first()
    if batch is None:
        return
    metadata = dict(batch.fields, state='running')
    active = ExportHistory.objects.filter(
        pk=batch_id, fields__attempt=attempt, fields__state='queued', status='pending')
    if not active.update(fields=metadata, modified=timezone.now()):
        return
    active = ExportHistory.objects.filter(pk=batch_id, fields__attempt=attempt, status='pending')
    try:
        def registrations():
            for registration in batch_queryset(batch).iterator(chunk_size=BATCH_SIZE):
                if not active.update(modified=timezone.now()):
                    raise RuntimeError('This batch attempt was replaced.')
                yield registration

        content = build_photo_roster(registrations(), metadata['programme'], all_ages=True)
        # Permissions may have changed during a slow photo download.
        batch.created_by.refresh_from_db()
        batch_queryset(batch)
        if not active.exists():
            return
        filename = ExportStorage().save('photo_batch_{}.xlsx'.format(uuid.uuid4().hex), ContentFile(content))
        active.update(status='done', fields=dict(metadata, state='done', filename=filename),
                      file_url=reverse('backends:photo_batch_download', args=[batch.pk]), modified=timezone.now())
    except Exception:
        active.update(status='failed', fields=dict(metadata, state='failed'), modified=timezone.now())
        logger.exception('Photo export batch %s failed', batch_id)
    finally:
        update_job_status(metadata['job_id'])


def owned_export(user, pk, kind):
    export = get_object_or_404(ExportHistory.objects.select_related('created_by'),
                               pk=pk, created_by=user, fields__kind=kind)
    scoped_registrations(user, export.fields['programme'])
    return export


@login_required
@require_GET
def progress(request, job_id):
    job = owned_export(request.user, job_id, JOB_KIND)
    batches = list(ExportHistory.objects.filter(
        created_by=request.user, fields__kind=BATCH_KIND, fields__job_id=job.pk).order_by('pk'))
    ready = sum(batch.status == 'done' for batch in batches)
    waiting = False
    for batch in batches:
        batch.interrupted = batch.status == 'pending' and batch.modified < timezone.now() - STALE_AFTER
        batch.can_retry = batch.status == 'failed' or batch.interrupted
        batch.row_count = len(batch.fields['ids'])
        waiting |= batch.status == 'pending' and not batch.interrupted
    response = render(request, 'backends/photo_batch_progress.html', {
        'job': job, 'batches': batches, 'ready': ready, 'waiting': waiting,
        'module_base': 'mscc/base.html' if job.fields['programme'] == 'makani' else 'clm/base.html',
    })
    response['Cache-Control'] = 'private, no-store'
    return response


@login_required
@require_POST
def retry(request, batch_id):
    batch = owned_export(request.user, batch_id, BATCH_KIND)
    eligible = ExportHistory.objects.filter(pk=batch.pk, status='failed')
    if batch.status == 'pending':
        eligible = ExportHistory.objects.filter(pk=batch.pk, status='pending', modified__lt=timezone.now() - STALE_AFTER)
    attempt = uuid.uuid4().hex
    metadata = dict(batch.fields, state='queued', attempt=attempt)
    metadata.pop('filename', None)
    with transaction.atomic():
        if eligible.update(status='pending', fields=metadata, file_url='', modified=timezone.now()):
            ExportHistory.objects.filter(pk=batch.fields['job_id'], created_by=request.user).update(
                status='pending', modified=timezone.now())
            transaction.on_commit(lambda: schedule_batch(batch.pk, attempt))
    return redirect('backends:photo_batch_progress', job_id=batch.fields['job_id'])


@login_required
@require_GET
def download(request, batch_id):
    batch = owned_export(request.user, batch_id, BATCH_KIND)
    if batch.status != 'done' or not batch.fields.get('filename'):
        raise Http404
    batch_queryset(batch)
    source = None
    try:
        source = ExportStorage().open(batch.fields['filename'], 'rb')
        # Force Azure to finish its bounded-range download before sending 200.
        source.seek(0)
    except Exception:
        if source is not None:
            source.close()
        # Allow an individual batch to be regenerated if its stored file expired.
        ExportHistory.objects.filter(pk=batch.pk).update(status='failed', modified=timezone.now())
        update_job_status(batch.fields['job_id'])
        return redirect('backends:photo_batch_progress', job_id=batch.fields['job_id'])
    response = FileResponse(source, as_attachment=True, filename='{}-photos-batch-{:03d}.xlsx'.format(
        batch.fields['programme'], batch.fields['number']),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Cache-Control'] = 'private, no-store'
    return response
