__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import *


class Command(BaseCommand):
    help = 'Assign groups to users'

    def handle(self, *args, **options):
        assign_groups_to_2nd_shift_schools()
        assign_groups_to_2nd_shift_directors()
