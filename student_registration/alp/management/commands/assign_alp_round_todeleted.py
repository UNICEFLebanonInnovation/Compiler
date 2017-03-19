__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import *


class Command(BaseCommand):
    help = 'Assign ALP round to deleted'

    def add_arguments(self, parser):
        parser.add_argument('round', nargs='+', type=int)

    def handle(self, *args, **options):
        if options['round']:
            for round_id in options['round']:
                assign_round_to_deleted(round_id)
