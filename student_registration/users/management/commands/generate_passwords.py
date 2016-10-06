__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import *


class Command(BaseCommand):
    help = 'Generate Users password'

    def handle(self, *args, **options):
        generate_passwords()
