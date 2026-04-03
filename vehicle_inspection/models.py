from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class InspectionCenter(models.Model):
    name = models.CharField('Tên trung tâm', max_length=200)
    code = models.CharField('Mã', max_length=20, unique=True)
    address = models.TextField('Địa chỉ')
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Trung tâm đăng kiểm'

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    VEHICLE_TYPES = [('car','Ô tô'),('motorbike','Xe máy'),('truck','Xe tải'),('bus','Xe khách'),('other','Khác')]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    plate_number = models.CharField('Biển số', max_length=15, unique=True)
    vehicle_type = models.CharField('Loại xe', max_length=10, choices=VEHICLE_TYPES)
    brand = models.CharField('Hãng', max_length=50, blank=True)
    model = models.CharField('Mẫu', max_length=50, blank=True)
    year = models.IntegerField('Năm sản xuất', null=True, blank=True)
    color = models.CharField('Màu', max_length=30, blank=True)
    engine_number = models.CharField('Số máy', max_length=50, blank=True)
    chassis_number = models.CharField('Số khung', max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Phương tiện'

    def __str__(self):
        return f"{self.plate_number} - {self.get_vehicle_type_display()}"


class Inspection(models.Model):
    STATUS_CHOICES = [
        ('pending','Chờ đăng kiểm'),('in_progress','Đang kiểm'),
        ('passed','Đạt'),('failed','Không đạt'),('cancelled','Hủy'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections')
    center = models.ForeignKey(InspectionCenter, on_delete=models.CASCADE, related_name='inspections')
    scheduled_date = models.DateField('Ngày hẹn')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_inspections')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='pending')
    defects = models.TextField('Lỗi phát hiện', blank=True)
    repair_required = models.TextField('Yêu cầu sửa chữa', blank=True)
    result_notes = models.TextField('Ghi chú kết quả', blank=True)
    certificate_number = models.CharField('Số giấy CN', max_length=50, blank=True)
    valid_until = models.DateField('Hiệu lực đến', null=True, blank=True)
    fee_paid = models.DecimalField('Phí đã thanh toán', max_digits=10, decimal_places=0, default=0)
    is_renewed = models.BooleanField('Đã gia hạn', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đăng kiểm'
        verbose_name_plural = 'Đăng kiểm'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.scheduled_date}"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.valid_until:
            return self.valid_until < timezone.now().date()
        return False
