__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import *


class Command(BaseCommand):
    help = 'Generate ALP report'

    def add_arguments(self, parser):
        parser.add_argument('params', nargs='*', type=str)

    def handle(self, *args, **options):
        params = options['params']
        school = 0
        location = 0
        email = ''
        if 'school' in params:
            school = params[1]
        if 'location' in params:
            location = params[1]
        if 'email' in params:
            email = params[5]
