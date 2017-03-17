__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.enrollments.tasks import *


class Command(BaseCommand):
    help = 'Track enrolled students moves'

    def handle(self, *args, **options):
        track_student_moves()
