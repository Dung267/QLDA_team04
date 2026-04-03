from django.contrib import admin
from .models import Vehicle, Inspection, InspectionCenter


@admin.register(InspectionCenter)
class InspectionCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'address', 'is_active']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'vehicle_type', 'brand', 'model', 'owner']
    list_filter = ['vehicle_type']
    search_fields = ['plate_number', 'owner__username']

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'center', 'scheduled_date', 'status', 'valid_until']
    list_filter = ['status', 'center']
    search_fields = ['vehicle__plate_number']
