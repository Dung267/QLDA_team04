from django.db import models


class WeatherData(models.Model):
    location = models.CharField('Vị trí', max_length=100)
    district = models.CharField('Quận/Huyện', max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    temperature = models.FloatField('Nhiệt độ (°C)')
    humidity = models.FloatField('Độ ẩm (%)')
    wind_speed = models.FloatField('Tốc độ gió (km/h)', default=0)
    rainfall_mm = models.FloatField('Lượng mưa (mm)', default=0)
    description = models.CharField('Mô tả', max_length=200, blank=True)
    weather_code = models.CharField('Mã thời tiết', max_length=10, blank=True)
    recorded_at = models.DateTimeField('Thời điểm đo')
    source = models.CharField('Nguồn', max_length=50, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dữ liệu thời tiết'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.location} - {self.recorded_at.strftime('%d/%m/%Y %H:%M')}"


class WeatherForecast(models.Model):
    PERIOD_CHOICES = [('daily','Hàng ngày'),('weekly','Hàng tuần')]
    location = models.CharField('Vị trí', max_length=100)
    forecast_date = models.DateField('Ngày dự báo')
    period = models.CharField('Kỳ hạn', max_length=10, choices=PERIOD_CHOICES, default='daily')
    min_temp = models.FloatField('Nhiệt độ thấp nhất')
    max_temp = models.FloatField('Nhiệt độ cao nhất')
    rainfall_probability = models.FloatField('Xác suất mưa (%)', default=0)
    description = models.CharField('Mô tả', max_length=200)
    is_dangerous = models.BooleanField('Nguy hiểm', default=False)
    warning_message = models.TextField('Cảnh báo', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dự báo thời tiết'
        ordering = ['forecast_date']

    def __str__(self):
        return f"{self.location} - {self.forecast_date}"
