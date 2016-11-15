__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Generate unique number'

    def handle(self, *args, **options):
        # generate_adult_unique_number()
        # generate_child_unique_number()
        generate_hashing_unique_number()
