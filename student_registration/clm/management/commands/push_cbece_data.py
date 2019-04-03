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
            base_url='127.0.0.1:8000',
            token='Token d170839fdc49d8bfd32d359bfe25da018ed45bab',
            protocol='HTTP'
            # file_name=options['file'],
            # base_url=options['url'],
            # token=options['token'],
            # protocol=options['protocol']
        )
