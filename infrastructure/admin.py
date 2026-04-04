from django.contrib import admin
from .models import Road, Pothole, RoadRepairHistory, TrafficLight, Infrastructure, InfrastructureType, ManagementZone


@admin.register(InfrastructureType)
class InfrastructureTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(ManagementZone)
class ManagementZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'manager']
    list_filter = ['district']
    search_fields = ['name', 'district']


@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'direction', 'status', 'quality_score', 'zone', 'built_year']
    list_filter = ['direction', 'status', 'quality_score', 'zone']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Pothole)
class PotholeAdmin(admin.ModelAdmin):
    list_display = ['road', 'severity', 'is_repaired', 'created_at']
    list_filter = ['severity', 'is_repaired']
    search_fields = ['road__name']


@admin.register(TrafficLight)
class TrafficLightAdmin(admin.ModelAdmin):
    list_display = ['code', 'location', 'status', 'installed_date', 'zone']
    list_filter = ['status', 'zone']
    search_fields = ['code', 'location']


@admin.register(Infrastructure)
class InfrastructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'status', 'zone', 'installed_date']
    list_filter = ['type', 'status', 'zone']
    search_fields = ['name', 'code']
