from django.contrib import admin
from .models import RequestLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'timestamp', 'path')
    list_filter = ('timestamp',)
    search_fields = ('ip_address', 'path')