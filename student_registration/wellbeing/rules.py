"""The flag rules: which children may need a follow-up, as of a date.

Each rule reads only what the centres already record and returns ``Hit``s: the registration, the
kind of flag, the reason in words, the evidence and ``as_of`` (the date of the latest data behind
it, used to tell a new problem from one already followed up). Rules take ``today`` so the same code
can replay a past round (``wellbeing_backtest``).

Attendance: day-offs are left out, and so are "all present" sheets of a class (at least
``all_present_min_children`` children, every one present): the form pre-fills "present", so such a
sheet may never have been filled in, and it counts neither way.
"""

import datetime
from collections import defaultdict
from dataclasses import dataclass, field

from django.db.models import Count, Q

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc import models as m

from .models import Flag

MALNUTRITION = (
    'MAM (MUAC >11.5 and <12.5 cm)',
    'SAM (MUAC <11.5 cm)',
    'SAM with Bilateral pitting oedema  (both feet puffy)',
)
SEVERE_MALNUTRITION = MALNUTRITION[1:]
URGENT_CONCERNS = ('Suicidal ideation',)
CP_FOLLOW_UP = ('Child referred to CP', 'Child referred to specialized services')
WITHOUT_PARENTS = ('Unaccompanied', 'Separated', 'Child headed household')
TARL_LEVELS = {
    'arabic_level_reached': ('Beginner', 'Letter', 'Word', 'Paragraph', 'Story', 'Comprehension'),
    'french_level_reached': ('Beginner', 'Letter', 'Word', 'Paragraph', 'Story', 'Comprehension'),
    'math_level_reached': ('Beginner', '1-digit', '2-digits', 'Subtraction', 'Division'),
}
SUBJECT_NAMES = {'arabic': 'Arabic', 'french': 'French', 'math': 'Math', 'english': 'English',
                 'science': 'Science', 'language': 'Language'}


@dataclass
class Hit:
    registration_id: int
    kind: str
    reason: str
    as_of: datetime.date
    evidence: dict = field(default_factory=dict)
    urgent: bool = False


# --------------------------------------------------------------------------------- helpers
def value(raw):
    """A value of a test saved from a form: lists (raw POST) give their last item; blanks are None."""
    if isinstance(raw, (list, tuple)):
        raw = raw[-1] if raw else None
    if raw is None:
        return None
    raw = str(raw).strip()
    return raw or None


def number(raw):
    raw = value(raw)
    try:
        return float(raw) if raw is not None else None
    except ValueError:
        return None


def latest_by_registration(queryset):
    """The latest row (highest id) of a service per registration: services are not unique."""
    latest = {}
    for row in queryset.order_by('registration_id', 'id'):
        latest[row.registration_id] = row
    return latest


def dropped_out(registration_ids, today):
    """Registrations recorded as having left the programme by ``today``: {id: (date, source)}."""
    out = {}
    for reg_id, when, created in m.Referral.objects.filter(
            registration_id__in=registration_ids, recommended_learning_path='Drop out').values_list(
            'registration_id', 'dropout_date', 'created'):
        day = when or created.date()
        if day <= today:
            out[reg_id] = (day, 'referral')
    for reg_id, when, created in m.FollowUpService.objects.filter(
            registration_id__in=registration_ids, follow_up_result='Dropout/No Interest').values_list(
            'registration_id', 'dropout_date', 'created'):
        day = when or created.date()
        if day <= today:
            out.setdefault(reg_id, (day, 'follow-up'))
    for reg_id, created in m.InclusionService.objects.filter(
            registration_id__in=registration_ids, dropout__iexact='yes').values_list('registration_id', 'created'):
        if created.date() <= today:
            out.setdefault(reg_id, (created.date(), 'inclusion'))
    for reg_id, when, created in m.YouthKitService.objects.filter(
            registration_id__in=registration_ids, adolescent_attendance='Dropout').values_list(
            'registration_id', 'adolescent_dropout_date', 'created'):
        day = when or created.date()
        if day <= today:
            out.setdefault(reg_id, (day, 'youth kit'))
    return out


def priority_registrations(registrations):
    """Context that makes a flag more pressing (never a flag on its own): the child works, lives
    without parents, or has a disability."""
    out = set()
    for reg in registrations:
        child = reg.child
        works = (reg.have_labour or '').startswith('Yes') or bool(reg.labour_condition)
        alone = child is not None and child.living_arrangement in WITHOUT_PARENTS
        disabled = (child is not None and child.disability_id is not None
                    and not (child.disability.name or '').strip().lower().startswith('no'))
        if works or alone or disabled:
            out.add(reg.id)
    return out


# ------------------------------------------------------------------------------- attendance
def attendance_days(registration_ids, center_id, start, today, settings):
    """{registration id: [(date, present, reason)]} over the period, one entry per class day (a
    child on two sheets the same day is present if present on either), plus the excluded sheets."""
    sheets = (MSCCAttendance.objects
              .filter(center_id=center_id, attendance_date__gte=start, attendance_date__lte=today)
              .exclude(day_off__iexact='yes')
              .annotate(listed=Count('attendance_child'),
                        present=Count('attendance_child', filter=Q(attendance_child__attended__iexact='yes'))))
    keep, blank = [], 0
    for sheet in sheets.values('id', 'listed', 'present'):
        if sheet['listed'] >= settings.all_present_min_children and sheet['present'] == sheet['listed']:
            blank += 1
        else:
            keep.append(sheet['id'])
    days = defaultdict(dict)
    rows = (MSCCAttendanceChild.objects
            .filter(attendance_day_id__in=keep, registration_id__in=registration_ids)
            .values_list('registration_id', 'attendance_day__attendance_date', 'attended', 'absence_reason'))
    for reg_id, day, attended, reason in rows.iterator():
        present = (attended or '').strip().lower() == 'yes'
        before = days[reg_id].get(day)
        days[reg_id][day] = (present or (before[0] if before else False), reason or (before[1] if before else ''))
    by_reg = {reg_id: sorted((d, p, r) for d, (p, r) in entries.items()) for reg_id, entries in days.items()}
    return by_reg, {'sheets': len(keep) + blank, 'sheets_all_present': blank}


def _rate(entries):
    return round(100.0 * sum(1 for _d, p, _r in entries if p) / len(entries), 1) if entries else None


def attendance_hits(by_reg, today, settings):
    hits = []
    window_start = today - datetime.timedelta(days=settings.attendance_window_days - 1)
    recent_start = today - datetime.timedelta(days=settings.drop_recent_days - 1)
    previous_start = recent_start - datetime.timedelta(days=settings.drop_previous_days)
    for reg_id, entries in by_reg.items():
        streak = []
        for day, present, reason in reversed(entries):
            if present:
                break
            streak.append((day, reason))
        if len(streak) >= settings.absence_streak:
            streak.reverse()
            hits.append(Hit(
                reg_id, Flag.ABSENCE_STREAK,
                'Absent {} class days in a row ({:%d %b} to {:%d %b})'.format(len(streak), streak[0][0], streak[-1][0]),
                streak[-1][0],
                {'absences': [[d.isoformat(), r] for d, r in streak]},
            ))
        window = [e for e in entries if e[0] >= window_start]
        rate = _rate(window)
        if len(window) >= settings.attendance_min_days and rate < settings.attendance_rate_below:
            last_absence = max(d for d, p, _r in window if not p)
            hits.append(Hit(
                reg_id, Flag.LOW_ATTENDANCE,
                'Attended {:g}% of {} class days in the last {} days'.format(
                    rate, len(window), settings.attendance_window_days),
                last_absence,
                {'rate': rate, 'class_days': len(window), 'since': window_start.isoformat()},
            ))
        recent = [e for e in entries if e[0] >= recent_start]
        previous = [e for e in entries if previous_start <= e[0] < recent_start]
        if len(recent) >= 4 and len(previous) >= 6:
            before, now = _rate(previous), _rate(recent)
            if before - now >= settings.drop_points:
                last_absence = max(d for d, p, _r in recent if not p)
                hits.append(Hit(
                    reg_id, Flag.ATTENDANCE_DROP,
                    'Attendance fell from {:g}% to {:g}% in the last {} days'.format(
                        before, now, settings.drop_recent_days),
                    last_absence,
                    {'before': before, 'recent': now},
                ))
    return hits


# --------------------------------------------------------------------------------- services
def entry_dates(registrations):
    """When each child joined the round: the education service's date, else the registration's."""
    dates = {reg.id: reg.registration_date for reg in registrations}
    for service in latest_by_registration(m.EducationService.objects.filter(
            registration_id__in=list(dates), registration_date__isnull=False)).values():
        dates[service.registration_id] = service.registration_date
    return dates


def service_hits(registrations, today, settings):
    core = [r for r in registrations if (r.type or '') == 'Core-Package']
    entered = entry_dates(core)
    missing = defaultdict(list)
    for service in m.ProvidedServices.objects.filter(
            registration_id__in=[r.id for r in core], required=True, completed=False):
        missing[service.registration_id].append(service.name)
    hits = []
    for reg in core:
        start = entered.get(reg.id)
        if start is None or reg.id not in missing:
            continue
        due = start + datetime.timedelta(weeks=settings.service_weeks)
        if due <= today:
            names = sorted(set(missing[reg.id]))
            hits.append(Hit(reg.id, Flag.SERVICE_GAP,
                            'Not received after {} weeks: {}'.format(settings.service_weeks, ', '.join(names)),
                            due, {'services': names, 'joined': start.isoformat()}))
    return hits


def dropout_hits(dropped):
    followed = set(m.FollowUpService.objects.filter(registration_id__in=list(dropped))
                   .values_list('registration_id', flat=True))
    return [Hit(reg_id, Flag.DROPOUT_NO_FOLLOWUP,
                'Recorded as dropped out on {:%d %b %Y} ({}); no follow-up recorded'.format(day, source),
                day, {'dropout_date': day.isoformat(), 'source': source})
            for reg_id, (day, source) in dropped.items() if reg_id not in followed and source != 'follow-up']


def health_hits(registration_ids, today):
    referrals = latest_by_registration(m.HealthNutritionReferral.objects.filter(registration_id__in=registration_ids))
    hits = []
    for reg_id, service in latest_by_registration(m.HealthNutritionService.objects.filter(
            registration_id__in=registration_ids)).items():
        referral = referrals.get(reg_id)
        screened = service.muac_malnutrition_screening or service.child_malnutrition_screening or ''
        if screened in MALNUTRITION and (referral is None or (referral.referred_malnutrition or '').lower() != 'yes'):
            hits.append(Hit(reg_id, Flag.MALNUTRITION_NO_REFERRAL,
                            'Screened {}; no referral to treatment recorded'.format(screened.split(' (')[0]),
                            service.created.date(), {'screening': screened}, urgent=screened in SEVERE_MALNUTRITION))
        delay = service.development_delays_identified or ''
        if delay and delay != 'No' and (
                referral is None or (referral.referred_development_delays or '').lower() != 'yes'):
            hits.append(Hit(reg_id, Flag.DELAY_NO_REFERRAL,
                            'Developmental delay identified ({}); no referral recorded'.format(delay),
                            service.created.date(), {'delay': delay}))
    return hits


def protection_hits(registration_ids, today):
    referred = set(m.Referral.objects.filter(registration_id__in=registration_ids, referred_service='CP')
                   .values_list('registration_id', flat=True))
    referred |= set(m.FollowUpService.objects.filter(registration_id__in=registration_ids,
                                                     follow_up_result__in=CP_FOLLOW_UP)
                    .values_list('registration_id', flat=True))
    hits = []
    for reg_id, service in latest_by_registration(m.PSSService.objects.filter(
            registration_id__in=registration_ids).exclude(child_protection_concern__isnull=True)
            .exclude(child_protection_concern='')).items():
        if reg_id in referred:
            continue
        concern = service.child_protection_concern
        # the PSS form keeps no date: the record id tells a new record from one already followed up
        hits.append(Hit(reg_id, Flag.PROTECTION_NO_REFERRAL,
                        'Protection concern recorded ({}); no CP referral recorded'.format(concern),
                        today, {'concern': concern, 'record': service.id}, urgent=concern in URGENT_CONCERNS))
    return hits


# --------------------------------------------------------------------------------- learning
def _tarl_gain(assessment):
    first = assessment.pre_test or {}
    last = assessment.post_test or assessment.mid_test or {}
    if not first or not last:
        return None
    compared, gained = [], []
    for key, levels in TARL_LEVELS.items():
        before, after = value(first.get(key)), value(last.get(key))
        if before in levels and after in levels:
            if levels.index(before) == len(levels) - 1:
                continue  # already at the top level: nothing to gain
            compared.append(key.split('_')[0])
            if levels.index(after) > levels.index(before):
                gained.append(key.split('_')[0])
    return compared, gained


def _scored_gain(assessment, config):
    pre, post = assessment.pre_test or {}, assessment.post_test or {}
    subjects = config.get(value(assessment.programme_type) or '', {})
    if not pre or not post or not subjects:
        return None
    compared, gained = [], []
    for key, spec in subjects.items():
        components = spec.get('components', ())

        def total(test):
            whole = number(test.get(key))
            if whole is not None:
                return whole
            parts = [number(test.get(c[0])) for c in components]
            parts = [p for p in parts if p is not None]
            return sum(parts) if parts else None
        before, after = total(pre), total(post)
        if before is not None and after is not None:
            compared.append(key.split('_')[0])
            if after > before:
                gained.append(key.split('_')[0])
    return compared, gained


def learning_hits(registration_ids, today):
    from student_registration.mscc.education_form import SUMMER_RS_PROGRAMME_CONFIG, WL_BLN_PROGRAMME_CONFIG

    hits, assessed = [], 0
    sources = (
        ('TaRL', m.TarlAssessment, _tarl_gain),
        ('BLN', m.EducationProgrammeWLAssessment, lambda a: _scored_gain(a, WL_BLN_PROGRAMME_CONFIG)),
        ('Summer RS', m.EducationProgrammeSummerRSAssessment, lambda a: _scored_gain(a, SUMMER_RS_PROGRAMME_CONFIG)),
    )
    for label, model, gain in sources:
        for reg_id, assessment in latest_by_registration(model.objects.filter(
                registration_id__in=registration_ids)).items():
            result = gain(assessment)
            if not result or not result[0]:
                continue
            assessed += 1
            compared, gained = result
            if not gained:
                names = ', '.join(SUBJECT_NAMES.get(s, s.title()) for s in compared)
                hits.append(Hit(reg_id, Flag.NO_LEARNING_GAIN,
                                '{} test: no progress in {} between the first and the latest test'.format(label, names),
                                assessment.modified.date(), {'test': label, 'subjects': compared}))
    return hits, assessed
