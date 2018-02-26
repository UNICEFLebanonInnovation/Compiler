__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import cleanup_duplications


class Command(BaseCommand):
    help = 'Cleanup students duplications'

    def handle(self, *args, **options):
        cleanup_duplications()
