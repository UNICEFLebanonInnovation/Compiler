"""Running the rules: the flags of every centre of the current round(s), kept in step with the data
(new problems open a flag, cleared ones resolve, followed-up ones stay closed unless something new
happens), and the monthly centre summaries.

Centres are processed one at a time, each in its own transaction, so memory stays small and a
failing centre does not stop the others.
"""

import datetime
import logging
import statistics
from collections import Counter, defaultdict

from django.db import transaction
from django.db.models import Q

from student_registration.mscc import models as m

from . import rules
from .models import CenterSummary, Flag, FlagSettings
from .models import today as local_today

logger = logging.getLogger(__name__)

HISTORY_DAYS = 120  # attendance read per run: enough for every window and a long absence streak
ATTENDANCE_KINDS = (Flag.ABSENCE_STREAK, Flag.LOW_ATTENDANCE, Flag.ATTENDANCE_DROP)


def registrations(rounds, center_id=None):
    qs = (m.Registration.objects
          .filter(deleted=False, round__in=rounds, center__isnull=False)
          .exclude(type='TLS')
          .select_related('child', 'child__disability'))
    return qs.filter(center_id=center_id) if center_id else qs


def evaluate(regs, center_id, today, settings=None):
    """The hits of one centre as of ``today``, and what the summary needs to know."""
    settings = settings or FlagSettings.current()
    ids = [r.id for r in regs]
    dropped = rules.dropped_out(ids, today)
    active = [r for r in regs if r.id not in dropped]
    active_ids = [r.id for r in active]
    start = today - datetime.timedelta(days=HISTORY_DAYS)
    by_reg, sheets = rules.attendance_days(active_ids, center_id, start, today, settings)
    hits = rules.attendance_hits(by_reg, today, settings)
    hits += rules.service_hits(active, today, settings)
    hits += rules.dropout_hits(dropped)
    hits += rules.health_hits(active_ids, today)
    hits += rules.protection_hits(active_ids, today)
    learning, assessed = rules.learning_hits(active_ids, today)
    hits += learning
    context = {'dropped': dropped, 'active': active, 'attendance': by_reg, 'sheets': sheets,
               'assessed': assessed, 'no_gain': len(learning)}
    return hits, context


def _reopens(previous, hit):
    """A followed-up flag comes back only with newer data, or a different record behind it."""
    if previous is None:
        return True
    if previous.status == Flag.FOLLOWED_UP:
        if hit.kind == Flag.PROTECTION_NO_REFERRAL:  # its record has no date: only a new record counts
            return previous.evidence.get('record') != hit.evidence.get('record')
        return hit.as_of > previous.followed_up_on
    return True  # resolved by itself, and back


def reconcile(regs, hits, today):
    """Open, update and resolve the flags of these registrations. Returns counts."""
    by_reg = {r.id: r for r in regs}
    priority = rules.priority_registrations(regs)
    open_flags = {(f.registration_id, f.kind): f
                  for f in Flag.objects.filter(registration_id__in=list(by_reg), status=Flag.OPEN)}
    last_closed = {}
    for flag in (Flag.objects.filter(registration_id__in=list(by_reg))
                 .exclude(status=Flag.OPEN).order_by('id')):
        last_closed[(flag.registration_id, flag.kind)] = flag
    counts = Counter()
    seen = set()
    for hit in hits:
        key = (hit.registration_id, hit.kind)
        seen.add(key)
        reg = by_reg[hit.registration_id]
        fields = dict(reason=hit.reason, evidence=hit.evidence, as_of=hit.as_of, urgent=hit.urgent,
                      priority=hit.registration_id in priority, last_seen_on=today)
        flag = open_flags.get(key)
        if flag is not None:
            for name, val in fields.items():
                setattr(flag, name, val)
            flag.save()
            counts['kept'] += 1
        elif _reopens(last_closed.get(key), hit):
            Flag.objects.create(registration=reg, child_id=reg.child_id, center_id=reg.center_id,
                                partner_id=reg.partner_id, round_id=reg.round_id, kind=hit.kind,
                                opened_on=today, **fields)
            counts['opened'] += 1
    for key, flag in open_flags.items():
        if key not in seen:
            flag.status, flag.resolved_on = Flag.RESOLVED, today
            flag.save(update_fields=['status', 'resolved_on', 'modified'])
            counts['resolved'] += 1
    return counts


# ------------------------------------------------------------------------------------ summary
def _age_band(child, today):
    try:
        age = today.year - int(child.birthday_year)
    except (TypeError, ValueError, AttributeError):
        return 'Unknown'
    for top, label in ((5, '0-5'), (9, '6-9'), (14, '10-14'), (17, '15-17')):
        if age <= top:
            return label
    return '18+'


def summary(center, regs, context, today, settings):
    month = today.replace(day=1)
    flags = list(Flag.objects.filter(registration_id__in=[r.id for r in regs]))
    open_flags = [f for f in flags if f.status == Flag.OPEN]
    flagged = {f.registration_id for f in open_flags}
    this_month = [f for f in flags if f.opened_on >= month]
    followed = [f for f in flags if f.followed_up_on and f.followed_up_on >= month]
    target = settings.followup_days
    on_time = [f for f in this_month if f.followed_up_on and (f.followed_up_on - f.opened_on).days <= target]
    waits = [(f.followed_up_on - f.opened_on).days for f in followed]
    window_start = today - datetime.timedelta(days=27)
    days = [e for entries in context['attendance'].values() for e in entries if e[0] >= window_start]
    required = list(m.ProvidedServices.objects.filter(registration_id__in=[r.id for r in context['active']],
                                                     required=True).values_list('registration_id', 'completed'))
    with_checklist = {reg_id for reg_id, _done in required}
    core = [r for r in context['active'] if (r.type or '') == 'Core-Package']
    breakdown = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for reg in context['active']:
        child = reg.child
        for name, group in (('gender', (child.gender if child else None) or 'Unknown'),
                            ('age', _age_band(child, today))):
            breakdown[name][group][0] += 1
            breakdown[name][group][1] += reg.id in flagged
    return {
        'children': len(context['active']),
        'dropouts': len(context['dropped']),
        'attendance': {
            'rate_28_days': rules._rate(days),
            'child_days_28_days': len(days),
            'sheets': context['sheets']['sheets'],
            'sheets_all_present': context['sheets']['sheets_all_present'],
        },
        'flags': {
            'children_flagged': len(flagged),
            'open': len(open_flags),
            'urgent_open': sum(1 for f in open_flags if f.urgent),
            'open_by_kind': dict(Counter(f.kind for f in open_flags)),
            'opened_this_month': len(this_month),
            'followed_up_this_month': len(followed),
            'followed_up_on_time': len(on_time),
            'median_days_to_follow_up': statistics.median(waits) if waits else None,
            'open_longer_than_target': sum(1 for f in open_flags if (today - f.opened_on).days > target),
        },
        'services': {
            'required': len(required),
            'completed': sum(1 for _r, done in required if done),
            'core_children_without_checklist': sum(1 for r in core if r.id not in with_checklist),
        },
        'learning': {'assessed': context['assessed'], 'no_progress': context['no_gain']},
        'breakdown': {k: {g: list(v) for g, v in groups.items()} for k, groups in breakdown.items()},
        'as_of': today.isoformat(),
    }


# ---------------------------------------------------------------------------------------- run
def current_rounds():
    return list(m.Round.objects.filter(current_year=True))


def refresh(today=None, rounds=None, center_ids=None):
    """Flags and summaries of every centre with registrations in the current round(s)."""
    today = today or local_today()
    rounds = rounds if rounds is not None else current_rounds()
    settings = FlagSettings.current()
    centers = (registrations(rounds).values_list('center_id', flat=True).distinct())
    if center_ids:
        centers = [c for c in centers if c in set(center_ids)]
    totals = Counter()
    for center_id in centers:
        try:
            with transaction.atomic():
                regs = list(registrations(rounds, center_id))
                hits, context = evaluate(regs, center_id, today, settings)
                totals.update(reconcile(regs, hits, today))
                center = regs[0].center
                for round_id in {r.round_id for r in regs}:
                    round_regs = [r for r in regs if r.round_id == round_id]
                    ids = {r.id for r in round_regs}
                    round_context = dict(context, active=[r for r in context['active'] if r.id in ids],
                                         dropped={k: v for k, v in context['dropped'].items() if k in ids})
                    CenterSummary.objects.update_or_create(
                        center_id=center_id, round_id=round_id, month=today.replace(day=1),
                        defaults={'partner_id': center.partner_id,
                                  'figures': summary(center, round_regs, round_context, today, settings)})
                totals['centres'] += 1
        except Exception:
            logger.exception('wellbeing flags of centre %s failed', center_id)
            totals['failed'] += 1
    return totals


def scope_filter(user):
    """The flags a user may see: their centre's or their partner's; None for no child-level access."""
    from student_registration.users.templatetags.custom_tags import has_group

    if has_group(user, 'MSCC_CENTER') and user.center_id:
        return Q(center_id=user.center_id)
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return Q(partner_id=user.partner_id)
    return None
