__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import fix_round_assignment


class Command(BaseCommand):
    help = 'Fix ALP round assignment'

    def add_arguments(self, parser):
        parser.add_argument('update', nargs='+', type=int)

    def handle(self, *args, **options):
        if options['update']:
            for update in options['update']:
                fix_round_assignment(update)
