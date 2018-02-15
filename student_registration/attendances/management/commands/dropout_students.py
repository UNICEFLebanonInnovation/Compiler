__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import *


class Command(BaseCommand):
    help = 'Disable/Dropout absent students'

    def handle(self, *args, **options):
        dropout_students(from_date=None, to_date=None)
