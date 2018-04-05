__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        from student_registration.backends.tasks import export_attendance_by_student
        data = export_attendance_by_student({}, return_data=True)
        file_object = open("attendance_by_student.xlsx", "w")
        file_object.write(data)
        file_object.close()
