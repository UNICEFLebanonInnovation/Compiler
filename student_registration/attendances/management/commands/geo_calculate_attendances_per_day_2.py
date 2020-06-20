from datetime import datetime

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import geo_calculate_attendances_per_day_2


class Command(BaseCommand):
    help = 'geo_calculate_attendances_per_day_2'

    def add_arguments(self, parser):
        parser.add_argument('--from_date', type=lambda d: datetime.strptime(d, '%Y-%m-%d'))
        parser.add_argument('--to_date', type=lambda d: datetime.strptime(d, '%Y-%m-%d'))

    def handle(self, *args, **options):
        geo_calculate_attendances_per_day_2(options['from_date'], options['to_date'])
