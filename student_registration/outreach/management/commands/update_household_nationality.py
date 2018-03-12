__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import update_household_nationality


class Command(BaseCommand):
    help = 'update_household_nationality'

    def handle(self, *args, **options):
        update_household_nationality()
