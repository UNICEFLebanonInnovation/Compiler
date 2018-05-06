__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.backends.tasks import import_grading_data


class Command(BaseCommand):
    help = 'import_grading_data'

    def handle(self, *args, **options):
        import_grading_data()
