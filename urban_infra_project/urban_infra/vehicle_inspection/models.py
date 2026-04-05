from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class InspectionCenter(models.Model):
    name = models.CharField('Tên trung tâm', max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'Trung tâm đăng kiểm'
    def __str__(self): return self.name

class Vehicle(models.Model):
    TYPE_CHOICES = [('car','Ô tô'),('motorcycle','Xe máy'),('truck','Xe tải'),('bus','Xe buýt'),('other','Khác')]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField('Biển số xe', max_length=20, unique=True)
    vehicle_type = models.CharField('Loại xe', max_length=15, choices=TYPE_CHOICES)
    brand = models.CharField('Hãng xe', max_length=100, blank=True)
    model = models.CharField('Model', max_length=100, blank=True)
    color = models.CharField('Màu sắc', max_length=50, blank=True)
    year = models.IntegerField('Năm sản xuất', null=True, blank=True)
    chassis_number = models.CharField('Số khung', max_length=50, blank=True)
    engine_number = models.CharField('Số máy', max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Phương tiện'
    def __str__(self): return f"{self.license_plate} ({self.get_vehicle_type_display()})"

class Inspection(models.Model):
    STATUS_CHOICES = [
        ('pending','Chờ kiểm tra'),('in_progress','Đang kiểm tra'),
        ('passed','Đạt'),('failed','Không đạt'),('needs_repair','Cần sửa chữa'),
        ('cancelled','Đã hủy'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections')
    center = models.ForeignKey(InspectionCenter, on_delete=models.SET_NULL, null=True)
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections_done')
    scheduled_date = models.DateTimeField('Lịch hẹn')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='pending')
    technical_notes = models.TextField('Ghi chú kỹ thuật', blank=True)
    defects = models.TextField('Lỗi phát hiện', blank=True)
    repair_required = models.TextField('Yêu cầu sửa chữa', blank=True)
    repair_result = models.TextField('Kết quả sửa chữa', blank=True)
    fee = models.DecimalField('Phí đăng kiểm (VNĐ)', max_digits=10, decimal_places=0, default=0)
    is_fee_paid = models.BooleanField('Đã thanh toán', default=False)
    certificate_number = models.CharField('Số giấy chứng nhận', max_length=50, blank=True)
    valid_until = models.DateField('Hiệu lực đến', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Lịch đăng kiểm'
        verbose_name_plural = 'Lịch đăng kiểm'
        ordering = ['-scheduled_date']
    def __str__(self): return f"{self.vehicle.license_plate} - {self.scheduled_date.strftime('%d/%m/%Y')}"
