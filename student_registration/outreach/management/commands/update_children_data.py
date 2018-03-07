__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import update_children_data


class Command(BaseCommand):
    help = 'update_children_data'

    def handle(self, *args, **options):
        update_children_data()
