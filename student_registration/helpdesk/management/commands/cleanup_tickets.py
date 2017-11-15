__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.helpdesk.tasks import cleanup_old_data


class Command(BaseCommand):
    help = 'Cleanup old tickets'

    def handle(self, *args, **options):
        cleanup_old_data()
