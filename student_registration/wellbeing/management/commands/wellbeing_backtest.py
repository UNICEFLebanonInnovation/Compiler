"""``wellbeing_backtest --round ID``: replay the attendance flags on a past Makani round and print
how many children who left were flagged beforehand (counts only). Read-only."""

import json

from django.core.management.base import BaseCommand, CommandError

from student_registration.mscc.models import Round
from student_registration.wellbeing import backtest


class Command(BaseCommand):
    help = 'Replay the attendance flags on a past round (read-only; counts only)'

    def add_arguments(self, parser):
        parser.add_argument('--round', type=int, required=True)
        parser.add_argument('--every', type=int, default=7, help='days between checkpoints')
        parser.add_argument('--silence-days', type=int, default=28,
                            help='no class day attended for this long at the end counts as having left')

    def handle(self, *args, **options):
        round_obj = Round.objects.filter(pk=options['round']).first()
        if round_obj is None:
            raise CommandError('No such round')
        result = backtest.run(round_obj, every=options['every'], silence_days=options['silence_days'])
        self.stdout.write(json.dumps(result, indent=2))
