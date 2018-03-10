__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import cross_matching_children, cross_matching_children_2


class Command(BaseCommand):
    help = 'cross_matching_children'

    def handle(self, *args, **options):
        cross_matching_children_2()
