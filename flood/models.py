from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class FloodAlert(models.Model):
    LEVEL_CHOICES = [
        ('watch', 'Cảnh báo'),
        ('warning', 'Nguy hiểm'),
        ('emergency', 'Khẩn cấp'),
    ]
    area_name = models.CharField('Khu vực', max_length=200)
    district = models.CharField('Quận/Huyện', max_length=100)
    level = models.CharField('Mức độ', max_length=10, choices=LEVEL_CHOICES)
    description = models.TextField('Mô tả')
    water_level_cm = models.FloatField('Mực nước (cm)', default=0)
    latitude = models.FloatField('Vĩ độ', null=True, blank=True)
    longitude = models.FloatField('Kinh độ', null=True, blank=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    safe_routes = models.TextField('Tuyến đường an toàn', blank=True)
    evacuation_info = models.TextField('Thông tin sơ tán', blank=True)
    shelter_locations = models.TextField('Địa điểm trú ẩn', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cảnh báo ngập lụt'
        verbose_name_plural = 'Cảnh báo ngập lụt'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.area_name} - {self.get_level_display()}"


class DisasterAlert(models.Model):
    TYPE_CHOICES = [
        ('storm', 'Bão'),
        ('flood', 'Lũ lụt'),
        ('earthquake', 'Động đất'),
        ('landslide', 'Sạt lở'),
        ('power_outage', 'Mất điện'),
    ]
    disaster_type = models.CharField('Loại thiên tai', max_length=15, choices=TYPE_CHOICES)
    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả')
    affected_areas = models.TextField('Khu vực ảnh hưởng')
    safety_guidelines = models.TextField('Hướng dẫn an toàn', blank=True)
    property_protection = models.TextField('Bảo vệ tài sản', blank=True)
    unsafe_areas = models.TextField('Khu vực không an toàn', blank=True)
    service_status = models.TextField('Tình trạng dịch vụ', blank=True)
    is_active = models.BooleanField('Đang hoạt động', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cảnh báo thiên tai'
        verbose_name_plural = 'Cảnh báo thiên tai'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_disaster_type_display()} - {self.title}"


class WeatherStation(models.Model):
    name = models.CharField('Tên trạm', max_length=100)
    location = models.CharField('Vị trí', max_length=200)
    latitude = models.FloatField('Vĩ độ')
    longitude = models.FloatField('Kinh độ')
    is_active = models.BooleanField('Hoạt động', default=True)
    api_endpoint = models.URLField('API endpoint', blank=True)

    class Meta:
        verbose_name = 'Trạm khí tượng'

    def __str__(self):
        return self.name
