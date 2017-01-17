from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import calculate_attendance_and_absentees


class Command(BaseCommand):
    help = 'Calculate attendances and absentees'

    def handle(self, *args, **options):
        calculate_attendance_and_absentees()
