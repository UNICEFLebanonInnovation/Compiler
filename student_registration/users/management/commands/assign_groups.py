__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import *


class Command(BaseCommand):
    help = 'Assign groups to users'

    def add_arguments(self, parser):
        parser.add_argument('groups', nargs='+', type=str)

    def handle(self, *args, **options):
        for group in options['groups']:
            assign_group(group)
