"""Replaying the attendance flags on a past round, to see whether they would have warned in time.

At a checkpoint every ``every`` days, the attendance rules run on the data recorded up to that day;
a child's first flag date is kept. The outcome is leaving the programme: a recorded dropout, or
"stopped coming" (no class day attended in the last ``silence_days`` of the round's attendance).
Only counts come out: no names, no ids.
"""

import datetime
import statistics
from collections import Counter

from . import engine, rules
from .models import FlagSettings


def run(round_obj, every=7, silence_days=28, settings=None):
    settings = settings or FlagSettings.current()
    regs = list(engine.registrations([round_obj]))
    by_center = {}
    for reg in regs:
        by_center.setdefault(reg.center_id, []).append(reg)
    first_day = round_obj.start_date
    last_day = round_obj.end_date or datetime.date.today()
    first_flag, last_seen, kinds = {}, {}, Counter()
    recorded = rules.dropped_out([r.id for r in regs], last_day)
    for center_id, center_regs in by_center.items():
        ids = [r.id for r in center_regs]
        start = first_day or (last_day - datetime.timedelta(days=365))
        attendance, _sheets = rules.attendance_days(ids, center_id, start, last_day, settings)
        for reg_id, entries in attendance.items():
            present = [d for d, p, _r in entries if p]
            if present:
                last_seen[reg_id] = max(present)
        data_days = sorted({d for entries in attendance.values() for d, _p, _r in entries})
        if not data_days:
            continue
        checkpoint = data_days[0] + datetime.timedelta(days=settings.attendance_window_days)
        while checkpoint <= data_days[-1]:
            sliced = {}
            for reg_id, entries in attendance.items():
                if reg_id in first_flag:
                    continue
                gone = recorded.get(reg_id)
                if gone and gone[0] <= checkpoint:
                    continue
                window = [e for e in entries if e[0] <= checkpoint]
                if window:
                    sliced[reg_id] = window
            for hit in rules.attendance_hits(sliced, checkpoint, settings):
                if hit.registration_id not in first_flag:
                    first_flag[hit.registration_id] = checkpoint
                    kinds[hit.kind] += 1
            checkpoint += datetime.timedelta(days=every)
    end_of_data = max(last_seen.values(), default=last_day)
    left = {}
    for reg_id, (day, _source) in recorded.items():
        left[reg_id] = day
    for reg in regs:
        seen = last_seen.get(reg.id)
        if reg.id not in left and seen and (end_of_data - seen).days >= silence_days:
            left[reg.id] = seen
    warned = [reg_id for reg_id in left if reg_id in first_flag and first_flag[reg_id] <= left[reg_id]]
    leads = [(left[reg_id] - first_flag[reg_id]).days for reg_id in warned]
    flagged_stayed = [reg_id for reg_id in first_flag if reg_id not in left]
    return {
        'children': len(regs),
        'children_with_attendance': len(last_seen),
        'flagged': len(first_flag),
        'flagged_by_first_kind': dict(kinds),
        'left': len(left),
        'left_recorded_dropout': len(recorded),
        'left_stopped_coming': len(left) - len(recorded),
        'left_and_flagged_before': len(warned),
        'share_of_leavers_warned': round(100.0 * len(warned) / len(left), 1) if left else None,
        'share_of_flagged_who_left': round(100.0 * sum(1 for r in first_flag if r in left) / len(first_flag), 1)
        if first_flag else None,
        'flagged_and_stayed': len(flagged_stayed),
        'median_days_of_warning': statistics.median(leads) if leads else None,
    }
