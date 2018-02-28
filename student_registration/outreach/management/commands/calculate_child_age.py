__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import calculate_child_age


class Command(BaseCommand):
    help = 'calculate_child_age'

    def handle(self, *args, **options):
        calculate_child_age()
