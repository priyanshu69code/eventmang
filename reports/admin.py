from django.contrib import admin
from .models import Report, UserActivityLog


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'generated_by', 'date_from', 'date_to', 'is_completed', 'created_at')
    list_filter = ('report_type', 'is_completed', 'created_at')
    search_fields = ('name', 'generated_by__username')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Report Information', {
            'fields': ('name', 'report_type', 'generated_by')
        }),
        ('Date Range', {
            'fields': ('date_from', 'date_to')
        }),
        ('Additional Information', {
            'fields': ('filters', 'file_path', 'is_completed')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'ip_address', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('user__username', 'action', 'resource_type', 'resource_id', 'ip_address')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action', 'resource_type', 'resource_id')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Additional Details', {
            'fields': ('details',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
