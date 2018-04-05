__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        from student_registration.backends.tasks import export_attendance
        data = export_attendance({'from_date': '2018-03-01', 'to_date': '2018-03-31'}, return_data=True)
        file_object = open("export_attendance.xlsx", "w")
        file_object.write(data)
        file_object.close()
