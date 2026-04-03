from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class InfrastructureType(models.Model):
    name = models.CharField('Tên loại', max_length=100)
    code = models.CharField('Mã', max_length=20, unique=True)
    description = models.TextField('Mô tả', blank=True)

    class Meta:
        verbose_name = 'Loại hạ tầng'
        verbose_name_plural = 'Loại hạ tầng'

    def __str__(self):
        return self.name


class ManagementZone(models.Model):
    name = models.CharField('Tên khu vực', max_length=100)
    district = models.CharField('Quận/Huyện', max_length=100)
    description = models.TextField('Mô tả', blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='managed_zones', verbose_name='Người quản lý')

    class Meta:
        verbose_name = 'Khu vực quản lý'
        verbose_name_plural = 'Khu vực quản lý'

    def __str__(self):
        return f"{self.name} - {self.district}"


class Road(models.Model):
    DIRECTION_CHOICES = [
        ('one_way', 'Một chiều'),
        ('two_way', 'Hai chiều'),
        ('railway', 'Đường sắt'),
    ]
    STATUS_CHOICES = [
        ('good', 'Tốt'),
        ('normal', 'Bình thường'),
        ('bad', 'Xấu'),
        ('critical', 'Nguy hiểm'),
        ('under_repair', 'Đang sửa chữa'),
    ]
    QUALITY_CHOICES = [(i, str(i)) for i in range(1, 6)]

    name = models.CharField('Tên đường', max_length=200)
    code = models.CharField('Mã đường', max_length=50, unique=True)
    direction = models.CharField('Loại đường', max_length=10, choices=DIRECTION_CHOICES, default='two_way')
    status = models.CharField('Tình trạng', max_length=20, choices=STATUS_CHOICES, default='good')
    quality_score = models.IntegerField('Điểm chất lượng (1-5)', choices=QUALITY_CHOICES, default=3)
    length_km = models.FloatField('Chiều dài (km)', default=0)
    width_m = models.FloatField('Chiều rộng (m)', default=0)
    lanes = models.IntegerField('Số làn', default=2)
    built_year = models.IntegerField('Năm xây dựng', null=True, blank=True)
    last_repaired = models.DateField('Sửa chữa lần cuối', null=True, blank=True)
    traffic_density = models.CharField('Mật độ giao thông', max_length=20,
                                        choices=[('low','Thấp'),('medium','Trung bình'),('high','Cao'),('very_high','Rất cao')],
                                        default='medium')
    zone = models.ForeignKey(ManagementZone, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='roads', verbose_name='Khu vực')
    managing_unit = models.CharField('Đơn vị quản lý', max_length=200, blank=True)
    start_point = models.CharField('Điểm đầu', max_length=200, blank=True)
    end_point = models.CharField('Điểm cuối', max_length=200, blank=True)
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_roads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tuyến đường'
        verbose_name_plural = 'Tuyến đường'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Pothole(models.Model):
    SEVERITY_CHOICES = [
        ('minor', 'Nhẹ'),
        ('moderate', 'Trung bình'),
        ('severe', 'Nghiêm trọng'),
        ('critical', 'Rất nghiêm trọng'),
    ]

    road = models.ForeignKey(Road, on_delete=models.CASCADE, related_name='potholes', verbose_name='Tuyến đường')
    description = models.TextField('Mô tả')
    severity = models.CharField('Mức độ', max_length=10, choices=SEVERITY_CHOICES, default='minor')
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    photo = models.ImageField('Ảnh', upload_to='potholes/', null=True, blank=True)
    is_repaired = models.BooleanField('Đã sửa', default=False)
    repaired_at = models.DateField('Ngày sửa', null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_potholes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ổ gà'
        verbose_name_plural = 'Ổ gà'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ổ gà - {self.road.name} ({self.get_severity_display()})"


class RoadRepairHistory(models.Model):
    road = models.ForeignKey(Road, on_delete=models.CASCADE, related_name='repair_history', verbose_name='Tuyến đường')
    repair_date = models.DateField('Ngày sửa chữa')
    description = models.TextField('Nội dung sửa chữa')
    cost = models.DecimalField('Chi phí (VNĐ)', max_digits=15, decimal_places=0, default=0)
    contractor = models.CharField('Đơn vị thi công', max_length=200, blank=True)
    photo_before = models.ImageField('Ảnh trước', upload_to='repairs/before/', null=True, blank=True)
    photo_after = models.ImageField('Ảnh sau', upload_to='repairs/after/', null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử sửa chữa'
        verbose_name_plural = 'Lịch sử sửa chữa'
        ordering = ['-repair_date']

    def __str__(self):
        return f"{self.road.name} - {self.repair_date}"


class TrafficLight(models.Model):
    STATUS_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('fault', 'Hỏng'),
        ('maintenance', 'Đang bảo trì'),
        ('off', 'Tắt'),
    ]

    code = models.CharField('Mã đèn', max_length=50, unique=True)
    location = models.CharField('Vị trí', max_length=300)
    road = models.ForeignKey(Road, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='traffic_lights', verbose_name='Tuyến đường')
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='active')
    installed_date = models.DateField('Ngày lắp đặt', null=True, blank=True)
    managing_unit = models.CharField('Đơn vị quản lý', max_length=200, blank=True)
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    last_bulb_change = models.DateField('Thay bóng lần cuối', null=True, blank=True)
    operating_hours = models.CharField('Giờ hoạt động', max_length=50, default='24/7')
    zone = models.ForeignKey(ManagementZone, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đèn giao thông'
        verbose_name_plural = 'Đèn giao thông'

    def __str__(self):
        return f"Đèn {self.code} - {self.location}"


class Infrastructure(models.Model):
    """Model chung cho hạ tầng (cầu, hầm, cống, v.v.)"""
    STATUS_CHOICES = [
        ('good', 'Tốt'),
        ('normal', 'Bình thường'),
        ('needs_repair', 'Cần sửa chữa'),
        ('critical', 'Nguy hiểm'),
    ]

    type = models.ForeignKey(InfrastructureType, on_delete=models.CASCADE, verbose_name='Loại')
    name = models.CharField('Tên', max_length=200)
    code = models.CharField('Mã', max_length=50, unique=True)
    status = models.CharField('Trạng thái', max_length=15, choices=STATUS_CHOICES, default='good')
    installed_date = models.DateField('Ngày lắp đặt', null=True, blank=True)
    managing_unit = models.CharField('Đơn vị quản lý', max_length=200, blank=True)
    zone = models.ForeignKey(ManagementZone, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    description = models.TextField('Mô tả', blank=True)
    expected_lifespan_years = models.IntegerField('Tuổi thọ dự kiến (năm)', default=20)
    notes = models.TextField('Ghi chú', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hạ tầng'
        verbose_name_plural = 'Hạ tầng'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.type.name})"

    @property
    def age_years(self):
        if self.installed_date:
            from django.utils import timezone
            return (timezone.now().date() - self.installed_date).days // 365
        return None