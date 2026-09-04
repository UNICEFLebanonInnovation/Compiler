# -*- coding: utf-8 -*-
"""Admin screens for the replication outbox."""

from __future__ import unicode_literals, absolute_import, division

from django.contrib import admin

from .models import STATUS_PENDING, SchoolCenterLink, SyncEvent


@admin.register(SchoolCenterLink)
class SchoolCenterLinkAdmin(admin.ModelAdmin):
    """Maps a Compiler school to the BMA-NFE centre its teachers belong to.

    Teachers are stored per school here and per centre in BMA-NFE. Until a
    school appears in this table its teachers replicate without a centre.
    """

    list_display = ('school', 'center', 'modified')
    list_select_related = ('school', 'center')
    search_fields = ('school__name', 'school__number', 'center__name', 'center__p_code')
    autocomplete_fields = ()
    raw_id_fields = ('school', 'center')


@admin.register(SyncEvent)
class SyncEventAdmin(admin.ModelAdmin):
    """Read-only view of what is queued for, or was sent to, BMA-NFE."""

    list_display = (
        'created', 'resource', 'source_id', 'operation', 'status',
        'attempts', 'conflict', 'remote_id', 'short_error',
    )
    list_filter = ('status', 'resource', 'operation', 'conflict')
    search_fields = ('source_id', 'event_id', 'last_error', 'remote_detail')
    date_hierarchy = 'created'
    readonly_fields = (
        'event_id', 'resource', 'operation', 'source_id', 'payload', 'status',
        'attempts', 'next_attempt', 'last_error', 'remote_detail', 'remote_id',
        'conflict', 'ignored_fields', 'sent_at', 'created', 'modified',
    )
    actions = ('requeue',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Last error')
    def short_error(self, obj):
        """Return the error trimmed to fit the changelist."""
        error = (obj.last_error or '').strip()
        return error[:100] + ('...' if len(error) > 100 else '')

    @admin.action(description='Send selected events again')
    def requeue(self, request, queryset):
        """Reset the selected events so the next sweep retries them.

        Useful after fixing whatever made them fail -- a missing centre in
        BMA-NFE, an expired token, a firewall rule.
        """
        updated = queryset.update(
            status=STATUS_PENDING, next_attempt=None, attempts=0, last_error='',
        )
        self.message_user(request, '{} event(s) queued to be sent again.'.format(updated))
