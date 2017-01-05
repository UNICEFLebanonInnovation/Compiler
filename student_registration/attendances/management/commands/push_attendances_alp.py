__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import *


class Command(BaseCommand):
    help = 'Push attendance ALP data to CouchBase'

    def add_arguments(self, parser):
        parser.add_argument('schools', nargs='+', type=str)

    def handle(self, *args, **options):

        if 'all' in options['schools']:
            set_app_attendances_alp()
        else:
            for school in options['schools']:
                set_app_attendances_alp(school)
