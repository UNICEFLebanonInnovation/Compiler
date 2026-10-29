"""Partner-scoped previews and bulk-sync controls in the Compiler admin."""
import uuid
from functools import partial

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core import signing
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.http import urlencode

from student_registration.mscc.models import Round
from student_registration.schools.models import PartnerOrganization

from .bulk_sync import RoundSyncPlan, run_progress, schedule_bulk_sweep
from .bulk_types import ALL_CATEGORIES, CATEGORY_CHOICES, GLOBAL_CATEGORIES, normalize_categories, requires_round
from .models import BulkSyncRun
from .outbox import sync_enabled
from .health import check_sync_health
from .serializers import MODEL_FOR_RESOURCE
from .partner_scope import available_partners
from .pending_cleanup import pending_for_user, remove_pending
from .query_budget import preview_budget, PreviewTimeout


PREVIEW_TIMEOUT_MESSAGE = ('Preview took too long. Choose fewer categories or a narrower round and try again. '
                           'No new sync request was created.')


class RoundSyncForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=PartnerOrganization.objects.order_by('name', 'pk'), required=True)
    round = forms.ModelChoiceField(queryset=Round.objects.order_by('-year', 'name'), required=False)
    category = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES, label='Element categories', initial=[ALL_CATEGORIES],
        widget=forms.CheckboxSelectMultiple,
    )

    def clean_category(self):
        return normalize_categories(self.cleaned_data['category'])

    def clean(self):
        cleaned = super().clean()
        categories = cleaned.get('category')
        if categories:
            if requires_round(categories):
                if not cleaned.get('round'):
                    self.add_error('round', 'Choose a round for the selected categories.')
            else:
                cleaned['round'] = None
        return cleaned


def can_read(user, resource):
    if resource not in MODEL_FOR_RESOURCE:
        return user.is_superuser  # Historical disabled resource audit.
    meta = MODEL_FOR_RESOURCE[resource]._meta
    return user.has_perm('{}.view_{}'.format(meta.app_label, meta.model_name)) or user.has_perm(
        '{}.change_{}'.format(meta.app_label, meta.model_name))


@admin.register(BulkSyncRun)
class BulkSyncRunAdmin(admin.ModelAdmin):
    def get_urls(self):
        return [path('remove-pending/', self.admin_site.admin_view(self.remove_pending_view),
                     name='datasync_bulksyncrun_remove_pending'),
                path('', self.admin_site.admin_view(self.changelist_view),
                     name='datasync_bulksyncrun_changelist')]

    def has_add_permission(self, request):
        return False  # Requests are created only by the scoped, CSRF-protected form.

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _can_start(self, request):
        return request.user.has_perm('datasync.add_bulksyncrun')

    def remove_pending_view(self, request):
        if not self.has_view_permission(request) or not self._can_start(request):
            raise PermissionDenied
        if request.method not in ('GET', 'POST'):
            return HttpResponseNotAllowed(['GET', 'POST'])
        try:
            partner_id = int(request.GET.get('partner', ''))
        except (TypeError, ValueError):
            raise Http404
        partner = get_object_or_404(available_partners(request.user), pk=partner_id)
        if request.method == 'POST':
            try:
                payload = signing.loads(request.POST.get('confirmation', ''),
                                        salt='datasync.remove_pending_bulk', max_age=900)
            except signing.BadSignature:
                return HttpResponseBadRequest('Removal confirmation expired or is invalid. Reopen the confirmation page.')
            if not isinstance(payload, dict) or payload.get('user') != request.user.pk or payload.get('partner') != partner.pk:
                raise PermissionDenied
            ids = payload.get('runs')
            if not isinstance(ids, list):
                return HttpResponseBadRequest('Invalid removal selection.')
            try:
                ids = [uuid.UUID(value) for value in ids]
            except (TypeError, ValueError, AttributeError):
                return HttpResponseBadRequest('Invalid removal selection.')
            removed, skipped = remove_pending(request.user, partner, ids)
            if removed:
                self.message_user(request, 'Removed {} pending bulk sync request(s) for {}.'.format(removed, partner), messages.SUCCESS)
            if skipped:
                self.message_user(request,
                    'Kept {} request(s): a worker is writing their queue records, they have already started, '
                    'or they are no longer available. Refresh status before trying again.'.format(skipped), messages.WARNING)
            elif not removed:
                self.message_user(request, 'No eligible pending requests remain to remove.', messages.INFO)
            return HttpResponseRedirect(reverse('admin:datasync_bulksyncrun_changelist'))

        pending = list(pending_for_user(request.user, partner).select_related('round', 'requested_by')
                       .order_by('created', 'pk'))
        confirmation = signing.dumps({'user': request.user.pk, 'partner': partner.pk,
                                      'runs': [str(run.pk) for run in pending]},
                                     salt='datasync.remove_pending_bulk', compress=True)
        return TemplateResponse(request, 'admin/datasync/remove_pending_bulk_syncs.html', {
            **self.admin_site.each_context(request), 'title': 'Remove pending bulk syncs',
            'opts': self.model._meta, 'partner': partner, 'pending_runs': pending,
            'confirmation': confirmation, 'back_url': reverse('admin:datasync_bulksyncrun_changelist'),
        })

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        data = request.POST if request.method == 'POST' else request.GET
        form = RoundSyncForm(data or None)
        partners = available_partners(request.user)
        can_select_round = can_read(request.user, 'mscc.round')
        allowed = {resource for resource in MODEL_FOR_RESOURCE if can_read(request.user, resource)}
        run = None
        diagnostics = None
        action = request.POST.get('sync_action') if request.method == 'POST' else None
        if request.GET.get('sync_action'):
            return HttpResponseNotAllowed(['POST'])
        run_id = request.GET.get('run')
        if run_id:
            try:
                run_id = uuid.UUID(run_id)
            except ValueError:
                raise PermissionDenied
            runs = BulkSyncRun.objects.select_related('partner', 'round', 'requested_by')
            if not request.user.is_superuser:
                runs = runs.filter(requested_by=request.user, partner__in=partners)
            run = get_object_or_404(runs, pk=run_id)
            if request.method == 'GET' or action:
                form = RoundSyncForm({'partner': run.partner_id, 'round': run.round_id,
                                      'category': run.selected_categories})

        if action:
            if action not in ('diagnose', 'notify_queue'):
                return HttpResponseBadRequest('Unknown sync action.')
            if run is None or not self._can_start(request):
                raise PermissionDenied
            if action == 'diagnose':
                diagnostics = check_sync_health()
            elif run.preparation == 'waiting':
                if not sync_enabled():
                    self.message_user(request, 'Synchronization is disabled in Compiler.', messages.ERROR)
                else:
                    # Recheck the saved selection before waking an existing run.
                    try:
                        with preview_budget():
                            plan = RoundSyncPlan(run.round, run.selected_categories, run.partner)
                            if any(row['count'] and not can_read(request.user, row['resource']) for row in plan.summary()):
                                raise PermissionDenied
                    except PreviewTimeout:
                        self.message_user(request, 'The selection check took too long. No queue notification was sent. '
                                          'The saved request is preserved; try again shortly.', messages.WARNING)
                        return HttpResponseRedirect('{}?{}'.format(
                            reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))
                    notified = schedule_bulk_sweep(run.pk)
                    self.message_user(request,
                        'Queue notification accepted. Refresh status to check whether the worker has prepared this request.'
                        if notified else 'The queue could not be notified. The saved request and error remain below.',
                        messages.SUCCESS if notified else messages.ERROR)
                return HttpResponseRedirect('{}?{}'.format(
                    reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))
            else:
                self.message_user(request, 'This request has already left the waiting stage.', messages.INFO)
                return HttpResponseRedirect('{}?{}'.format(
                    reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))

        form.fields['partner'].queryset = partners
        if not can_select_round:
            form.fields['round'].queryset = Round.objects.none()
        form.fields['category'].choices = [
            (key, label) for key, label in CATEGORY_CHOICES
            if (key == ALL_CATEGORIES and len(allowed) == len(MODEL_FOR_RESOURCE)) or
               (key in allowed and (key in GLOBAL_CATEGORIES or can_select_round))
        ]

        plan = None
        summary = []
        issues = []
        total = 0
        preview_rows = []
        preview_page = Paginator(range(0), 50).get_page(1)
        if form.is_bound and form.is_valid() and run is None:
            try:
                with preview_budget():
                    plan = RoundSyncPlan(form.cleaned_data['round'], form.cleaned_data['category'], form.cleaned_data['partner'])
                    summary = plan.summary()
                    if any(row['count'] and not can_read(request.user, row['resource']) for row in summary):
                        raise PermissionDenied
                    issues = plan.errors()
                    total = sum(row['count'] for row in summary)
                    preview_page = Paginator(range(total), 50).get_page(request.GET.get('page'))
                    if request.method == 'GET' and total:
                        preview_rows = plan.preview(preview_page.start_index() - 1, 50)
            except PreviewTimeout:
                plan, summary, total, preview_rows = None, [], 0, []
                issues = [PREVIEW_TIMEOUT_MESSAGE]
        if not sync_enabled():
            issues.append('Synchronization is disabled. Enable DATASYNC_ENABLED before starting.')
        if not partners.exists():
            issues.append('No partners are available. Check your partner assignment and partner view permission.')
        if not getattr(settings, 'DATASYNC_TARGET_URL', '') or not getattr(settings, 'DATASYNC_TARGET_TOKEN', ''):
            issues.append('The NFE destination URL and service token must be configured before starting.')

        if request.method == 'POST' and not action:
            if not self._can_start(request):
                raise PermissionDenied
            if plan is not None and not issues:
                try:
                    request_id = uuid.UUID(request.POST.get('request_id', ''))
                except ValueError:
                    form.add_error(None, 'Reload the preview before starting a sync.')
                else:
                    with transaction.atomic():
                        run, created = BulkSyncRun.objects.get_or_create(pk=request_id, defaults={
                            'partner': plan.partner,
                            'round': plan.round, 'category': plan.category, 'categories': plan.categories,
                            'requested_by': request.user,
                        })
                        if (run.partner_id != plan.partner.pk or
                                run.round_id != (plan.round.pk if plan.round else None) or run.selected_categories != plan.categories or
                                run.requested_by_id != request.user.pk):
                            raise PermissionDenied
                        if created:
                            transaction.on_commit(partial(schedule_bulk_sweep, run.pk))
                    self.message_user(request, 'Bulk sync requested. Delivery status appears below.', messages.SUCCESS)
                    return HttpResponseRedirect('{}?{}'.format(
                        reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))

        recent = BulkSyncRun.objects.select_related('partner', 'round', 'requested_by')
        if not request.user.is_superuser:
            recent = recent.filter(requested_by=request.user, partner__in=partners)
        if form.is_bound and form.is_valid() and form.cleaned_data.get('partner'):
            recent = recent.filter(partner=form.cleaned_data['partner'])
        preview_query = urlencode({'partner': form['partner'].value() or '',
                                   'round': form['round'].value() or '',
                                   'category': form['category'].value() or []}, doseq=True)
        chosen = form['category'].value() or []
        chosen_labels = [str(label) for key, label in form.fields['category'].choices if key in chosen]
        category_selection_label = (chosen_labels[0] if len(chosen_labels) == 1 else
                                    '{} categories selected'.format(len(chosen_labels)) if chosen_labels else
                                    'Choose categories')
        event_page = None
        progress = None
        if run is not None:
            # Re-check the permissions against the saved run when viewing its audit.
            if any(not can_read(request.user, resource) for resource, count in run.queued_counts.items() if count):
                raise PermissionDenied
            event_page = Paginator(run.events.order_by('id'), 50).get_page(request.GET.get('event_page'))
            progress = run_progress(run)
        selected_partner = getattr(form, 'cleaned_data', {}).get('partner')
        removal_count = pending_for_user(request.user, selected_partner).count() if selected_partner and self._can_start(request) else 0
        removal_url = '{}?{}'.format(reverse('admin:datasync_bulksyncrun_remove_pending'),
                                    urlencode({'partner': selected_partner.pk})) if selected_partner else ''
        context = {
            **self.admin_site.each_context(request),
            'title': 'Bulk sync', 'opts': self.model._meta, 'form': form,
            'summary': summary, 'issues': issues, 'preview_rows': preview_rows,
            'preview_page': preview_page, 'preview_query': preview_query, 'preview_total': total,
            'request_id': uuid.uuid4(), 'can_start': self._can_start(request),
            'category_selection_label': category_selection_label,
            'can_select_round': can_select_round,
            'run': run, 'progress': progress, 'event_page': event_page,
            'diagnostics': diagnostics,
            'pending_removal_count': removal_count, 'remove_pending_url': removal_url,
            'selected_partner': selected_partner,
            'recent_runs': recent[:10], 'has_view_permission': True,
            'school_links_url': reverse('admin:datasync_schoolcenterlink_changelist'),
            'events_url': reverse('admin:datasync_syncevent_changelist'),
        }
        context.update(extra_context or {})
        return TemplateResponse(request, 'admin/datasync/bulk_round_sync.html', context)
