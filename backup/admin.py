from django.contrib import admin
from .models import BackupRecord, RestoreRecord, BackupConfig

@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = ['file_name','backup_type','status','file_size_mb','created_by','started_at']
    list_filter = ['status','backup_type']
    readonly_fields = ['started_at','completed_at']

@admin.register(RestoreRecord)
class RestoreRecordAdmin(admin.ModelAdmin):
    list_display = ['backup','restored_by','status','restored_at']
    readonly_fields = ['restored_at']
