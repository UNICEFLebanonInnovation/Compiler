from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import (
    aggregate_attendace,
    calculate_by_day_summary
)


class Command(BaseCommand):
    help = 'Calculate attendance'

    def handle(self, *args, **options):
        aggregate_attendace()
        calculate_by_day_summary()
