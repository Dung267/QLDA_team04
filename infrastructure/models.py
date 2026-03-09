# infrastructure/models.py
from django.db import models
from common.models import TimeStampedModel


class Area(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children"
    )

    def __str__(self):
        return self.name


class RoadCondition(models.TextChoices):
    GOOD = "GOOD", "Tốt"
    FAIR = "FAIR", "Trung bình"
    POOR = "POOR", "Kém"
    DAMAGED = "DAMAGED", "Hư hỏng"


class Road(TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="roads")
    length_m = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    width_m = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    year_built = models.PositiveIntegerField(null=True, blank=True)
    condition = models.CharField(
        max_length=20,
        choices=RoadCondition.choices,
        default=RoadCondition.GOOD
    )
    surface_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class PotholeSeverity(models.TextChoices):
    LOW = "LOW", "Thấp"
    MEDIUM = "MEDIUM", "Trung bình"
    HIGH = "HIGH", "Cao"
    CRITICAL = "CRITICAL", "Khẩn cấp"


class PotholeStatus(models.TextChoices):
    OPEN = "OPEN", "Mới phát hiện"
    IN_PROGRESS = "IN_PROGRESS", "Đang xử lý"
    FIXED = "FIXED", "Đã sửa"


class Pothole(TimeStampedModel):
    road = models.ForeignKey(Road, on_delete=models.CASCADE, related_name="potholes")
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    severity = models.CharField(
        max_length=20,
        choices=PotholeSeverity.choices,
        default=PotholeSeverity.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=PotholeStatus.choices,
        default=PotholeStatus.OPEN
    )

    def __str__(self):
        return f"{self.road.name} - {self.severity}"


class TrafficLightStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Hoạt động"
    FAULT = "FAULT", "Lỗi"
    OFFLINE = "OFFLINE", "Mất kết nối"
    MAINTENANCE = "MAINTENANCE", "Bảo trì"


class TrafficLight(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    location_name = models.CharField(max_length=255)
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name="traffic_lights",
        null=True,
        blank=True
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_status = models.CharField(
        max_length=20,
        choices=TrafficLightStatus.choices,
        default=TrafficLightStatus.ACTIVE
    )
    installed_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.location_name}"