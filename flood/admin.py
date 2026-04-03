from django.contrib import admin
from .models import FloodAlert, DisasterAlert, WeatherStation


@admin.register(FloodAlert)
class FloodAlertAdmin(admin.ModelAdmin):
    list_display = ['area_name', 'district', 'level', 'water_level_cm', 'is_active', 'created_at']
    list_filter = ['level', 'is_active', 'district']
    search_fields = ['area_name', 'district']


@admin.register(DisasterAlert)
class DisasterAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'disaster_type', 'is_active', 'created_at']
    list_filter = ['disaster_type', 'is_active']


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active']

