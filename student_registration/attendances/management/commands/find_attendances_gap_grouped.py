__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import find_attendances_gap_grouped


class Command(BaseCommand):
    help = 'Find attendance GAP Grouped by school'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int)

    def handle(self, *args, **options):
        find_attendances_gap_grouped(options['days'])
