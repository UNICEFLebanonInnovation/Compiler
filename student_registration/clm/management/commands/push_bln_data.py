__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.clm.tasks import push_bln_data

# class Command(BaseCommand):
#     help = 'Push BLN data'
#
#     def add_arguments(self, parser):
#         parser.add_argument('--file', type=str, default=None)
#         parser.add_argument('--url', type=str, default=None)
#         parser.add_argument('--token', type=str, default=None)
#         parser.add_argument('--protocol', type=str, default='HTTPS')
#
#     def handle(self, *args, **options):
#         push_bln_data(
#             file_name='UNI12-RS-2018-compiled.XLSX',
#             base_url='mdb2.azurewebsites.net',
#             token='Token d2cdf9a40220d4965a0103e9512d76af00823baa',
#             protocol='HTTPS'
#         )

class Command(BaseCommand):
    help = 'Push BLN data'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTP')

    def handle(self, *args, **options):
        push_bln_data(
            file_name='test.XLSX',
            base_url='127.0.0.1:8282',
            token='Token d170839fdc49d8bfd32d359bfe25da018ed45bab',
            # base_url='leb-container-test.azurewebsites.net',
            # token='Token 145f569650265eebb2cd5f92eabab8f886a0a0c2',
            protocol='HTTP'
            # file_name=options['file'],
            # base_url=options['url'],
            # token=options['token'],
             # protocol=options['protocol'
        )
