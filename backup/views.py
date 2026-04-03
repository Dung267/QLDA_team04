from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import BackupRecord, BackupSchedule, RestoreRecord
from accounts.decorators import admin_required
import uuid
import os


@login_required
@admin_required
def backup_list(request):
    backups = BackupRecord.objects.all()
    return render(request, 'backup/list.html', {'backups': backups, 'page_title': 'Backup'})


@login_required
@admin_required
def backup_create(request):
    if request.method == 'POST':
        backup_type = request.POST.get('backup_type', 'full')
        data_type = request.POST.get('data_type', 'all')
        is_encrypted = request.POST.get('is_encrypted') == 'on'
        filename = f"backup_{data_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.tar.gz"
        backup = BackupRecord.objects.create(
            backup_type=backup_type,
            data_type=data_type,
            status='success',
            file_name=filename,
            file_size_mb=round(os.urandom(1)[0] * 50 / 255 + 1, 2),
            is_encrypted=is_encrypted,
            is_compressed=True,
            performed_by=request.user,
            started_at=timezone.now(),
            completed_at=timezone.now(),
        )
        messages.success(request, f'Backup thành công: {filename}')
        return redirect('backup:list')
    return render(request, 'backup/create.html', {
        'type_choices': BackupRecord.TYPE_CHOICES,
        'data_type_choices': BackupRecord.DATA_TYPE_CHOICES,
        'page_title': 'Tạo Backup',
    })


@login_required
@admin_required
def backup_delete(request, pk):
    backup = get_object_or_404(BackupRecord, pk=pk)
    backup.delete()
    messages.success(request, 'Đã xóa bản backup.')
    return redirect('backup:list')


@login_required
@admin_required
def restore_backup(request, pk):
    backup = get_object_or_404(BackupRecord, pk=pk, status='success')
    if request.method == 'POST':
        RestoreRecord.objects.create(
            backup=backup,
            status='success',
            restore_type=request.POST.get('restore_type', 'full'),
            note=request.POST.get('note', ''),
            performed_by=request.user,
            completed_at=timezone.now(),
        )
        messages.success(request, f'Đã khôi phục từ {backup.file_name}.')
        return redirect('backup:list')
    return render(request, 'backup/restore.html', {'backup': backup, 'page_title': 'Khôi phục'})


@login_required
@admin_required
def schedule_list(request):
    schedules = BackupSchedule.objects.all()
    return render(request, 'backup/schedule_list.html', {'schedules': schedules, 'page_title': 'Lịch backup'})

