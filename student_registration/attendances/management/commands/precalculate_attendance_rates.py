from django.core.management.base import BaseCommand

from student_registration.attendances.models import Absentee


class Command(BaseCommand):
    help = "Pre-calculate attendance rates per student to avoid expensive on-demand computation."

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of absentee records to update in a single batch.',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        buffer = []
        updated = 0

        queryset = Absentee.objects.all().iterator(chunk_size=batch_size)
        for absentee in queryset:
            attended = absentee.total_attended_days or 0
            absences = absentee.total_absent_days or 0
            total_days = attended + absences

            rate = None
            if total_days:
                rate = float(attended) / float(total_days)

            if absentee.attendance_rate != rate:
                absentee.attendance_rate = rate
                buffer.append(absentee)

            if len(buffer) >= batch_size:
                Absentee.objects.bulk_update(buffer, ['attendance_rate'])
                updated += len(buffer)
                buffer = []

        if buffer:
            Absentee.objects.bulk_update(buffer, ['attendance_rate'])
            updated += len(buffer)

        self.stdout.write(self.style.SUCCESS(f"Updated attendance rates for {updated} students."))
