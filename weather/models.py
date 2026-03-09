# weather/models.py
from django.db import models
from common.models import TimeStampedModel
from infrastructure.models import Area


class WeatherSnapshot(TimeStampedModel):
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True)
    city_name = models.CharField(max_length=100, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.IntegerField(null=True, blank=True)
    rainfall_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    weather_main = models.CharField(max_length=100, blank=True)
    observed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.city_name or f"Weather #{self.id}"