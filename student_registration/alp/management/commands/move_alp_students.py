__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.alp.tasks import move_student_to_school


class Command(BaseCommand):
    help = 'Move students from school to another school'

    def add_arguments(self, parser):
        parser.add_argument('--school_from', type=int)
        parser.add_argument('--school_to', type=int)

    def handle(self, *args, **options):
        move_student_to_school(options['school_from'], options['school_to'])
