from django.contrib import admin
from .models import Vehicle, Inspection, InspectionCenter

@admin.register(InspectionCenter)
class CenterAdmin(admin.ModelAdmin):
    list_display = ['name','address','phone','is_active']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate','vehicle_type','owner','brand','model','is_active']
    list_filter = ['vehicle_type','is_active']
    search_fields = ['license_plate','chassis_number']

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['vehicle','center','scheduled_date','status','is_fee_paid']
    list_filter = ['status','is_fee_paid']
