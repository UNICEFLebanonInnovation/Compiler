__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.clm.tasks import push_bln_data


class Command(BaseCommand):
    help = 'Push BLN data'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        push_bln_data(
            file_name=options['file'],
            base_url=options['url'],
            token=options['token'],
            protocol=options['protocol']
        )
