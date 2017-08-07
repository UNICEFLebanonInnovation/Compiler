__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Find Students matching between Generic and Enrollment'

    def handle(self, *args, **options):
        matching_generic_2ndshift_enrollments()
