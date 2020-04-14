__author__ = 'ybeydoun'

from django.core.management.base import BaseCommand

from student_registration.locations.tasks import push_cadaster_data

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
#             token='Token 6fb8fee84c8c7ea03e68c16f51c41a3a5f996596',
#             protocol='HTTPS'
#         )


class Command(BaseCommand):
    help = 'Push Cadaster data'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default=None)
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        push_cadaster_data(
            file_name='test.XLSX',
            base_url='leb-container-test.azurewebsites.net',
            token='Token 740cd8a19fc6b8a4ae9089782fea989c30c79797',
            protocol='HTTPS'
        )

# class Command(BaseCommand):
#     help = 'Push Cadaster data'
#
#     def add_arguments(self, parser):
#         parser.add_argument('--file', type=str, default=None)
#         parser.add_argument('--url', type=str, default=None)
#         parser.add_argument('--token', type=str, default=None)
#         parser.add_argument('--protocol', type=str, default='HTTP')
#
#     def handle(self, *args, **options):
#         push_cadaster_data(
#             file_name='test.XLSX',
#             base_url='http://localhost:8000',
#             token='Token d170839fdc49d8bfd32d359bfe25da018ed45bab',
#             protocol='HTTP'
#         )
