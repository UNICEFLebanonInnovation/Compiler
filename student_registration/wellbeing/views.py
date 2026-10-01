"""Makani wellbeing pages: the flags of a centre or a partner (child level, for the people who
already see those children), the follow-up of a flag, and the centre summaries (no child data)."""

import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from student_registration.users.templatetags.custom_tags import has_group

from .engine import scope_filter
from .forms import FollowUpForm
from .models import CenterSummary, Flag, FlagSettings, today


def _summary_scope(user):
    if user.is_superuser or has_group(user, 'MSCC_UNICEF'):
        return Q()
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return Q(partner_id=user.partner_id)
    if has_group(user, 'MSCC_CENTER') and user.center_id:
        return Q(center_id=user.center_id)
    return None


@login_required
def flag_list(request):
    scope = scope_filter(request.user)
    if scope is None:
        if _summary_scope(request.user) is not None:
            return redirect('wellbeing:summaries')
        raise PermissionDenied
    status = request.GET.get('status', Flag.OPEN)
    kind = request.GET.get('kind', '')
    flags = (Flag.objects.filter(scope)
             .select_related('child', 'center', 'registration'))
    if status in dict(Flag.STATUSES):
        flags = flags.filter(status=status)
    if kind in dict(Flag.KINDS):
        flags = flags.filter(kind=kind)
    center = request.GET.get('center', '')
    if center.isdigit():
        flags = flags.filter(center_id=int(center))
    counts = dict(Flag.objects.filter(scope, status=Flag.OPEN).values_list('kind').order_by()
                  .annotate(n=Count('id')))
    page = Paginator(flags, 50).get_page(request.GET.get('page'))
    centers = (Flag.objects.filter(scope).values_list('center_id', 'center__name').order_by('center__name')
               .distinct())
    return render(request, 'wellbeing/flags.html', {
        'page': page,
        'status': status,
        'kind': kind,
        'center': center,
        'kinds': Flag.KINDS,
        'statuses': Flag.STATUSES,
        'counts': [(code, label, counts.get(code, 0)) for code, label in Flag.KINDS],
        'centers': centers if not request.user.center_id else [],
        'settings': FlagSettings.current(),
        'today': today(),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def follow_up(request, pk):
    scope = scope_filter(request.user)
    if scope is None:
        raise PermissionDenied
    flag = get_object_or_404(Flag.objects.filter(scope).select_related('child', 'center'), pk=pk)
    form = FollowUpForm(request.POST or None, flag=flag)
    if request.method == 'POST' and flag.status == Flag.OPEN and form.is_valid():
        flag.status = Flag.FOLLOWED_UP
        flag.follow_up_type = form.cleaned_data['follow_up_type']
        flag.result = form.cleaned_data['result']
        flag.followed_up_on = form.cleaned_data['followed_up_on']
        flag.note = form.cleaned_data['note']
        flag.followed_up_by = request.user
        flag.save()
        messages.success(request, 'Follow-up recorded.')
        return redirect('wellbeing:flags')
    return render(request, 'wellbeing/follow_up.html', {'flag': flag, 'form': form})


@login_required
def summaries(request):
    scope = _summary_scope(request.user)
    if scope is None:
        raise PermissionDenied
    months = list(CenterSummary.objects.filter(scope).values_list('month', flat=True).distinct().order_by('-month'))
    try:
        month = datetime.date.fromisoformat(request.GET.get('month', ''))
    except ValueError:
        month = months[0] if months else None
    rows = (CenterSummary.objects.filter(scope, month=month).select_related('center', 'partner', 'round')
            if month else CenterSummary.objects.none())
    rows = list(rows)
    total = {'children': 0, 'children_flagged': 0, 'opened': 0, 'on_time': 0, 'urgent': 0}
    for row in rows:
        f = row.figures
        total['children'] += f.get('children', 0)
        total['children_flagged'] += f.get('flags', {}).get('children_flagged', 0)
        total['opened'] += f.get('flags', {}).get('opened_this_month', 0)
        total['on_time'] += f.get('flags', {}).get('followed_up_on_time', 0)
        total['urgent'] += f.get('flags', {}).get('urgent_open', 0)
    return render(request, 'wellbeing/summaries.html', {
        'rows': rows,
        'months': months,
        'month': month,
        'total': total,
        'kinds': Flag.KINDS,
        'settings': FlagSettings.current(),
        'child_level': scope_filter(request.user) is not None,
    })
