from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import (
    calculate_by_day_summary
)


class Command(BaseCommand):
    help = 'Calculate attendance'

    def handle(self, *args, **options):
        calculate_by_day_summary()
