__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import read_file


class Command(BaseCommand):
    help = 'Read outreach file'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        read_file(
            base_url=options['url'],
            token=options['token'],
            protocol=options['protocol']
        )
