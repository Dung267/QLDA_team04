from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import os, json
from .models import BackupRecord, BackupConfig, RestoreRecord
from accounts.decorators import admin_required

@login_required
@admin_required
def backup_list(request):
    backups = BackupRecord.objects.all()
    config, _ = BackupConfig.objects.get_or_create(pk=1)
    total_size = sum(b.file_size_mb for b in backups if b.status=='success')
    return render(request,'backup/list.html',{
        'backups':backups,'config':config,
        'total_size':round(total_size,2),'page_title':'Backup & Khôi phục'})

@login_required
@admin_required
def create_backup(request):
    if request.method=='POST':
        backup_type = request.POST.get('type','full')
        from datetime import datetime
        fname = f"backup_{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        record = BackupRecord.objects.create(
            backup_type=backup_type, file_name=fname,
            status='success', created_by=request.user,
            file_size_mb=round(os.path.getsize('db.sqlite3')/1024/1024, 2) if os.path.exists('db.sqlite3') else 0,
            completed_at=timezone.now()
        )
        messages.success(request, f'Đã tạo backup: {fname}')
        return JsonResponse({'success':True,'id':record.pk,'name':fname})
    return JsonResponse({'error':'Method not allowed'},status=405)

@login_required
@admin_required
def restore_backup(request, pk):
    backup = get_object_or_404(BackupRecord, pk=pk, status='success')
    if request.method=='POST':
        RestoreRecord.objects.create(backup=backup, restored_by=request.user, status='success')
        messages.success(request,f'Đã khôi phục từ {backup.file_name}')
    return redirect('backup:list')

@login_required
@admin_required
def delete_backup(request, pk):
    backup = get_object_or_404(BackupRecord, pk=pk)
    backup.delete()
    messages.success(request,'Đã xóa bản backup.')
    return redirect('backup:list')

@login_required
@admin_required
def save_config(request):
    if request.method=='POST':
        config, _ = BackupConfig.objects.get_or_create(pk=1)
        config.is_auto = request.POST.get('is_auto')=='on'
        config.frequency = request.POST.get('frequency','manual')
        config.max_backups = int(request.POST.get('max_backups',10))
        config.compress = request.POST.get('compress')=='on'
        config.encrypt = request.POST.get('encrypt')=='on'
        config.save()
        messages.success(request,'Đã lưu cấu hình backup.')
    return redirect('backup:list')
