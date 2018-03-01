__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.enrollments.tasks import migrate_gradings


class Command(BaseCommand):
    help = 'Migrate enrollment gradings to the new structure'

    def handle(self, *args, **options):
        migrate_gradings()
