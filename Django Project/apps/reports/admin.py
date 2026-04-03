from django.contrib import admin
from django.utils.html import format_html
from .models import IssueReport, Verification, StatusLog


class StatusLogInline(admin.TabularInline):
    model = StatusLog
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'note', 'created_at', 'created_by')
    can_delete = False


class VerificationInline(admin.TabularInline):
    model = Verification
    extra = 0
    readonly_fields = ('session_key', 'created_at')
    can_delete = False


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ('ref_id', 'category_display', 'status_badge', 'vote_count_display',
                    'address_text', 'reporter_phone', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('ref_id', 'description', 'address_text', 'reporter_name', 'reporter_phone')
    readonly_fields = ('ref_id', 'created_at', 'updated_at', 'vote_count_display')
    inlines = [StatusLogInline, VerificationInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Reference', {
            'fields': ('ref_id', 'status', 'whatsapp_sent'),
        }),
        ('Issue Details', {
            'fields': ('category', 'description', 'photo'),
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address_text', 'ward'),
        }),
        ('Reporter', {
            'fields': ('reporter_name', 'reporter_phone'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'vote_count_display'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Category')
    def category_display(self, obj):
        return f"{obj.category_icon} {obj.get_category_display()}"

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'logged': '#9a9a8e',
            'assigned': '#e76f51',
            'dispatched': '#2d6a4f',
            'resolved': '#1b7a3e',
            'closed': '#5a5a52',
        }
        color = colors.get(obj.status, '#ccc')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )

    @admin.display(description='Votes')
    def vote_count_display(self, obj):
        return obj.vote_count

    def save_model(self, request, obj, form, change):
        if change:
            old = IssueReport.objects.get(pk=obj.pk)
            if old.status != obj.status:
                StatusLog.objects.create(
                    issue=obj,
                    from_status=old.status,
                    to_status=obj.status,
                    created_by=request.user.username,
                    note=f'Status updated via admin by {request.user.username}',
                )
        super().save_model(request, obj, form, change)


@admin.register(StatusLog)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('issue', 'from_status', 'to_status', 'created_by', 'created_at')
    list_filter = ('to_status', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('issue', 'session_key', 'created_at')
    readonly_fields = ('created_at',)
