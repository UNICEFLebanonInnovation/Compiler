__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.enrollments.tasks import assign_section


class Command(BaseCommand):
    help = 'Assign section to null registrations'

    def add_arguments(self, parser):
        parser.add_argument('section', nargs='+', type=int)

    def handle(self, *args, **options):
        if options['section']:
            for section in options['section']:
                assign_section(section)
