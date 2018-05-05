__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.backends.tasks import import_attendance_by_student


class Command(BaseCommand):
    help = 'import_attendance_by_student'

    def handle(self, *args, **options):
        import_attendance_by_student()
