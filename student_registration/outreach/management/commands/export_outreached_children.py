__author__ = 'achamseddine'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export 2nd shift registrations'

    def handle(self, *args, **options):
        from student_registration.outreach.tasks import export_outreached_children
        data = export_outreached_children({'current': True}, return_data=True)
        file_object = open("export_outreached_children.xlsx", "w")
        file_object.write(data)
        file_object.close()
