from django.contrib import admin
from .models import BackupRecord, BackupSchedule, RestoreRecord


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'backup_type', 'data_type', 'status', 'file_size_mb', 'started_at']
    list_filter = ['backup_type', 'status', 'data_type']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(BackupSchedule)
class BackupScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'backup_type', 'frequency', 'scheduled_time', 'is_active']
    list_filter = ['is_active', 'frequency']
