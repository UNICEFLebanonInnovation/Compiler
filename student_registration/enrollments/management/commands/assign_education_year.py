__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.enrollments.tasks import assign_education_year


class Command(BaseCommand):
    help = 'Assign Education year to 2nd-shift'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)

    def handle(self, *args, **options):
        if options['year']:
            for year in options['year']:
                assign_education_year(year)
