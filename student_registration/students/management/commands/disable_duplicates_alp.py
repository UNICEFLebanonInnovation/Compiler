__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Disable duplicate ALP'

    def handle(self, *args, **options):
        disable_duplicate_outreaches()
