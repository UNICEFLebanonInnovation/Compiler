__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import auto_refer_to_alp_level


class Command(BaseCommand):
    help = 'Refer ALP level to students'

    def handle(self, *args, **options):
        auto_refer_to_alp_level()
