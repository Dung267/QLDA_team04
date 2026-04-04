from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class FloodAlert(models.Model):
    LEVEL_CHOICES = [('1','Cấp 1 - Theo dõi'),('2','Cấp 2 - Cảnh báo'),('3','Cấp 3 - Nguy hiểm'),('4','Cấp 4 - Rất nguy hiểm')]
    AREA_TYPES = [('district','Quận/Huyện'),('ward','Phường/Xã'),('road','Tuyến đường'),('infra','Hạ tầng')]

    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả')
    level = models.CharField('Cấp độ', max_length=2, choices=LEVEL_CHOICES, default='1')
    area_type = models.CharField('Loại khu vực', max_length=10, choices=AREA_TYPES, default='district')
    area_name = models.CharField('Tên khu vực', max_length=200)
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    water_level_cm = models.IntegerField('Mực nước (cm)', null=True, blank=True)
    safe_routes = models.TextField('Tuyến đường an toàn', blank=True)
    evacuation_info = models.TextField('Thông tin sơ tán', blank=True)
    shelter_locations = models.TextField('Địa điểm trú ẩn', blank=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    is_sent_sms = models.BooleanField('Đã gửi SMS', default=False)
    rescue_teams_notified = models.BooleanField('Đã thông báo đội cứu hộ', default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cảnh báo ngập lụt'
        verbose_name_plural = 'Cảnh báo ngập lụt'
        ordering = ['-created_at']

    def __str__(self): return f"{self.title} - Cấp {self.level}"


class DisasterUpdate(models.Model):
    TYPE_CHOICES = [('flood','Lũ lụt'),('storm','Bão'),('earthquake','Động đất'),('other','Khác')]
    disaster_type = models.CharField('Loại thiên tai', max_length=15, choices=TYPE_CHOICES)
    title = models.CharField('Tiêu đề', max_length=200)
    content = models.TextField('Nội dung')
    affected_areas = models.TextField('Khu vực bị ảnh hưởng', blank=True)
    casualties = models.TextField('Tình trạng nạn nhân', blank=True)
    infra_status = models.TextField('Tình trạng hạ tầng', blank=True)
    service_status = models.TextField('Tình trạng dịch vụ (y tế, điện, nước)', blank=True)
    power_status = models.TextField('Tình trạng điện', blank=True)
    areas_needing_help = models.TextField('Khu vực cần hỗ trợ', blank=True)
    is_published = models.BooleanField('Đã đăng', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cập nhật thiên tai'
        verbose_name_plural = 'Cập nhật thiên tai'
        ordering = ['-created_at']

    def __str__(self): return f"{self.get_disaster_type_display()} - {self.title}"
