__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.outreach.tasks import update_student_grade


class Command(BaseCommand):
    help = 'update_student_grade'

    def handle(self, *args, **options):
        update_student_grade()
