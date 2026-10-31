from django.contrib import admin

from .models import CenterSummary, Flag, FlagSettings


@admin.register(FlagSettings)
class FlagSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'absence_streak', 'attendance_rate_below', 'service_weeks', 'followup_days')

    def has_add_permission(self, request):
        return not FlagSettings.objects.exists()


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'status', 'urgent', 'priority', 'center', 'opened_on', 'followed_up_on', 'result')
    list_filter = ('status', 'kind', 'urgent', 'priority', 'round')
    search_fields = ('registration__id', 'center__name')
    raw_id_fields = ('registration', 'child', 'center', 'partner', 'followed_up_by')
    readonly_fields = ('reason', 'evidence', 'as_of', 'opened_on', 'last_seen_on', 'resolved_on', 'created', 'modified')


@admin.register(CenterSummary)
class CenterSummaryAdmin(admin.ModelAdmin):
    list_display = ('center', 'partner', 'round', 'month', 'computed_at')
    list_filter = ('month', 'round')
    search_fields = ('center__name',)
    raw_id_fields = ('center', 'partner')
    readonly_fields = ('figures', 'computed_at')
