from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class BackupRecord(models.Model):
    TYPE_CHOICES = [('full','Toàn bộ'),('incremental','Tăng dần'),('differential','Chênh lệch')]
    STATUS_CHOICES = [('running','Đang chạy'),('success','Thành công'),('failed','Thất bại'),('paused','Tạm dừng')]
    DATA_TYPE_CHOICES = [('all','Tất cả'),('database','Database'),('media','Media'),('config','Cấu hình')]

    backup_type = models.CharField('Loại backup', max_length=15, choices=TYPE_CHOICES, default='full')
    data_type = models.CharField('Loại dữ liệu', max_length=10, choices=DATA_TYPE_CHOICES, default='all')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='running')
    file_name = models.CharField('Tên file', max_length=200)
    file_path = models.CharField('Đường dẫn', max_length=500, blank=True)
    file_size_mb = models.FloatField('Dung lượng (MB)', default=0)
    is_encrypted = models.BooleanField('Đã mã hóa', default=False)
    is_compressed = models.BooleanField('Đã nén', default=False)
    is_cloud = models.BooleanField('Trên cloud', default=False)
    checksum = models.CharField('Checksum', max_length=64, blank=True)
    error_message = models.TextField('Lỗi', blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField('Bắt đầu')
    completed_at = models.DateTimeField('Hoàn thành', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField('Hết hạn', null=True, blank=True)

    class Meta:
        verbose_name = 'Backup'
        verbose_name_plural = 'Backup'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.file_name} - {self.get_status_display()}"


class BackupSchedule(models.Model):
    FREQUENCY_CHOICES = [('daily','Hàng ngày'),('weekly','Hàng tuần'),('monthly','Hàng tháng')]
    name = models.CharField('Tên lịch', max_length=100)
    backup_type = models.CharField('Loại backup', max_length=15, choices=BackupRecord.TYPE_CHOICES)
    data_type = models.CharField('Loại dữ liệu', max_length=10, choices=BackupRecord.DATA_TYPE_CHOICES)
    frequency = models.CharField('Tần suất', max_length=10, choices=FREQUENCY_CHOICES)
    scheduled_time = models.TimeField('Giờ thực hiện')
    day_of_week = models.IntegerField('Ngày trong tuần (0-6)', null=True, blank=True)
    retain_count = models.IntegerField('Số bản giữ lại', default=7)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    is_encrypted = models.BooleanField('Mã hóa', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch backup'

    def __str__(self):
        return self.name


class RestoreRecord(models.Model):
    STATUS_CHOICES = [('running','Đang khôi phục'),('success','Thành công'),('failed','Thất bại')]
    backup = models.ForeignKey(BackupRecord, on_delete=models.CASCADE, related_name='restores')
    status = models.CharField('Trạng thái', max_length=10, choices=STATUS_CHOICES, default='running')
    restore_type = models.CharField('Loại', max_length=20, choices=[('full','Toàn bộ'),('partial','Một phần')], default='full')
    note = models.TextField('Ghi chú', blank=True)
    error_message = models.TextField('Lỗi', blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Lịch sử khôi phục'
        ordering = ['-started_at']
