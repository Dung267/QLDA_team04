from django.db import models

class WeatherData(models.Model):
    location = models.CharField('Vị trí', max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    temperature = models.FloatField('Nhiệt độ (°C)')
    humidity = models.IntegerField('Độ ẩm (%)')
    wind_speed = models.FloatField('Tốc độ gió (km/h)', default=0)
    wind_direction = models.CharField('Hướng gió', max_length=10, blank=True)
    description = models.CharField('Mô tả', max_length=200, blank=True)
    icon = models.CharField('Icon', max_length=50, blank=True)
    rain_mm = models.FloatField('Lượng mưa (mm)', default=0)
    pressure_hpa = models.FloatField('Áp suất (hPa)', null=True, blank=True)
    is_dangerous = models.BooleanField('Nguy hiểm', default=False)
    source = models.CharField('Nguồn dữ liệu', max_length=50, default='manual')
    recorded_at = models.DateTimeField('Thời gian đo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dữ liệu thời tiết'
        verbose_name_plural = 'Dữ liệu thời tiết'
        ordering = ['-recorded_at']

    def __str__(self): return f"{self.location} - {self.recorded_at.strftime('%d/%m/%Y %H:%M')}"


class WeatherForecast(models.Model):
    location = models.CharField('Vị trí', max_length=200)
    forecast_date = models.DateField('Ngày dự báo')
    temp_min = models.FloatField('Nhiệt độ thấp nhất')
    temp_max = models.FloatField('Nhiệt độ cao nhất')
    description = models.CharField('Mô tả', max_length=200, blank=True)
    rain_probability = models.IntegerField('Xác suất mưa (%)', default=0)
    is_warning = models.BooleanField('Cảnh báo', default=False)
    warning_message = models.TextField('Thông điệp cảnh báo', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dự báo thời tiết'
        verbose_name_plural = 'Dự báo thời tiết'
        ordering = ['forecast_date']
