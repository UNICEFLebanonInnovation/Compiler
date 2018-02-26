__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import split_attendance


class Command(BaseCommand):
    help = 'Split ALP attendances data'

    def add_arguments(self, parser):
        parser.add_argument('--school_type', type=str)

    def handle(self, *args, **options):
        school_type = options['school_type']
        split_attendance(school_type)

