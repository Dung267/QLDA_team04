from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.management import call_command
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from .models import BackupRecord, BackupConfig, RestoreRecord


@login_required
@require_http_methods(["GET"])
def list_backups(request):
    """
    Danh sÃ¡ch backup vá»›i thá»‘ng kÃª
    - Hiá»ƒn thá»‹ táº¥t cáº£ backup records
    - TÃ­nh toÃ¡n thá»‘ng kÃª (total, success, failed, running)
    - Hiá»ƒn thá»‹ cáº¥u hÃ¬nh backup hiá»‡n táº¡i
    - PhÃ¢n trang (10 items/page)
    """
    # Get all backups with related data
    backups = BackupRecord.objects.select_related('created_by').prefetch_related('restores').order_by('-started_at')
    
    # Pagination
    paginator = Paginator(backups, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_backups = BackupRecord.objects.count()
    success_count = BackupRecord.objects.filter(status='success').count()
    failed_count = BackupRecord.objects.filter(status='failed').count()
    running_count = BackupRecord.objects.filter(status='running').count()
    
    # Total size calculation
    total_size_data = BackupRecord.objects.aggregate(total=Sum('file_size_mb'))
    total_size = total_size_data['total'] or 0
    
    # Get backup config (create if not exists)
    backup_config, created = BackupConfig.objects.get_or_create()
    
    context = {
        'backups': page_obj,
        'page_obj': page_obj,
        'total_backups': total_backups,
        'success_count': success_count,
        'failed_count': failed_count,
        'running_count': running_count,
        'total_size_mb': total_size,
        'backup_config': backup_config,
    }
    return render(request, 'backup/list.html', context)


@staff_member_required
@require_http_methods(["POST"])
def create_backup(request):
    """
    Táº¡o backup má»›i
    - Chá»n loáº¡i backup (full, incremental, differential)
    - Táº¡o BackupRecord vá»›i status='running'
    - Thá»±c hiá»‡n backup (simulate hoáº·c Celery task)
    - LÆ°u file_size_mb, file_path
    - Cáº­p nháº­t cáº¥u hÃ¬nh nÃ©n/mÃ£ hÃ³a tá»« BackupConfig
    """
    backup_type = request.POST.get('backup_type', 'full')
    
    if backup_type not in ['full', 'incremental', 'differential']:
        messages.error(request, 'Loáº¡i backup khÃ´ng há»£p lá»‡!')
        return redirect('backup:list')
    
    try:
        # Get config
        config = BackupConfig.objects.first() or BackupConfig.objects.create()
        
        # Generate file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'backup_{backup_type}_{timestamp}.zip'
        
        # Create backup record
        backup = BackupRecord.objects.create(
            backup_type=backup_type,
            file_name=file_name,
            status='running',
            created_by=request.user,
            is_compressed=config.compress,
            is_encrypted=config.encrypt,
        )
        
        try:
            # Thá»±c hiá»‡n backup
            # ÄÃ¢y lÃ  nÆ¡i gá»i Celery task hoáº·c subprocess Ä‘á»ƒ backup thá»±c táº¿
            # For now, simulating with sample data
            
            # Simulate backup execution
            # In production, nÃ y sáº½ lÃ  Celery task
            backup_result = perform_backup(backup, config)
            
            if backup_result['success']:
                backup.status = 'success'
                backup.file_size_mb = backup_result['size_mb']
                backup.file_path = backup_result['file_path']
                backup.completed_at = timezone.now()
                backup.save()
                
                # Delete excess backups if exceeds max_backups
                delete_excess_backups(config.max_backups)
                
                messages.success(
                    request, 
                    f'Backup "{backup.file_name}" Ä‘Ã£ Ä‘Æ°á»£c táº¡o thÃ nh cÃ´ng! '
                    f'({backup_result["size_mb"]:.2f} MB)'
                )
            else:
                raise Exception(backup_result.get('error', 'Lá»—i khÃ´ng xÃ¡c Ä‘á»‹nh'))
                
        except Exception as e:
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.completed_at = timezone.now()
            backup.save()
            messages.error(request, f'Lá»—i táº¡o backup: {str(e)}')
        
    except Exception as e:
        messages.error(request, f'Lá»—i: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def restore_backup(request, pk):
    """
    KhÃ´i phá»¥c tá»« backup
    - Kiá»ƒm tra backup tá»“n táº¡i vÃ  status='success'
    - YÃªu cáº§u confirm tá»« user
    - Táº¡o RestoreRecord
    - Thá»±c hiá»‡n restore (Celery task)
    - Cáº­p nháº­t status restore
    - Ghi log & gá»­i notification
    """
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    # Verify backup is successful
    if backup.status != 'success':
        messages.error(request, 'Chá»‰ cÃ³ thá»ƒ khÃ´i phá»¥c tá»« backup thÃ nh cÃ´ng!')
        return redirect('backup:list')
    
    # Verify file exists
    if not backup.file_path or not os.path.exists(backup.file_path):
        messages.error(request, 'File backup khÃ´ng tá»“n táº¡i!')
        return redirect('backup:list')
    
    try:
        # Get note from request
        note = request.POST.get('note', f'KhÃ´i phá»¥c bá»Ÿi {request.user.username}')
        
        # Create restore record
        restore = RestoreRecord.objects.create(
            backup=backup,
            restored_by=request.user,
            status='running',
            note=note
        )
        
        try:
            # Thá»±c hiá»‡n restore
            # ÄÃ¢y lÃ  nÆ¡i gá»i Celery task Ä‘á»ƒ restore thá»±c táº¿
            restore_result = perform_restore(backup, restore)
            
            if restore_result['success']:
                restore.status = 'success'
                restore.note = f'{note}\nâœ“ Restore thÃ nh cÃ´ng'
                restore.save()
                
                messages.success(
                    request, 
                    f'Dá»¯ liá»‡u Ä‘Ã£ Ä‘Æ°á»£c khÃ´i phá»¥c tá»« backup "{backup.file_name}"!'
                )
            else:
                raise Exception(restore_result.get('error', 'Lá»—i restore khÃ´ng xÃ¡c Ä‘á»‹nh'))
                
        except Exception as e:
            restore.status = 'failed'
            restore.note = f'{note}\nâœ— Lá»—i: {str(e)}'
            restore.save()
            messages.error(request, f'Lá»—i khÃ´i phá»¥c: {str(e)}')
        
    except Exception as e:
        messages.error(request, f'Lá»—i: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def delete_backup(request, pk):
    """
    XÃ³a backup
    - Kiá»ƒm tra backup tá»“n táº¡i
    - XÃ³a file khá»i filesystem
    - XÃ³a RestoreRecord liÃªn quan (CASCADE)
    - XÃ³a BackupRecord
    - Giáº£i phÃ³ng dung lÆ°á»£ng
    """
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    try:
        file_name = backup.file_name
        file_size = backup.file_size_mb
        
        # Delete file from filesystem
        if backup.file_path and os.path.exists(backup.file_path):
            try:
                os.remove(backup.file_path)
            except OSError as e:
                messages.warning(request, f'KhÃ´ng thá»ƒ xÃ³a file: {str(e)}')
        
        # Delete record (RestoreRecord sáº½ cascade delete)
        backup.delete()
        
        messages.success(
            request, 
            f'Backup "{file_name}" Ä‘Ã£ Ä‘Æ°á»£c xÃ³a! '
            f'({file_size:.2f} MB Ä‘Ã£ Ä‘Æ°á»£c giáº£i phÃ³ng)'
        )
        
    except Exception as e:
        messages.error(request, f'Lá»—i xÃ³a backup: {str(e)}')
    
    return redirect('backup:list')


@login_required
@require_http_methods(["GET"])
def download_backup(request, pk):
    """
    Download backup file
    - Kiá»ƒm tra permission (chá»‰ staff Ä‘Æ°á»£c download)
    - Kiá»ƒm tra file tá»“n táº¡i
    - Stream file vá»›i proper headers
    - Ghi log download
    """
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    # Check permissions
    if not request.user.is_staff:
        messages.error(request, 'Báº¡n khÃ´ng cÃ³ quyá»n download backup!')
        return redirect('backup:list')
    
    # Check backup status
    if backup.status != 'success':
        messages.error(request, 'Chá»‰ cÃ³ thá»ƒ download backup thÃ nh cÃ´ng!')
        return redirect('backup:list')
    
    # Check file exists
    if not backup.file_path or not os.path.exists(backup.file_path):
        messages.error(request, 'File backup khÃ´ng tá»“n táº¡i!')
        return redirect('backup:list')
    
    try:
        # Return file
        response = FileResponse(open(backup.file_path, 'rb'))
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{backup.file_name}"'
        response['Content-Length'] = os.path.getsize(backup.file_path)
        
        # Log download
        # CÃ³ thá»ƒ thÃªm audit log á»Ÿ Ä‘Ã¢y
        
        return response
        
    except Exception as e:
        messages.error(request, f'Lá»—i download: {str(e)}')
        return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def configure_backup(request):
    """
    Cáº¥u hÃ¬nh backup
    - Cáº­p nháº­t BackupConfig tá»« form data
    - Validate cÃ¡c field (frequency, max_backups, time_of_day)
    - LÆ°u vÃ o database
    - Trigger Celery beat schedule update (náº¿u cáº§n)
    """
    try:
        # Get or create config
        config, created = BackupConfig.objects.get_or_create()
        
        # Parse boolean fields
        is_auto = request.POST.get('is_auto') == 'on'
        include_media = request.POST.get('include_media') == 'on'
        compress = request.POST.get('compress') == 'on'
        encrypt = request.POST.get('encrypt') == 'on'
        upload_to_cloud = request.POST.get('upload_to_cloud') == 'on'
        
        # Get other fields
        frequency = request.POST.get('frequency', 'manual')
        time_of_day = request.POST.get('time_of_day')
        max_backups = request.POST.get('max_backups', '10')
        
        # Validate frequency
        valid_frequencies = ['manual', 'daily', 'weekly', 'monthly']
        if frequency not in valid_frequencies:
            messages.error(request, f'Táº§n suáº¥t khÃ´ng há»£p lá»‡! Pháº£i lÃ : {", ".join(valid_frequencies)}')
            return redirect('backup:list')
        
        # Validate max_backups
        try:
            max_backups = int(max_backups)
            if max_backups < 1 or max_backups > 100:
                messages.error(request, 'Sá»‘ lÆ°á»£ng backup tá»‘i Ä‘a pháº£i tá»« 1-100!')
                return redirect('backup:list')
        except ValueError:
            messages.error(request, 'Sá»‘ lÆ°á»£ng backup pháº£i lÃ  sá»‘!')
            return redirect('backup:list')
        
        # Update config
        config.is_auto = is_auto
        config.frequency = frequency
        config.max_backups = max_backups
        config.include_media = include_media
        config.compress = compress
        config.encrypt = encrypt
        config.upload_to_cloud = upload_to_cloud
        
        # Update time_of_day if provided
        if time_of_day:
            config.time_of_day = time_of_day
        
        config.save()
        
        # Build message
        msg_parts = []
        if is_auto:
            msg_parts.append(f'Tá»± Ä‘á»™ng {frequency}')
            if time_of_day:
                msg_parts.append(f'lÃºc {time_of_day}')
        else:
            msg_parts.append('Thá»§ cÃ´ng')
        
        if compress:
            msg_parts.append('nÃ©n file')
        if encrypt:
            msg_parts.append('mÃ£ hÃ³a')
        if upload_to_cloud:
            msg_parts.append('upload cloud')
        
        message = 'Cáº¥u hÃ¬nh backup: ' + ', '.join(msg_parts)
        messages.success(request, message)
        
    except Exception as e:
        messages.error(request, f'Lá»—i cáº¥u hÃ¬nh: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["GET"])
def backup_stats(request):
    """
    Thá»‘ng kÃª chi tiáº¿t vá» backup
    - TÃ­nh toÃ¡n various metrics
    - Hiá»ƒn thá»‹ backup trend (7 ngÃ y gáº§n Ä‘Ã¢y)
    - Hiá»ƒn thá»‹ storage usage
    - Restore success rate
    """
    # Overall stats
    total_count = BackupRecord.objects.count()
    success_count = BackupRecord.objects.filter(status='success').count()
    failed_count = BackupRecord.objects.filter(status='failed').count()
    running_count = BackupRecord.objects.filter(status='running').count()
    
    # Size stats
    total_size = BackupRecord.objects.aggregate(total=Sum('file_size_mb'))['total'] or 0
    success_size = BackupRecord.objects.filter(status='success').aggregate(total=Sum('file_size_mb'))['total'] or 0
    
    # Average size
    success_backups = BackupRecord.objects.filter(status='success').count()
    avg_size = success_size / success_backups if success_backups > 0 else 0
    
    # Success rate
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    # Last 7 days backups
    week_ago = timezone.now() - timedelta(days=7)
    recent_backups = BackupRecord.objects.filter(
        started_at__gte=week_ago
    ).order_by('-started_at')[:10]
    
    # Backup by type
    backup_by_type = BackupRecord.objects.values('backup_type').annotate(
        count=Count('id'),
        total_size=Sum('file_size_mb')
    )
    
    # Restore stats
    restore_count = RestoreRecord.objects.count()
    successful_restores = RestoreRecord.objects.filter(status='success').count()
    restore_success_rate = (successful_restores / restore_count * 100) if restore_count > 0 else 0
    
    # Most restored backup
    most_restored = RestoreRecord.objects.values('backup').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    # Build stats dictionary
    stats = {
        'total_count': total_count,
        'success_count': success_count,
        'failed_count': failed_count,
        'running_count': running_count,
        'success_rate': f'{success_rate:.1f}%',
        'total_size_mb': f'{total_size:.2f}',
        'avg_size_mb': f'{avg_size:.2f}',
        'restore_count': restore_count,
        'successful_restores': successful_restores,
        'restore_success_rate': f'{restore_success_rate:.1f}%',
    }
    
    context = {
        'stats': stats,
        'recent_backups': recent_backups,
        'backup_by_type': backup_by_type,
    }
    
    return render(request, 'backup/stats.html', context)


# ============================================================================
# Helper Functions - Thá»±c táº¿ backup/restore operations
# ============================================================================

def perform_backup(backup, config):
    try:
        backups_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
        os.makedirs(backups_dir, exist_ok=True)

        file_path = os.path.join(backups_dir, backup.file_name)
        dump_name = backup.file_name.replace('.zip', '.json')

        with tempfile.TemporaryDirectory(prefix='urban_backup_') as tmp_dir:
            dump_file = os.path.join(tmp_dir, dump_name)
            with open(dump_file, 'w', encoding='utf-8') as dump_handle:
                call_command(
                    'dumpdata',
                    '--natural-foreign',
                    '--natural-primary',
                    '--exclude',
                    'contenttypes',
                    '--exclude',
                    'auth.permission',
                    stdout=dump_handle,
                    verbosity=0,
                )

            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(dump_file, arcname=dump_name)
                if config.include_media and os.path.isdir(settings.MEDIA_ROOT):
                    backup_root = os.path.abspath(backups_dir)
                    for root, _, files in os.walk(settings.MEDIA_ROOT):
                        if os.path.abspath(root).startswith(backup_root):
                            continue
                        for item in files:
                            full_path = os.path.join(root, item)
                            arcname = os.path.join(
                                'media',
                                os.path.relpath(full_path, settings.MEDIA_ROOT),
                            )
                            zf.write(full_path, arcname=arcname)

        if config.encrypt:
            backup.is_encrypted = False
            backup.error_message = 'Encryption skipped: no encryption key/backend configured.'
            backup.save(update_fields=['is_encrypted', 'error_message'])

        if config.upload_to_cloud:
            backup.error_message = (backup.error_message + '\n' if backup.error_message else '') + (
                'Cloud upload skipped: no storage backend configured.'
            )
            backup.save(update_fields=['error_message'])

        return {
            'success': True,
            'size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'file_path': file_path,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def perform_restore(backup, restore):
    try:
        if not os.path.exists(backup.file_path):
            raise Exception('File backup khong ton tai')

        with tempfile.TemporaryDirectory(prefix='urban_restore_') as extract_dir:
            with zipfile.ZipFile(backup.file_path, 'r') as zf:
                zf.extractall(extract_dir)

            dump_files = []
            for root, _, files in os.walk(extract_dir):
                for item in files:
                    if item.endswith('.json'):
                        dump_files.append(os.path.join(root, item))

            if not dump_files:
                raise Exception('Khong tim thay file dump JSON trong backup')

            call_command('loaddata', dump_files[0], verbosity=0)

            media_dir = os.path.join(extract_dir, 'media')
            if os.path.isdir(media_dir):
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                for item in os.listdir(media_dir):
                    src = os.path.join(media_dir, item)
                    dst = os.path.join(settings.MEDIA_ROOT, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)

        return {'success': True}
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def delete_excess_backups(max_backups):
    """
    XÃ³a backup cÅ© náº¿u vÆ°á»£t quÃ¡ max_backups limit
    - Query backup success_backups
    - Order by started_at descending
    - XÃ³a tá»« vá»‹ trÃ­ max_backups trá»Ÿ Ä‘i
    """
    try:
        excess_backups = BackupRecord.objects.filter(
            status='success'
        ).order_by('-started_at')[max_backups:]
        
        for backup in excess_backups:
            # Delete file
            if backup.file_path and os.path.exists(backup.file_path):
                try:
                    os.remove(backup.file_path)
                except OSError:
                    pass
            # Delete record
            backup.delete()
    except Exception as e:
        # Log error but don't raise
        print(f'Error deleting excess backups: {str(e)}')
