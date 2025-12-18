from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q

from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.mscc.models import Registration


class Command(BaseCommand):
    help = "Pre-calculate attendance rates per MSCC registration to avoid expensive on-demand queries."

    def handle(self, *args, **options):
        stats = (
            MSCCAttendanceChild.objects
            .exclude(registration_id__isnull=True)
            .values('registration_id')
            .annotate(
                attended_days=Count('id', filter=Q(attended='yes')),
                total_days=Count('id'),
            )
        )

        updates = defaultdict(list)
        for entry in stats.iterator():
            total_days = entry['total_days'] or 0
            if not total_days:
                continue

            attendance_rate = round(entry['attended_days'] / float(total_days), 4)
            total_attendance = entry['attended_days']
            total_absence = total_days - total_attendance
            updates[(attendance_rate, total_attendance, total_absence)].append(entry['registration_id'])

        updated = 0
        with transaction.atomic():
            for values, registration_ids in updates.items():
                attendance_rate, total_attendance, total_absence = values
                affected = Registration.objects.filter(id__in=registration_ids)
                affected = affected.exclude(
                    attendance_rate=attendance_rate,
                    total_attendance=total_attendance,
                    total_absence=total_absence,
                )
                count = affected.update(
                    attendance_rate=attendance_rate,
                    total_attendance=total_attendance,
                    total_absence=total_absence,
                )
                updated += count

        self.stdout.write(self.style.SUCCESS(f"Updated attendance rates for {updated} registration rows."))
