# -*- coding: utf-8 -*-
"""Queue existing MSCC records for replication to BMA-NFE.

Run once when the integration is switched on, and again whenever BMA-NFE has
to be rebuilt. Ordinary day-to-day changes need nothing: they are captured as
they are saved.
"""

from __future__ import unicode_literals, absolute_import, division

from django.core.management.base import BaseCommand, CommandError

from student_registration.datasync.constants import RESOURCE_ORDER
from student_registration.datasync.dispatch import flush_outbox
from student_registration.datasync.outbox import enqueue, sync_enabled
from student_registration.datasync.serializers import MODEL_FOR_RESOURCE


class Command(BaseCommand):
    help = (
        'Queue existing MSCC records for replication to BMA-NFE. '
        'Records are queued in dependency order (rounds and centres first), '
        'so a fresh BMA-NFE database can be built from an empty state.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--resource',
            action='append',
            dest='resources',
            choices=RESOURCE_ORDER,
            help=(
                'Limit the backfill to this resource. Repeat to name several; '
                'the default is every resource, in dependency order.'
            ),
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Queue at most this many records per resource (0 = no limit).',
        )
        parser.add_argument(
            '--no-send',
            action='store_true',
            help='Only fill the outbox; leave delivery to the periodic sweep.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would be queued without writing anything.',
        )

    def handle(self, *args, **options):
        """Queue the requested records and, unless told not to, send them."""
        if not sync_enabled() and not options['dry_run']:
            raise CommandError(
                'DATASYNC_ENABLED is off, so nothing would be queued. '
                'Switch it on, or re-run with --dry-run.'
            )

        resources = options['resources'] or RESOURCE_ORDER
        limit = options['limit']
        total = 0

        for resource in RESOURCE_ORDER:
            if resource not in resources:
                continue
            model = MODEL_FOR_RESOURCE[resource]
            queryset = model.objects.all().order_by('pk')
            if limit:
                queryset = queryset[:limit]

            ids = list(queryset.values_list('pk', flat=True))
            self.stdout.write('{}: {} record(s)'.format(resource, len(ids)))
            total += len(ids)

            if options['dry_run']:
                continue
            for record_id in ids:
                enqueue(resource, record_id, deliver=False)

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(
                'Dry run: {} record(s) would have been queued.'.format(total)
            ))
            return

        self.stdout.write(self.style.SUCCESS('Queued {} record(s).'.format(total)))

        if options['no_send']:
            self.stdout.write('Delivery left to the periodic sweep.')
            return

        totals = flush_outbox()
        self.stdout.write(self.style.SUCCESS(
            'Delivered {} event(s) in {} batch(es); {} deferred, {} abandoned.'.format(
                totals['sent'], totals['batches'], totals['failed'], totals['abandoned'],
            )
        ))
        if totals['failed'] or totals['abandoned']:
            self.stdout.write(self.style.WARNING(
                'Check the Sync events admin for the events that did not go through.'
            ))
