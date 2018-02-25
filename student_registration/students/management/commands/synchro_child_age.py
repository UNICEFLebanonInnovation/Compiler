__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Synchronize Child age with UNHCR'

    def handle(self, *args, **options):
        pass
