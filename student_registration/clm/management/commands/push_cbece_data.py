__author__ = 'ybeydoun'

from django.core.management.base import BaseCommand

from student_registration.clm.tasks import push_cbece_data

class Command(BaseCommand):
    help = 'Push CBECE data'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        push_cbece_data(
            file_name='test.XLSX',
            base_url='leb-container-test.azurewebsites.net',
            token='Token 145f569650265eebb2cd5f92eabab8f886a0a0c2',
            protocol='HTTPS'
            # file_name=options['file'],
            # base_url=options['url'],
            # token=options['token'],
            # protocol=options['protocol']
        )
