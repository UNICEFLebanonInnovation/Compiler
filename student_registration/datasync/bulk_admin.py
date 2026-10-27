"""Partner-scoped previews and bulk-sync controls in the Compiler admin."""
import uuid

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseRedirect
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
from .serializers import MODEL_FOR_RESOURCE
from .partner_scope import available_partners


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
        return [path('', self.admin_site.admin_view(self.changelist_view),
                     name='datasync_bulksyncrun_changelist')]

    def has_add_permission(self, request):
        return False  # Requests are created only by the scoped, CSRF-protected form.

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _can_start(self, request):
        return request.user.has_perm('datasync.add_bulksyncrun')

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        data = request.POST if request.method == 'POST' else request.GET
        form = RoundSyncForm(data or None)
        partners = available_partners(request.user)
        can_select_round = can_read(request.user, 'mscc.round')
        allowed = {resource for resource in MODEL_FOR_RESOURCE if can_read(request.user, resource)}
        run = None
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
            if request.method == 'GET':
                form = RoundSyncForm({'partner': run.partner_id, 'round': run.round_id,
                                      'category': run.selected_categories})

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
        if form.is_bound and form.is_valid() and run is None:
            plan = RoundSyncPlan(form.cleaned_data['round'], form.cleaned_data['category'], form.cleaned_data['partner'])
            summary = plan.summary()
            if any(row['count'] and not can_read(request.user, row['resource']) for row in summary):
                raise PermissionDenied
            issues = plan.errors()
        if not sync_enabled():
            issues.append('Synchronization is disabled. Enable DATASYNC_ENABLED before starting.')
        if not partners.exists():
            issues.append('No partners are available. Check your partner assignment and partner view permission.')
        if not getattr(settings, 'DATASYNC_TARGET_URL', '') or not getattr(settings, 'DATASYNC_TARGET_TOKEN', ''):
            issues.append('The NFE destination URL and service token must be configured before starting.')

        if request.method == 'POST':
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
                            transaction.on_commit(schedule_bulk_sweep)
                    self.message_user(request, 'Bulk sync requested. Delivery status appears below.', messages.SUCCESS)
                    return HttpResponseRedirect('{}?{}'.format(
                        reverse('admin:datasync_bulksyncrun_changelist'), urlencode({'run': run.pk})))

        recent = BulkSyncRun.objects.select_related('partner', 'round', 'requested_by')
        if not request.user.is_superuser:
            recent = recent.filter(requested_by=request.user, partner__in=partners)
        if form.is_bound and form.is_valid() and form.cleaned_data.get('partner'):
            recent = recent.filter(partner=form.cleaned_data['partner'])
        total = sum(row['count'] for row in summary)
        preview_page = Paginator(range(total), 50).get_page(request.GET.get('page'))
        preview_rows = plan.preview(preview_page.start_index() - 1, 50) if plan and total else []
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
        context = {
            **self.admin_site.each_context(request),
            'title': 'Bulk sync', 'opts': self.model._meta, 'form': form,
            'summary': summary, 'issues': issues, 'preview_rows': preview_rows,
            'preview_page': preview_page, 'preview_query': preview_query, 'preview_total': total,
            'request_id': uuid.uuid4(), 'can_start': self._can_start(request),
            'category_selection_label': category_selection_label,
            'can_select_round': can_select_round,
            'run': run, 'progress': progress, 'event_page': event_page,
            'recent_runs': recent[:10], 'has_view_permission': True,
            'school_links_url': reverse('admin:datasync_schoolcenterlink_changelist'),
            'events_url': reverse('admin:datasync_syncevent_changelist'),
        }
        context.update(extra_context or {})
        return TemplateResponse(request, 'admin/datasync/bulk_round_sync.html', context)
