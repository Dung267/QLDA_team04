from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class BackupConfig(models.Model):
    FREQ_CHOICES = [('manual','Thủ công'),('daily','Hàng ngày'),('weekly','Hàng tuần'),('monthly','Hàng tháng')]
    is_auto = models.BooleanField('Tự động', default=False)
    frequency = models.CharField('Tần suất', max_length=10, choices=FREQ_CHOICES, default='manual')
    time_of_day = models.TimeField('Giờ backup', null=True, blank=True)
    max_backups = models.IntegerField('Số lượng backup tối đa', default=10)
    include_media = models.BooleanField('Bao gồm media', default=True)
    compress = models.BooleanField('Nén file', default=True)
    encrypt = models.BooleanField('Mã hóa', default=False)
    upload_to_cloud = models.BooleanField('Upload lên cloud', default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Cấu hình backup'

class BackupRecord(models.Model):
    STATUS_CHOICES = [('running','Đang chạy'),('success','Thành công'),('failed','Thất bại'),('paused','Tạm dừng')]
    backup_type = models.CharField('Loại', max_length=20, default='full')
    file_name = models.CharField('Tên file', max_length=255)
    file_path = models.CharField('Đường dẫn', max_length=500, blank=True)
    file_size_mb = models.FloatField('Kích thước (MB)', default=0)
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='running')
    is_encrypted = models.BooleanField('Đã mã hóa', default=False)
    is_compressed = models.BooleanField('Đã nén', default=False)
    error_message = models.TextField('Lỗi', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = 'Bản backup'
        verbose_name_plural = 'Bản backup'
        ordering = ['-started_at']
    def __str__(self): return f"{self.file_name} ({self.get_status_display()})"

class RestoreRecord(models.Model):
    backup = models.ForeignKey(BackupRecord, on_delete=models.CASCADE, related_name='restores')
    restored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, default='success')
    note = models.TextField(blank=True)
    restored_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Lịch sử restore'
        ordering = ['-restored_at']
