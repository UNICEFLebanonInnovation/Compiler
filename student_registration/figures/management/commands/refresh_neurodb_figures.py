"""``manage.py refresh_neurodb_figures [--programme mscc|bridging|youth] [--year 2025-2026|all]``: count now."""

from django.core.management.base import BaseCommand, CommandError

from student_registration.figures import snapshots


class Command(BaseCommand):
    help = 'Count the NeuroDB beneficiary figures now and store them (run it off-peak).'

    def add_arguments(self, parser):
        parser.add_argument('--programme', choices=sorted(snapshots.all_programmes()),
                            help='one programme (default: every programme, youth included)')
        parser.add_argument('--year', help="the round or year's name (default: the current one); "
                                           "youth also takes 'all' (every year)")

    def handle(self, *args, **options):
        names = [options['programme']] if options['programme'] else list(snapshots.all_programmes())
        for name in names:
            snapshot = snapshots.refresh(name, options['year'])
            if snapshot is None:
                raise CommandError('%s: no such year' % name)
            self.stdout.write('%s %s: %ss' % (name, snapshot.year, snapshot.seconds))
