__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Find Students matching between Enrollment and Registrations'

    def handle(self, *args, **options):
        pass
