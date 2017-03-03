__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.enrollments.tasks import *


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        generate_2ndshift_report()
