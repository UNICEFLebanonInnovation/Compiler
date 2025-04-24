__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import generate_2ndshift_unique_number, generate_alp_unique_number


class Command(BaseCommand):
    help = 'Generate unique number'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str)

    def handle(self, *args, **options):
        if '2ndshift' in options['models']:
            generate_2ndshift_unique_number()
        if 'alp' in options['models']:
            generate_alp_unique_number()
