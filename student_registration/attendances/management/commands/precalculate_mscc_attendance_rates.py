from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q

from student_registration.attendances.models import MSCCAttendanceChild


class Command(BaseCommand):
    help = "Pre-calculate attendance rates per MSCC child to avoid expensive on-demand queries."

    def handle(self, *args, **options):
        stats = (
            MSCCAttendanceChild.objects
            .values('child_id')
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
            updates[attendance_rate].append(entry['child_id'])

        updated = 0
        with transaction.atomic():
            for rate, child_ids in updates.items():
                affected = MSCCAttendanceChild.objects.filter(child_id__in=child_ids)
                affected = affected.exclude(attendance_rate=rate)
                count = affected.update(attendance_rate=rate)
                updated += count

        self.stdout.write(self.style.SUCCESS(f"Updated attendance rates for {updated} attendance rows."))
