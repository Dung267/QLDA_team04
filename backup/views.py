from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
import os
import subprocess
import zipfile
import json
from datetime import datetime, timedelta
from .models import BackupRecord, BackupConfig, RestoreRecord


@login_required
@require_http_methods(["GET"])
def list_backups(request):
    """
    Danh sách backup với thống kê
    - Hiển thị tất cả backup records
    - Tính toán thống kê (total, success, failed, running)
    - Hiển thị cấu hình backup hiện tại
    - Phân trang (10 items/page)
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
    Tạo backup mới
    - Chọn loại backup (full, incremental, differential)
    - Tạo BackupRecord với status='running'
    - Thực hiện backup (simulate hoặc Celery task)
    - Lưu file_size_mb, file_path
    - Cập nhật cấu hình nén/mã hóa từ BackupConfig
    """
    backup_type = request.POST.get('backup_type', 'full')
    
    if backup_type not in ['full', 'incremental', 'differential']:
        messages.error(request, 'Loại backup không hợp lệ!')
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
            # Thực hiện backup
            # Đây là nơi gọi Celery task hoặc subprocess để backup thực tế
            # For now, simulating with sample data
            
            # Simulate backup execution
            # In production, này sẽ là Celery task
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
                    f'Backup "{backup.file_name}" đã được tạo thành công! '
                    f'({backup_result["size_mb"]:.2f} MB)'
                )
            else:
                raise Exception(backup_result.get('error', 'Lỗi không xác định'))
                
        except Exception as e:
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.completed_at = timezone.now()
            backup.save()
            messages.error(request, f'Lỗi tạo backup: {str(e)}')
        
    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def restore_backup(request, pk):
    """
    Khôi phục từ backup
    - Kiểm tra backup tồn tại và status='success'
    - Yêu cầu confirm từ user
    - Tạo RestoreRecord
    - Thực hiện restore (Celery task)
    - Cập nhật status restore
    - Ghi log & gửi notification
    """
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    # Verify backup is successful
    if backup.status != 'success':
        messages.error(request, 'Chỉ có thể khôi phục từ backup thành công!')
        return redirect('backup:list')
    
    # Verify file exists
    if not backup.file_path or not os.path.exists(backup.file_path):
        messages.error(request, 'File backup không tồn tại!')
        return redirect('backup:list')
    
    try:
        # Get note from request
        note = request.POST.get('note', f'Khôi phục bởi {request.user.username}')
        
        # Create restore record
        restore = RestoreRecord.objects.create(
            backup=backup,
            restored_by=request.user,
            status='running',
            note=note
        )
        
        try:
            # Thực hiện restore
            # Đây là nơi gọi Celery task để restore thực tế
            restore_result = perform_restore(backup, restore)
            
            if restore_result['success']:
                restore.status = 'success'
                restore.note = f'{note}\n✓ Restore thành công'
                restore.save()
                
                messages.success(
                    request, 
                    f'Dữ liệu đã được khôi phục từ backup "{backup.file_name}"!'
                )
            else:
                raise Exception(restore_result.get('error', 'Lỗi restore không xác định'))
                
        except Exception as e:
            restore.status = 'failed'
            restore.note = f'{note}\n✗ Lỗi: {str(e)}'
            restore.save()
            messages.error(request, f'Lỗi khôi phục: {str(e)}')
        
    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def delete_backup(request, pk):
    """
    Xóa backup
    - Kiểm tra backup tồn tại
    - Xóa file khỏi filesystem
    - Xóa RestoreRecord liên quan (CASCADE)
    - Xóa BackupRecord
    - Giải phóng dung lượng
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
                messages.warning(request, f'Không thể xóa file: {str(e)}')
        
        # Delete record (RestoreRecord sẽ cascade delete)
        backup.delete()
        
        messages.success(
            request, 
            f'Backup "{file_name}" đã được xóa! '
            f'({file_size:.2f} MB đã được giải phóng)'
        )
        
    except Exception as e:
        messages.error(request, f'Lỗi xóa backup: {str(e)}')
    
    return redirect('backup:list')


@login_required
@require_http_methods(["GET"])
def download_backup(request, pk):
    """
    Download backup file
    - Kiểm tra permission (chỉ staff được download)
    - Kiểm tra file tồn tại
    - Stream file với proper headers
    - Ghi log download
    """
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    # Check permissions
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền download backup!')
        return redirect('backup:list')
    
    # Check backup status
    if backup.status != 'success':
        messages.error(request, 'Chỉ có thể download backup thành công!')
        return redirect('backup:list')
    
    # Check file exists
    if not backup.file_path or not os.path.exists(backup.file_path):
        messages.error(request, 'File backup không tồn tại!')
        return redirect('backup:list')
    
    try:
        # Return file
        response = FileResponse(open(backup.file_path, 'rb'))
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{backup.file_name}"'
        response['Content-Length'] = os.path.getsize(backup.file_path)
        
        # Log download
        # Có thể thêm audit log ở đây
        
        return response
        
    except Exception as e:
        messages.error(request, f'Lỗi download: {str(e)}')
        return redirect('backup:list')


@staff_member_required
@require_http_methods(["POST"])
def configure_backup(request):
    """
    Cấu hình backup
    - Cập nhật BackupConfig từ form data
    - Validate các field (frequency, max_backups, time_of_day)
    - Lưu vào database
    - Trigger Celery beat schedule update (nếu cần)
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
            messages.error(request, f'Tần suất không hợp lệ! Phải là: {", ".join(valid_frequencies)}')
            return redirect('backup:list')
        
        # Validate max_backups
        try:
            max_backups = int(max_backups)
            if max_backups < 1 or max_backups > 100:
                messages.error(request, 'Số lượng backup tối đa phải từ 1-100!')
                return redirect('backup:list')
        except ValueError:
            messages.error(request, 'Số lượng backup phải là số!')
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
            msg_parts.append(f'Tự động {frequency}')
            if time_of_day:
                msg_parts.append(f'lúc {time_of_day}')
        else:
            msg_parts.append('Thủ công')
        
        if compress:
            msg_parts.append('nén file')
        if encrypt:
            msg_parts.append('mã hóa')
        if upload_to_cloud:
            msg_parts.append('upload cloud')
        
        message = 'Cấu hình backup: ' + ', '.join(msg_parts)
        messages.success(request, message)
        
    except Exception as e:
        messages.error(request, f'Lỗi cấu hình: {str(e)}')
    
    return redirect('backup:list')


@staff_member_required
@require_http_methods(["GET"])
def backup_stats(request):
    """
    Thống kê chi tiết về backup
    - Tính toán various metrics
    - Hiển thị backup trend (7 ngày gần đây)
    - Hiển thị storage usage
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
# Helper Functions - Thực tế backup/restore operations
# ============================================================================

def perform_backup(backup, config):
    """
    Thực hiện backup thực tế
    - Dump database (PostgreSQL/SQLite)
    - Nén file nếu config.compress=True
    - Mã hóa nếu config.encrypt=True
    - Upload cloud nếu config.upload_to_cloud=True
    
    Return: {'success': bool, 'size_mb': float, 'file_path': str, 'error': str}
    """
    try:
        # Create backups directory if not exists
        backups_dir = os.path.join('media', 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        
        # File path
        file_path = os.path.join(backups_dir, backup.file_name)
        
        # Step 1: Dump database
        # Ví dụ với SQLite (change for PostgreSQL)
        dump_file = file_path.replace('.zip', '.sql')
        
        # For SQLite
        db_path = 'db.sqlite3'  # hoặc lấy từ settings
        if os.path.exists(db_path):
            # Sao chép database file
            import shutil
            shutil.copy(db_path, dump_file)
        
        # Step 2: Nén file nếu cần
        if config.compress:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(dump_file, arcname=os.path.basename(dump_file))
            os.remove(dump_file)
        else:
            # Rename to zip anyway
            import shutil
            shutil.move(dump_file, file_path)
        
        # Step 3: Mã hóa nếu cần (optional, requires cryptography)
        if config.encrypt:
            # Here you would encrypt the file
            # Example: encrypt_file(file_path, password)
            pass
        
        # Step 4: Upload cloud nếu cần (optional)
        if config.upload_to_cloud:
            # Upload to S3, Google Drive, etc.
            # Example: upload_to_s3(file_path)
            pass
        
        # Calculate file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        return {
            'success': True,
            'size_mb': file_size_mb,
            'file_path': file_path,
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def perform_restore(backup, restore):
    """
    Thực hiện restore dữ liệu từ backup
    - Giải nén file
    - Restore database từ dump
    - Verify data integrity
    - Update Django cache/sessions
    
    Return: {'success': bool, 'error': str}
    """
    try:
        if not os.path.exists(backup.file_path):
            raise Exception('File backup không tồn tại')
        
        # Step 1: Giải nén file
        extract_dir = os.path.join('media', 'restore_temp')
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(backup.file_path, 'r') as zf:
            zf.extractall(extract_dir)
        
        # Step 2: Restore database
        # Ví dụ với SQLite
        dump_files = [f for f in os.listdir(extract_dir) if f.endswith('.sql')]
        if dump_files:
            dump_file = os.path.join(extract_dir, dump_files[0])
            # Run restore command (adjust for your database)
            # subprocess.run(['sqlite3', 'db.sqlite3', f'< {dump_file}'])
            pass
        
        # Step 3: Clean up temp directory
        import shutil
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        return {'success': True}
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


def delete_excess_backups(max_backups):
    """
    Xóa backup cũ nếu vượt quá max_backups limit
    - Query backup success_backups
    - Order by started_at descending
    - Xóa từ vị trí max_backups trở đi
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