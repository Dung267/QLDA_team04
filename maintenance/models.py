from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MaintenanceRequest(models.Model):
    TYPE_CHOICES = [
        ('road_damage', 'Hư hỏng đường'),
        ('pothole', 'Ổ gà'),
        ('traffic_light', 'Đèn giao thông'),
        ('drainage', 'Thoát nước'),
        ('bridge', 'Cầu cống'),
        ('sign', 'Biển báo'),
        ('lighting', 'Chiếu sáng'),
        ('other', 'Khác'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Chờ tiếp nhận'),
        ('received', 'Đã tiếp nhận'),
        ('assigned', 'Đã phân công'),
        ('in_progress', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ]

    title = models.CharField('Tiêu đề', max_length=300)
    description = models.TextField('Mô tả sự cố')
    incident_type = models.CharField('Loại sự cố', max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField('Mức độ ưu tiên', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='pending')
    infrastructure = models.ForeignKey(
        'infrastructure.Infrastructure', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='maintenance_requests', verbose_name='Hạ tầng liên quan'
    )
    road = models.ForeignKey(
        'infrastructure.Road', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='maintenance_requests', verbose_name='Tuyến đường'
    )
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    address = models.CharField('Địa chỉ', max_length=300, blank=True)
    is_anonymous = models.BooleanField('Phản ánh ẩn danh', default=False)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                     related_name='reported_requests', verbose_name='Người báo cáo')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='assigned_requests', verbose_name='Người xử lý')
    assigned_at = models.DateTimeField('Thời gian phân công', null=True, blank=True)
    started_at = models.DateTimeField('Thời gian bắt đầu', null=True, blank=True)
    completed_at = models.DateTimeField('Thời gian hoàn thành', null=True, blank=True)
    estimated_cost = models.DecimalField('Chi phí dự kiến (VNĐ)', max_digits=15, decimal_places=0, default=0)
    actual_cost = models.DecimalField('Chi phí thực tế (VNĐ)', max_digits=15, decimal_places=0, default=0)
    rejection_reason = models.TextField('Lý do từ chối', blank=True)
    processing_note = models.TextField('Ghi chú xử lý', blank=True)
    is_duplicate = models.BooleanField('Phản ánh trùng', default=False)
    duplicate_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='duplicates', verbose_name='Trùng với')
    citizen_rating = models.IntegerField('Đánh giá của người dân (1-5)', null=True, blank=True)
    citizen_feedback = models.TextField('Phản hồi người dân', blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật', auto_now=True)

    class Meta:
        verbose_name = 'Yêu cầu bảo trì'
        verbose_name_plural = 'Yêu cầu bảo trì'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def processing_time_hours(self):
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds() / 3600, 1)
        return None


class MaintenancePhoto(models.Model):
    PHASE_CHOICES = [('before', 'Trước'), ('after', 'Sau'), ('during', 'Trong quá trình')]
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField('Ảnh', upload_to='maintenance/photos/')
    phase = models.CharField('Giai đoạn', max_length=10, choices=PHASE_CHOICES)
    caption = models.CharField('Chú thích', max_length=200, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ảnh bảo trì'
        verbose_name_plural = 'Ảnh bảo trì'


class MaintenanceVideo(models.Model):
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField('Video', upload_to='maintenance/videos/')
    caption = models.CharField('Chú thích', max_length=200, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Video bảo trì'


class MaintenanceComment(models.Model):
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField('Nội dung')
    is_internal = models.BooleanField('Nội bộ', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author} - {self.created_at.strftime('%d/%m/%Y')}"


class MaintenanceSchedule(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Kế hoạch'),
        ('confirmed', 'Đã xác nhận'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('postponed', 'Hoãn'),
    ]

    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    infrastructure = models.ForeignKey('infrastructure.Infrastructure', on_delete=models.CASCADE,
                                        null=True, blank=True, related_name='schedules')
    road = models.ForeignKey('infrastructure.Road', on_delete=models.CASCADE,
                              null=True, blank=True, related_name='schedules')
    scheduled_date = models.DateField('Ngày lên kế hoạch')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='planned')
    assigned_to = models.ManyToManyField(User, blank=True, related_name='maintenance_schedules',
                                          verbose_name='Nhân viên phụ trách')
    estimated_cost = models.DecimalField('Chi phí dự kiến', max_digits=15, decimal_places=0, default=0)
    is_periodic = models.BooleanField('Định kỳ', default=False)
    period_days = models.IntegerField('Chu kỳ (ngày)', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lịch bảo trì'
        verbose_name_plural = 'Lịch bảo trì'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"