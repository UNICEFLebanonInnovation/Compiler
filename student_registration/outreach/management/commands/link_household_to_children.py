__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import link_household_to_children


class Command(BaseCommand):
    help = 'Link Household to children'

    def handle(self, *args, **options):
        link_household_to_children()
