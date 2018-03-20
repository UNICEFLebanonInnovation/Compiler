__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import create_children_data


class Command(BaseCommand):
    help = 'create_children_data'

    def handle(self, *args, **options):
        create_children_data()
