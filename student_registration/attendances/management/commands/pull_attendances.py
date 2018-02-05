__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import *


class Command(BaseCommand):
    help = 'Pull attendance data from CouchBase'

    def handle(self, *args, **options):
        pass
        # import_docs()
        # flatten_attendance()
