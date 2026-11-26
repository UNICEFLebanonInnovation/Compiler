"""Partner-scoped selection and one active bulk sync in the Compiler admin."""
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

from .bulk_sync import run_progress, schedule_bulk_sweep
from .bulk_types import ALL_CATEGORIES, CATEGORY_CHOICES, GLOBAL_CATEGORIES, normalize_categories, requires_round
from .models import BulkSyncRun
from .outbox import sync_enabled
from .health import check_sync_health
from .serializers import MODEL_FOR_RESOURCE
from .partner_scope import available_partners
from .pending_cleanup import pending_for_user, remove_pending
from .bulk_jobs import BulkBusy, current_run, required_resources, retry_run, stop_run, submit_run


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
        if request.method not in ('GET', 'POST') or request.GET.get('sync_action'):
            return HttpResponseNotAllowed(['GET', 'POST'])
        partners = available_partners(request.user)
        readable = {key for key in MODEL_FOR_RESOURCE if can_read(request.user, key)}
        visible_runs = BulkSyncRun.objects.select_related('partner', 'round', 'requested_by')
        if not request.user.is_superuser:
            visible_runs = visible_runs.filter(requested_by=request.user, partner__in=partners)
        run = None
        if request.GET.get('run'):
            try:
                run = get_object_or_404(visible_runs, pk=uuid.UUID(request.GET['run']))
            except ValueError:
                raise PermissionDenied
        active = current_run()
        visible_active = visible_runs.filter(pk=active.pk).first() if active else None
        diagnostics = None
        action = request.POST.get('sync_action') if request.method == 'POST' else None
        if action:
            if not self._can_start(request) or run is None:
                raise PermissionDenied
            if any(not can_read(request.user, key) for key in required_resources(run.selected_categories)):
                raise PermissionDenied
            if action == 'diagnose':
                diagnostics = check_sync_health()
            elif action in ('retry', 'notify_queue', 'stop'):
                try:
                    if action == 'stop':
                        stopped = stop_run(run.pk)
                        self.message_user(request, 'Sync stopped. Records already received by BMA-NFE are preserved. '
                            'An upload already in progress may finish.' if stopped else
                            'This sync has already finished. There are no further attempts to stop.',
                            messages.SUCCESS if stopped else messages.INFO)
                    else:
                        if not sync_enabled():
                            self.message_user(request, 'Synchronization is disabled in Compiler.', messages.ERROR)
                            return HttpResponseRedirect('{}?{}'.format(
                                reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))
                        retry_run(run.pk)
                        notified = schedule_bulk_sweep(run.pk)
                        self.message_user(request, 'Sync retry requested.' if notified else
                            'The sync worker could not be notified. The saved sync and its errors are preserved.',
                            messages.SUCCESS if notified else messages.WARNING)
                except BulkBusy as error:
                    self.message_user(request, str(error), messages.WARNING)
                return HttpResponseRedirect('{}?{}'.format(
                    reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))
            else:
                return HttpResponseBadRequest('Unknown sync action.')
        data = request.POST if request.method == 'POST' and not action else (
            request.GET if any(key in request.GET for key in ('partner', 'round', 'category')) else None)
        initial_run = run or visible_active
        form = RoundSyncForm(data or None, initial={
            'partner': initial_run.partner_id, 'round': initial_run.round_id,
            'category': initial_run.selected_categories} if initial_run else None)
        can_select_round = can_read(request.user, 'mscc.round')
        form.fields['partner'].queryset = partners
        if not can_select_round:
            form.fields['round'].queryset = Round.objects.none()
        form.fields['category'].choices = [(key, label) for key, label in CATEGORY_CHOICES
            if (key == ALL_CATEGORIES and len(readable) == len(MODEL_FOR_RESOURCE)) or
               (key in readable and (key in GLOBAL_CATEGORIES or can_select_round))]
        issues = []
        if not sync_enabled():
            issues.append('Synchronization is disabled in Compiler.')
        if not getattr(settings, 'DATASYNC_TARGET_URL', '') or not getattr(settings, 'DATASYNC_TARGET_TOKEN', ''):
            issues.append('The NFE destination URL and service token must be configured before starting.')
        if not partners.exists():
            issues.append('No partners are available. Check your partner assignment and partner view permission.')
        if request.method == 'POST' and not action:
            if not self._can_start(request):
                raise PermissionDenied
            if form.is_valid():
                categories = form.cleaned_data['category']
                if any(not can_read(request.user, key) for key in required_resources(categories)):
                    raise PermissionDenied
                if not issues:
                    try:
                        request_id = uuid.UUID(request.POST.get('request_id', ''))
                    except ValueError:
                        form.add_error(None, 'Reload this page before starting a sync.')
                    else:
                        try:
                            with transaction.atomic():
                                saved, created = submit_run(request.user, form.cleaned_data['partner'],
                                    form.cleaned_data['round'], categories, request_id)
                                if created:
                                    transaction.on_commit(partial(schedule_bulk_sweep, saved.pk))
                        except BulkBusy as error:
                            self.message_user(request, str(error), messages.WARNING)
                        else:
                            return HttpResponseRedirect('{}?{}'.format(
                                reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': saved.pk})))
        # GET only reads the form choices and job status. No source record
        # counts, attendance checks, previews or photo access run in the web app.
        if run is None:
            run = visible_active or visible_runs.order_by('-created').first()
        event_page = progress = None
        if run:
            if any(not can_read(request.user, key) for key, count in run.queued_counts.items() if count):
                raise PermissionDenied
            event_page = Paginator(run.events.order_by('id'), 50).get_page(request.GET.get('event_page'))
            progress = run_progress(run)
        chosen = form['category'].value() or []
        labels = [str(label) for key, label in form.fields['category'].choices if key in chosen]
        label = labels[0] if len(labels) == 1 else '{} categories selected'.format(len(labels)) if labels else 'Choose categories'
        recent = visible_runs
        if form.is_bound and form.is_valid() and form.cleaned_data.get('partner'):
            recent = recent.filter(partner=form.cleaned_data['partner'])
        context = {**self.admin_site.each_context(request), 'title': 'Bulk sync', 'opts': self.model._meta,
            'form': form, 'request_id': uuid.uuid4(), 'issues': issues, 'can_start': self._can_start(request),
            'can_select_round': can_select_round, 'category_selection_label': label,
            'busy': bool(active), 'active_run': visible_active, 'run': run, 'event_page': event_page,
            'progress': progress, 'diagnostics': diagnostics, 'recent_runs': recent.order_by('-created')[:10],
            'can_retry': bool(run and (run.preparation in ('waiting', 'failed') or
                                      run.preparation == 'ready' and progress['failed'])),
            'can_stop': bool(run and (run.preparation == 'waiting' or
                                     run.preparation == 'ready' and (progress['pending'] or progress['failed']))),
            'events_url': reverse('admin:datasync_syncevent_changelist')}
        context.update(extra_context or {})
        return TemplateResponse(request, 'admin/datasync/bulk_round_sync.html', context)
