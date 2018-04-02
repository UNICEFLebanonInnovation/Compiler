from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import calculate_last_attendance_date


class Command(BaseCommand):
    help = 'calculate_last_attendance_date'

    def handle(self, *args, **options):
        calculate_last_attendance_date()
