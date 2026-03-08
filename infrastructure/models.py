from django.db import models
from common.models import TimeStampedModel

class Area(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Road(TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    length_m = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    width_m = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    year_built = models.PositiveIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=30, default="GOOD")

    def __str__(self):
        return self.name

class Pothole(TimeStampedModel):
    road = models.ForeignKey(Road, on_delete=models.CASCADE, related_name="potholes")
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    severity = models.CharField(max_length=20, default="MEDIUM")
    status = models.CharField(max_length=20, default="OPEN")

    def __str__(self):
        return f"{self.road.name} - {self.status}"