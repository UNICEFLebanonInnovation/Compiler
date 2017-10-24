from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import calculate_attendances_by_student


class Command(BaseCommand):
    help = 'Calculate attendances by student'

    def handle(self, *args, **options):
        calculate_attendances_by_student()
