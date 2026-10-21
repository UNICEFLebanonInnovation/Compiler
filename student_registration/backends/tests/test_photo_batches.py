import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils import timezone

from student_registration.backends import photo_batches as batches
from student_registration.backends.models import ExportHistory
from student_registration.backends.tests.test_child_photo_export import read_rows

REAL_SCHEDULE_BATCH = batches.schedule_batch


@pytest.fixture(params=['makani', 'dirasa'])
def world(request, django_user_model, monkeypatch, tmp_path):
    from student_registration.child.models import Child
    from student_registration.clm.models import Bridging
    from student_registration.mscc.models import Registration, Round
    from student_registration.schools.models import CLMRound, PartnerOrganization
    from student_registration.students.models import Student

    programme = request.param
    partner = PartnerOrganization.objects.create(name='Batch partner')
    other_partner = PartnerOrganization.objects.create(name='Other partner')
    user = django_user_model.objects.create_user(username='batch-owner', partner=partner)
    stranger = django_user_model.objects.create_user(username='another-user', partner=partner)
    roles = ['MSCC', 'MSCC_PARTNER'] if programme == 'makani' else ['CLM_Bridging']
    groups = [Group.objects.get_or_create(name=name)[0] for name in roles]
    user.groups.add(*groups)
    stranger.groups.add(*groups)
    if programme == 'makani':
        model, person_model, relation, cycle_model = Registration, Child, 'child', Round
        route = 'mscc:all_ages_children_photo_export'
    else:
        model, person_model, relation, cycle_model = Bridging, Student, 'student', CLMRound
        route = 'clm:bridging_all_ages_children_photo_export'
    cycle = cycle_model.objects.create(name='Current', current_year=True)
    person = person_model.objects.create(first_name='Child', father_name='Father', last_name='Family',
                                         birthday_year='2010', birthday_month='1', birthday_day='1')

    def add(count=1, assigned_partner=partner):
        records = model.objects.bulk_create([
            model(**{relation: person}, partner=assigned_partner, round=cycle) for _ in range(count)])
        return [record.pk for record in records]

    storage = FileSystemStorage(location=tmp_path)
    monkeypatch.setattr(batches, 'ExportStorage', lambda: storage)
    queue = Mock()
    monkeypatch.setattr(batches, 'schedule_batch', queue)
    return SimpleNamespace(programme=programme, user=user, stranger=stranger, model=model,
                           partner=partner, other_partner=other_partner, route=route, person=person,
                           add=add, storage=storage, queue=queue)


def make_job(world):
    return batches.create_job(world.user, world.programme,
                              batches.scoped_registrations(world.user, world.programme), {})


def children(job):
    return list(ExportHistory.objects.filter(fields__kind=batches.BATCH_KIND,
                                             fields__job_id=job.pk).order_by('pk'))


@pytest.mark.django_db
def test_snapshot_partitions_200_and_queues_after_commit(world, django_capture_on_commit_callbacks):
    ids = world.add(201)
    world.add(1, assigned_partner=world.other_partner)
    with django_capture_on_commit_callbacks(execute=True):
        job = make_job(world)
        assert not world.queue.called
    parts = children(job)
    assert job.fields['total'] == 201
    assert [len(part.fields['ids']) for part in parts] == [200, 1]
    assert parts[0].fields['ids'] + parts[1].fields['ids'] == sorted(ids)
    assert world.queue.call_count == 2
    with django_capture_on_commit_callbacks(execute=True):
        assert make_job(world).pk == job.pk
    assert world.queue.call_count == 2
    world.add()
    assert sum(len(part.fields['ids']) for part in children(job)) == 201


@pytest.mark.django_db
def test_worker_progress_download_and_history(world, client):
    ids = world.add(2)
    job = make_job(world)
    batch = children(job)[0]
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    batch.refresh_from_db()
    job.refresh_from_db()
    assert batch.status == job.status == 'done'
    client.force_login(world.user)
    page = client.get(reverse('backends:photo_batch_progress', args=[job.pk]))
    assert page.status_code == 200
    assert b'1 of 1' in page.content
    response = client.get(batch.file_url)
    assert response.status_code == 200
    rows, _, _ = read_rows(b''.join(response.streaming_content))
    assert [int(row['U']) for row in rows[1:]] == ids
    assert response['Cache-Control'] == 'private, no-store'
    history = client.get(reverse('backends:export_history_list')).json()['exports']
    assert [item['id'] for item in history] == [job.pk]
    assert history[0]['url'] == job.file_url
    client.force_login(world.stranger)
    assert client.get(batch.file_url).status_code == 404
    assert client.get(job.file_url).status_code == 404
    assert client.post(reverse('backends:photo_batch_retry', args=[batch.pk])).status_code == 404


@pytest.mark.django_db
def test_failed_batch_retries_individually_and_rejects_old_attempt(world, client, monkeypatch,
                                                                  django_capture_on_commit_callbacks):
    world.add()
    job = make_job(world)
    batch = children(job)[0]
    original = batches.build_photo_roster
    monkeypatch.setattr(batches, 'build_photo_roster', Mock(side_effect=OSError('Storage unavailable')))
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    batch.refresh_from_db()
    assert batch.status == 'failed'
    monkeypatch.setattr(batches, 'build_photo_roster', original)
    client.force_login(world.user)
    retry_url = reverse('backends:photo_batch_retry', args=[batch.pk])
    assert client.get(retry_url).status_code == 405
    with django_capture_on_commit_callbacks(execute=True):
        assert client.post(retry_url).status_code == 302
    retried = ExportHistory.objects.get(pk=batch.pk)
    job.refresh_from_db()
    assert job.status == 'pending'
    assert retried.fields['attempt'] != batch.fields['attempt']
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    retried.refresh_from_db()
    assert retried.fields['state'] == 'queued'
    batches.generate_batch(batch.pk, retried.fields['attempt'])
    retried.refresh_from_db()
    assert retried.status == 'done'
    world.queue.reset_mock()
    with django_capture_on_commit_callbacks(execute=True):
        client.post(retry_url)
    assert not world.queue.called


@pytest.mark.django_db
def test_permissions_rechecked_before_worker_and_download(world, client):
    ids = world.add()
    job = make_job(world)
    batch = children(job)[0]
    world.model.objects.filter(pk__in=ids).update(partner=world.other_partner)
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    batch.refresh_from_db()
    assert batch.status == 'failed'
    job.refresh_from_db()
    assert job.status == 'failed'
    world.model.objects.filter(pk__in=ids).update(partner=world.partner)
    batch.fields.update(state='queued')
    batch.status = 'pending'
    batch.save()
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    batch.refresh_from_db()
    assert batch.status == 'done'
    world.model.objects.filter(pk__in=ids).update(partner=world.other_partner)
    client.force_login(world.user)
    assert client.get(batch.file_url).status_code == 403


@pytest.mark.django_db
def test_stale_pending_can_retry_but_active_work_cannot(world, client, django_capture_on_commit_callbacks):
    world.add()
    job = make_job(world)
    batch = children(job)[0]
    client.force_login(world.user)
    url = reverse('backends:photo_batch_retry', args=[batch.pk])
    with django_capture_on_commit_callbacks(execute=True):
        client.post(url)
    assert not world.queue.called
    ExportHistory.objects.filter(pk=batch.pk).update(modified=timezone.now() - datetime.timedelta(hours=1))
    page = client.get(job.file_url)
    assert b'Interrupted' in page.content
    with django_capture_on_commit_callbacks(execute=True):
        client.post(url)
    assert world.queue.call_count == 1


@pytest.mark.django_db
def test_empty_job_and_start_confirmation_and_csrf(world, client):
    client.force_login(world.user)
    start = reverse(world.route)
    assert client.get(start).status_code == 200
    assert not ExportHistory.objects.exists()
    assert client.post(start).status_code == 302
    job = ExportHistory.objects.get(fields__kind=batches.JOB_KIND)
    assert job.status == 'done'
    assert children(job) == []
    assert b'No registrations match' in client.get(job.file_url).content
    from django.test import Client
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(world.user)
    assert csrf_client.post(start).status_code == 403


@pytest.mark.django_db
def test_download_failure_allows_regeneration_and_legacy_alias_is_blocked(world, client):
    from django.http import Http404
    from student_registration.backends.utils import download_file
    world.add()
    job = make_job(world)
    batch = children(job)[0]
    batches.generate_batch(batch.pk, batch.fields['attempt'])
    batch.refresh_from_db()
    filename = batch.fields['filename']
    for alias in [filename, './' + filename, 'nested/../' + filename,
                  'nested\\..\\' + filename, filename + '/.']:
        with pytest.raises(Http404):
            download_file(alias, 'batch.xlsx')
    world.storage.delete(batch.fields['filename'])
    client.force_login(world.user)
    assert client.get(batch.file_url).status_code == 302
    batch.refresh_from_db()
    assert batch.status == 'failed'


@pytest.mark.django_db(transaction=True)
def test_real_background_pool_returns_before_photos_finish(world, client, monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from student_registration.mscc import tasks

    world.add(201)
    started, release = threading.Event(), threading.Event()
    pool = ThreadPoolExecutor(max_workers=2)
    original = batches.build_photo_roster

    def wait_for_photos(*args, **kwargs):
        started.set()
        assert release.wait(timeout=10)
        return original(*args, **kwargs)

    monkeypatch.setattr(batches, 'schedule_batch', REAL_SCHEDULE_BATCH)
    monkeypatch.setattr(tasks, '_get_executor', lambda: pool)
    monkeypatch.setattr(batches, 'build_photo_roster', wait_for_photos)
    client.force_login(world.user)
    try:
        response = client.post(reverse(world.route))
        assert response.status_code == 302
        assert started.wait(timeout=5)
        job = ExportHistory.objects.get(fields__kind=batches.JOB_KIND)
        assert all(batch.status == 'pending' for batch in children(job))
        assert b'0 of 2' in client.get(response['Location']).content
    finally:
        release.set()
        pool.shutdown(wait=True)
    job.refresh_from_db()
    assert job.status == 'done'
    parts = children(job)
    assert [part.status for part in parts] == ['done', 'done']
    for part, expected_rows in zip(parts, [200, 1]):
        with world.storage.open(part.fields['filename'], 'rb') as source:
            rows, _, _ = read_rows(source.read())
        assert len(rows) == expected_rows + 1
