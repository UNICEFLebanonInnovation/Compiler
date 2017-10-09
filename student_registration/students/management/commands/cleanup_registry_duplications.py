__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.students.tasks import *


class Command(BaseCommand):
    help = 'Cleanup 2ndshift/ALP duplications'

    def add_arguments(self, parser):
        parser.add_argument('--registry_type', type=str, default=None)

    def handle(self, *args, **options):
        registry_type = options['registry_type']
        cleanup_registry_duplications(registry_type=registry_type)
