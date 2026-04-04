from django.contrib import admin
from .models import APIIntegration, WebhookLog

@admin.register(APIIntegration)
class APIIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name','endpoint','status','last_sync']
    list_filter = ['status']

@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['event_type','response_code','is_success','created_at']
    list_filter = ['is_success']
