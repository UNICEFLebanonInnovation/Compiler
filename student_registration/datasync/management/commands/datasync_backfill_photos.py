"""Inspect explicit photo links before queueing historical child photos."""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from ...photos import enqueue_child_photo, linked_student_id, photo_sync_enabled, PhotoSourceError


class Command(BaseCommand):
    help = 'Audit child photo links or requeue complete registrations with their photos'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--child-id', type=int)

    def handle(self, *args, **options):
        if not options['dry_run'] and not photo_sync_enabled():
            raise CommandError('Enable DATASYNC_ENABLED before enqueueing')
        from ...outbox import sync_enabled
        if not options['dry_run'] and not sync_enabled():
            raise CommandError('Enable DATASYNC_ENABLED before enqueueing')
        Registration = apps.get_model('mscc', 'Registration')
        Student = apps.get_model('students', 'Student')
        storage = Student._meta.get_field('std_image').storage
        self.stdout.write('Source photo backend: {}.{}'.format(
            storage.__class__.__module__, storage.__class__.__name__))
        rows = Registration.objects.exclude(child_id__isnull=True)
        if options.get('child_id') is not None:
            rows = rows.filter(child_id=options['child_id'])
        counts = {'ready': 0, 'missing_link': 0, 'missing_student': 0, 'no_photo': 0, 'ambiguous': 0}
        for child_id in rows.values_list('child_id', flat=True).distinct().iterator():
            try:
                student_id = linked_student_id(child_id)
            except PhotoSourceError:
                counts['ambiguous'] += 1
                continue
            if student_id is None:
                counts['missing_link'] += 1
                continue
            student = Student.objects.filter(pk=student_id).first()
            if student is None:
                counts['missing_student'] += 1
                continue
            if options.get('child_id') is not None:
                self.stdout.write('BMA child #{} -> Student #{}'.format(child_id, student_id))
            if not student.std_image:
                counts['no_photo'] += 1
                continue  # Bulk backfill never queues photo removals.
            counts['ready'] += 1
            if not options['dry_run']:
                enqueue_child_photo(child_id, deliver=False)
        self.stdout.write(str(counts))
        self.stdout.write('Dry run: no events queued' if options['dry_run'] else 'Queued; run the existing outbox flush worker')
