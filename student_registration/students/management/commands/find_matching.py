__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Find Students matching between Enrollment and Registrations'

    def handle(self, *args, **options):
<<<<<<< HEAD
        find_matching()
=======
        pass
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
