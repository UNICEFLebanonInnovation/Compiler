__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.attendances.tasks import reset_absentees


class Command(BaseCommand):
    help = 'reset_absentees'

    def handle(self, *args, **options):
        reset_absentees()
