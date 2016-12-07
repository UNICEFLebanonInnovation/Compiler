__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.hhvisit.tasks import *


class Command(BaseCommand):
    help = 'Pull visit data from CouchBase'

    def handle(self, *args, **options):
        import_visits()



