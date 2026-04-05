from django.contrib import admin
from .models import FloodAlert, DisasterUpdate

@admin.register(FloodAlert)
class FloodAlertAdmin(admin.ModelAdmin):
    list_display = ['title','level','area_name','is_active','created_at']
    list_filter = ['level','is_active']

@admin.register(DisasterUpdate)
class DisasterUpdateAdmin(admin.ModelAdmin):
    list_display = ['disaster_type','title','is_published','created_at']
    list_filter = ['disaster_type','is_published']
