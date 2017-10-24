__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.winterization.tasks import *


class Command(BaseCommand):
    help = 'Cleanup winter old data'

    def handle(self, *args, **options):
        cleanup_old_data()
