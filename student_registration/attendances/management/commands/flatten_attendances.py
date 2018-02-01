from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import *


class Command(BaseCommand):
    help = 'Flatten attendance data from CouchBase'

    def handle(self, *args, **options):
        pass
        # flatten_attendance()
