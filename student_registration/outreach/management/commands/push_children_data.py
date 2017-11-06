__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import push_children_data


class Command(BaseCommand):
    help = 'Read outreach file and push children data'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, default=None)
        parser.add_argument('--token', type=str, default=None)
        parser.add_argument('--protocol', type=str, default='HTTPS')

    def handle(self, *args, **options):
        push_children_data(
            base_url=options['url'],
            token=options['token'],
            protocol=options['protocol']
        )
