__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        from student_registration.backends.tasks import export_2ndshift
        data = export_2ndshift({}, return_data=True)
        file_object = open("enrolment_data.xlsx", "w")
        file_object.write(data)
        file_object.close()
