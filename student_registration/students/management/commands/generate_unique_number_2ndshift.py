__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Generate unique number for 2ndshift'

    def add_arguments(self, parser):
        parser.add_argument('offset', nargs='+', type=int)

    def handle(self, *args, **options):
        for offset in options['offset']:
<<<<<<< HEAD
            print 'Generate hash number for 2nd shift students'
=======
            print('Generate hash number for 2nd shift students')
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            generate_2ndshift_unique_number(offset)
