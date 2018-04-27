__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'export_2ndshift_gradings'

    def handle(self, *args, **options):
        from student_registration.backends.tasks import export_2ndshift_gradings
        data = export_2ndshift_gradings({'term':1}, return_data=True)
        file_object = open("enrolment_grading_data.xlsx", "w")
        file_object.write(data)
        file_object.close()
