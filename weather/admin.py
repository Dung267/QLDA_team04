from django.contrib import admin
from .models import WeatherData, WeatherForecast


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'temperature', 'humidity', 'rainfall_mm', 'recorded_at']
    list_filter = ['location']
    date_hierarchy = 'recorded_at'


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['location', 'forecast_date', 'min_temp', 'max_temp', 'is_dangerous']
    list_filter = ['is_dangerous', 'period']
