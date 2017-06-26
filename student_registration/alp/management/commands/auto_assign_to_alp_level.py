__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import *


class Command(BaseCommand):
    help = 'Assign ALP level to students'

    def handle(self, *args, **options):
        auto_assign_to_alp_level()
