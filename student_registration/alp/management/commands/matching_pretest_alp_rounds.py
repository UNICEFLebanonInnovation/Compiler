__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import *


class Command(BaseCommand):
    help = 'matching pretest 2ndshift alp rounds'

    def handle(self, *args, **options):
        matching_pretest_alp_rounds()
