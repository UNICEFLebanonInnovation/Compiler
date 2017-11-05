__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

# from student_registration.outreach.tasks import read_file


class Command(BaseCommand):
    help = 'Read outreach file'

    def handle(self, *args, **options):
        from openpyxl import load_workbook

        wb = load_workbook(filename='outreach_data.xlsx', read_only=True)
        ws = wb['big_data']

        for row in ws.rows:
            for cell in row:
                print(cell.value)
