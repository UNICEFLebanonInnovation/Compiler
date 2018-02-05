from datetime import datetime

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import calculate_attendances_by_student


class Command(BaseCommand):
    help = 'Calculate absentees'
    #
    # def add_arguments(self, parser):
    #     parser.add_argument('from_date', type=lambda d: datetime.strptime(d, '%Y%m%d'))
    #     parser.add_argument('to_date', type=lambda d: datetime.strptime(d, '%Y%m%d'))

    def handle(self, *args, **options):
        calculate_attendances_by_student()
