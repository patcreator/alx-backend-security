from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'country', 'city', 'timestamp', 'path')
    list_filter = ('timestamp', 'country', 'city')
    search_fields = ('ip_address', 'path', 'country', 'city')
    readonly_fields = ('ip_address', 'country', 'city', 'timestamp', 'path')
    date_hierarchy = 'timestamp'
    list_per_page = 50

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('ip_address',)

@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'detected_at', 'is_resolved')
    list_filter = ('detected_at', 'is_resolved', 'reason')
    search_fields = ('ip_address', 'reason')
    list_editable = ('is_resolved',)
    readonly_fields = ('detected_at',)
    
    actions = ['mark_as_resolved', 'block_selected_ips']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Mark selected IPs as resolved"
    
    def block_selected_ips(self, request, queryset):
        for suspicious in queryset:
            BlockedIP.objects.get_or_create(ip_address=suspicious.ip_address)
            suspicious.is_resolved = True
            suspicious.save()
        self.message_user(request, f"Blocked {queryset.count()} IPs")
    block_selected_ips.short_description = "Block selected IPs"