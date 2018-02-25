__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import assign_alp_level


class Command(BaseCommand):
    help = 'Assign ALP level to students'

    def handle(self, *args, **options):
        assign_alp_level()
