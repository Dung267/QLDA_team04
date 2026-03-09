# incidents/models.py
from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from infrastructure.models import Area


class IncidentType(models.TextChoices):
    ROAD_DAMAGE = "ROAD_DAMAGE", "Đường hư hỏng"
    FLOOD = "FLOOD", "Ngập lụt"
    TRAFFIC_LIGHT = "TRAFFIC_LIGHT", "Đèn giao thông lỗi"
    BRIDGE_DAMAGE = "BRIDGE_DAMAGE", "Cầu hư hỏng"
    OTHER = "OTHER", "Khác"


class IncidentStatus(models.TextChoices):
    NEW = "NEW", "Mới"
    VERIFIED = "VERIFIED", "Đã xác minh"
    ASSIGNED = "ASSIGNED", "Đã phân công"
    RESOLVED = "RESOLVED", "Đã xử lý"
    REJECTED = "REJECTED", "Từ chối"


class IncidentPriority(models.TextChoices):
    LOW = "LOW", "Thấp"
    MEDIUM = "MEDIUM", "Trung bình"
    HIGH = "HIGH", "Cao"
    CRITICAL = "CRITICAL", "Khẩn cấp"


class Incident(TimeStampedModel):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_incidents"
    )
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="incidents")
    incident_type = models.CharField(max_length=30, choices=IncidentType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=IncidentStatus.choices,
        default=IncidentStatus.NEW
    )
    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="duplicates"
    )
    priority = models.CharField(
        max_length=20,
        choices=IncidentPriority.choices,
        default=IncidentPriority.MEDIUM
    )

    def __str__(self):
        return self.title


class IncidentAttachment(TimeStampedModel):
    FILE_TYPE_CHOICES = [
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
    ]

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(upload_to="incident_attachments/%Y/%m/")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default="IMAGE")

    def __str__(self):
        return f"{self.incident.title} - {self.file_type}"