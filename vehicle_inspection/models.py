from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator

User = get_user_model()


class InspectionCenter(models.Model):
    """Trung tâm đăng kiểm xe cơ giới"""
    name = models.CharField('Tên trung tâm', max_length=200, unique=True)
    address = models.TextField('Địa chỉ')
    phone = models.CharField('Số điện thoại', max_length=15, blank=True)
    is_active = models.BooleanField('Hoạt động', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trung tâm đăng kiểm'
        verbose_name_plural = 'Trung tâm đăng kiểm'
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Phương tiện cơ giới"""
    TYPE_CHOICES = [
        ('car', 'Ô tô'),
        ('motorcycle', 'Xe máy'),
        ('truck', 'Xe tải'),
        ('bus', 'Xe buýt'),
        ('other', 'Khác')
    ]
    danang_plate_validator = RegexValidator(
        # Biểu thức này chấp nhận: 43A-12345, 43A-123.45, 43B1-12345
        regex=r'^43[A-Z0-9]{1,2}-?\d{3}\.?\d{2}$|^43[A-Z0-9]{1,2}-?\d{4}$',
        message='Biển số không hợp lệ. Vui lòng nhập biển số Đà Nẵng, ví dụ: 43A-12345 hoặc 43A-123.45',
        code='invalid_license_plate'
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name='Chủ xe')
    
    # 2. Gắn validator vào trường license_plate
    license_plate = models.CharField(
        'Biển số xe', 
        max_length=20, 
        unique=True, 
        db_index=True,
        validators=[danang_plate_validator], # <-- Thêm dòng này
        help_text="Ví dụ: 43A-12345"
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name='Chủ xe')
    vehicle_type = models.CharField('Loại xe', max_length=15, choices=TYPE_CHOICES)
    brand = models.CharField('Hãng xe', max_length=100, blank=True)
    model = models.CharField('Model', max_length=100, blank=True)
    color = models.CharField('Màu sắc', max_length=50, blank=True)
    year = models.IntegerField('Năm sản xuất', null=True, blank=True)
    chassis_number = models.CharField('Số khung', max_length=50, blank=True)
    engine_number = models.CharField('Số máy', max_length=50, blank=True)
    is_active = models.BooleanField('Hoạt động', default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Phương tiện'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['license_plate']),
        ]

    def __str__(self):
        return f"{self.license_plate} ({self.get_vehicle_type_display()})"

    @property
    def inspection_expiry_date(self):
        """Ngày hết hạn đăng kiểm gần đây nhất"""
        latest = self.inspections.filter(
            valid_until__isnull=False,
            status='passed'
        ).order_by('-valid_until').first()
        return latest.valid_until if latest else None

    @property
    def days_until_inspection_expiry(self):
        """Số ngày còn lại cho tới khi hết hạn"""
        expiry_date = self.inspection_expiry_date
        if not expiry_date:
            return None
        delta = expiry_date - timezone.localdate()
        return delta.days

    def get_expiry_status(self):
        """
        Trả về dict với thông tin trạng thái hạn đăng kiểm
        {
            'badge_class': str (CSS class),
            'badge_text': str,
            'days_left': int | None,
            'is_alert': bool,
            'note': str,
            'note_class': str
        }
        """
        expiry_date = self.inspection_expiry_date
        days_left = self.days_until_inspection_expiry

        if expiry_date is None:
            return {
                'badge_class': 'text-bg-secondary',
                'badge_text': 'Chưa có dữ liệu',
                'days_left': None,
                'is_alert': False,
                'note': 'Chưa có lịch sử đăng kiểm',
                'note_class': 'text-muted',
            }

        if days_left < 0:
            return {
                'badge_class': 'text-bg-danger',
                'badge_text': 'Hết hạn',
                'days_left': days_left,
                'is_alert': True,
                'note': f'Đã quá hạn {abs(days_left)} ngày',
                'note_class': 'text-danger',
            }

        if days_left <= 30:
            return {
                'badge_class': 'text-bg-warning text-dark',
                'badge_text': 'Sắp hết hạn',
                'days_left': days_left,
                'is_alert': True,
                'note': f'Còn {days_left} ngày',
                'note_class': 'text-muted',
            }

        return {
            'badge_class': 'text-bg-success',
            'badge_text': 'Hợp lệ',
            'days_left': days_left,
            'is_alert': False,
            'note': f'Còn {days_left} ngày',
            'note_class': 'text-muted',
        }


class Inspection(models.Model):
    """Lịch đăng kiểm xe cơ giới"""
    STATUS_CHOICES = [
        ('pending', 'Chờ kiểm tra'),
        ('in_progress', 'Đang kiểm tra'),
        ('passed', 'Đạt'),
        ('failed', 'Không đạt'),
        ('needs_repair', 'Cần sửa chữa'),
        ('cancelled', 'Đã hủy'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections', verbose_name='Phương tiện')
    center = models.ForeignKey(InspectionCenter, on_delete=models.SET_NULL, null=True, verbose_name='Trung tâm')
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections_conducted',
        verbose_name='Cán bộ kiểm tra'
    )
    scheduled_date = models.DateTimeField('Ngày hẹn')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True)

    technical_notes = models.TextField('Ghi chú kỹ thuật', blank=True)
    defects = models.TextField('Lỗi phát hiện', blank=True)
    repair_required = models.TextField('Yêu cầu sửa chữa', blank=True)
    repair_result = models.TextField('Kết quả sửa chữa', blank=True)

    fee = models.DecimalField('Phí đăng kiểm (VNĐ)', max_digits=10, decimal_places=0, default=0, null=True, blank=True)
    is_fee_paid = models.BooleanField('Đã thanh toán phí', default=False)

    certificate_number = models.CharField('Số giấy chứng nhận', max_length=50, blank=True, unique=True, null=True)
    valid_until = models.DateField('Hiệu lực đến', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lịch đăng kiểm'
        verbose_name_plural = 'Lịch đăng kiểm'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def can_be_cancelled(self):
        """Chỉ lịch ở trạng thái pending mới có thể hủy"""
        return self.status == 'pending'

    @property
    def can_be_updated(self):
        """Chỉ cán bộ mới có thể cập nhật kết quả"""
        return self.status in ['pending', 'in_progress']

    def get_status_badge_class(self):
        """Lấy CSS class badge cho trạng thái"""
        status_badge_map = {
            'pending': 'text-bg-warning text-dark',
            'in_progress': 'text-bg-info',
            'passed': 'text-bg-success',
            'failed': 'text-bg-danger',
            'needs_repair': 'text-bg-danger',
            'cancelled': 'text-bg-secondary',
        }
        return status_badge_map.get(self.status, 'text-bg-secondary')

    def get_status_label(self):
        """Lấy label thân thiện của trạng thái"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)