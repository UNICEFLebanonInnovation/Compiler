__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        from student_registration.enrollments.tasks import export_student_program_moves
        data = export_student_program_moves()
        file_object = open("export_student_program_moves.xlsx", "w")
        file_object.write(data)
        file_object.close()
