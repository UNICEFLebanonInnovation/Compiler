__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import disable_duplicate_enrolments


class Command(BaseCommand):
    help = 'Disable duplicate enrolments by schools'

    def add_arguments(self, parser):
        parser.add_argument('schools', nargs='+', type=str)

    def handle(self, *args, **options):
        for school in options['schools']:
            disable_duplicate_enrolments(offset=None, school_number=school)
