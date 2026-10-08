# -*- coding: utf-8 -*-
"""Report the health of the replication channel.

Answers the two questions an operator actually asks: can we reach BMA-NFE,
and is anything stuck in the outbox?
"""

from __future__ import unicode_literals, absolute_import, division

from django.core.management.base import BaseCommand
from django.db.models import Count

from student_registration.datasync.client import (
    SyncClient,
    SyncConfigurationError,
    SyncTransportError,
)
from student_registration.datasync.models import (
    STATUS_ABANDONED,
    STATUS_FAILED,
    STATUS_PENDING,
    SyncEvent,
)
from student_registration.datasync.outbox import sync_enabled


class Command(BaseCommand):
    help = 'Show the state of the outbox and check connectivity to BMA-NFE.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-ping',
            action='store_true',
            help='Skip the connectivity check and only report the outbox.',
        )

    def handle(self, *args, **options):
        """Print the outbox breakdown and, unless skipped, ping BMA-NFE."""
        self.stdout.write(
            'Outbound replication: {}'.format('on' if sync_enabled() else 'OFF')
        )

        counts = dict(
            SyncEvent.objects.values_list('status')
            .annotate(total=Count('id'))
            .values_list('status', 'total')
        )
        for status in (STATUS_PENDING, STATUS_FAILED, STATUS_ABANDONED, 'sent'):
            self.stdout.write('  {:<10} {}'.format(status, counts.get(status, 0)))

        stuck = SyncEvent.objects.filter(status=STATUS_ABANDONED).count()
        if stuck:
            self.stdout.write(self.style.WARNING(
                '  {} event(s) abandoned -- review them in the Sync events admin '
                'and use the "Send selected events again" action once fixed.'.format(stuck)
            ))

        if options['no_ping']:
            return

        client = SyncClient()
        self.stdout.write('Target: {}'.format(client.url or '(not configured)'))
        try:
            info = client.ping()
        except SyncConfigurationError as error:
            self.stdout.write(self.style.ERROR('Not configured: {}'.format(error)))
            return
        except SyncTransportError as error:
            self.stdout.write(self.style.ERROR('Unreachable: {}'.format(error)))
            return

        self.stdout.write(self.style.SUCCESS(
            'Reachable. Contract {}, ingest {}, max batch {}.'.format(
                info.get('contract_version'),
                'enabled' if info.get('enabled') else 'DISABLED',
                info.get('max_batch_size'),
            )
        ))
