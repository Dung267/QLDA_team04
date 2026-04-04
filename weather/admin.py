from django.contrib import admin
from .models import WeatherData, WeatherForecast

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location','temperature','humidity','rain_mm','is_dangerous','recorded_at']

@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['location','forecast_date','temp_min','temp_max','rain_probability','is_warning']
