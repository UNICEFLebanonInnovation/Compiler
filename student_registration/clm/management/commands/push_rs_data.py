__author__ = 'ybeydoun'

from django.core.management.base import BaseCommand

from student_registration.clm.tasks import push_rs_data


# class Command(BaseCommand):
#     help = 'Push RS data'
#
#     def add_arguments(self, parser):
#         parser.add_argument('--file', type=str, default=None)
#         parser.add_argument('--url', type=str, default=None)
#         parser.add_argument('--token', type=str, default=None)
#         parser.add_argument('--protocol', type=str, default='HTTPS')
#
#     def handle(self, *args, **options):
#         push_rs_data(
#             file_name='UNI12-RS-2018-compiled.XLSX',
#             base_url='mdb2.azurewebsites.net',
#             # base_url='127.0.0.1:8000',
#             token='Token 045efd8f70311ace357198eb44f300cfabd2dfc7',
#             protocol='HTTPS'
#             # file_name=options['file'],
#             # base_url=options['url'],
#             # token=options['token'],
#             # protocol=options['protocol']
#         )


class Command(BaseCommand):
    help = 'Push RS data'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        push_rs_data(
            file_name='test.XLSX',
            base_url='127.0.0.1:8000',
            token='Token d170839fdc49d8bfd32d359bfe25da018ed45bab',
            protocol='HTTPS'
            # file_name=options['file'],
            # base_url=options['url'],
            # token=options['token'],
            # protocol=options['protocol']
        )
