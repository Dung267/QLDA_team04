from django.contrib import admin
from .models import MaintenanceRequest, MaintenancePhoto, MaintenanceComment, MaintenanceSchedule


class MaintenancePhotoInline(admin.TabularInline):
    model = MaintenancePhoto
    extra = 0
    readonly_fields = ['uploaded_at']


class MaintenanceCommentInline(admin.TabularInline):
    model = MaintenanceComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'incident_type', 'priority', 'status', 'reported_by', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'incident_type']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MaintenancePhotoInline, MaintenanceCommentInline]
    date_hierarchy = 'created_at'


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_date', 'status', 'is_periodic']
    list_filter = ['status', 'is_periodic']
    search_fields = ['title']
    filter_horizontal = ['assigned_to']