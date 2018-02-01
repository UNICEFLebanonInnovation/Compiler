__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import *


class Command(BaseCommand):
    help = 'Push attendance data to CouchBase'

    def add_arguments(self, parser):
        parser.add_argument('--schools', nargs='+', type=str)
        parser.add_argument('--school_type', type=str, default=None)

    def handle(self, *args, **options):
        pass
        # school_type = options['school_type']
        #
        # if options['schools']:
        #     for school in options['schools']:
        #         set_app_attendances(
        #             school_number=school,
        #             school_type=school_type)
        # else:
        #     set_app_attendances(school_type=school_type)

