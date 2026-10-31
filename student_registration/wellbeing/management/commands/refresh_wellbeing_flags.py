"""``refresh_wellbeing_flags [--center ID ...]``: work out the Makani wellbeing flags and centre
summaries now (what the nightly task does)."""

from django.core.management.base import BaseCommand

from student_registration.wellbeing import engine


class Command(BaseCommand):
    help = 'Work out the Makani wellbeing flags and centre summaries of the current round(s)'

    def add_arguments(self, parser):
        parser.add_argument('--center', type=int, action='append', help='only this centre (repeatable)')

    def handle(self, *args, **options):
        totals = engine.refresh(center_ids=options['center'])
        self.stdout.write(', '.join('{} {}'.format(v, k) for k, v in sorted(totals.items())) or 'nothing to do')
