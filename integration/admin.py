from django.contrib import admin
from .models import APIIntegration, APILog


@admin.register(APIIntegration)
class APIIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'status', 'last_sync']
    list_filter = ['status']


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'method', 'endpoint', 'response_status', 'is_success', 'created_at']
    list_filter = ['is_success', 'method']
    readonly_fields = ['created_at']
