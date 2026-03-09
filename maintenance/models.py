# maintenance/models.py
from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from incidents.models import Incident


class MaintenancePriority(models.TextChoices):
    LOW = "LOW", "Thấp"
    MEDIUM = "MEDIUM", "Trung bình"
    HIGH = "HIGH", "Cao"
    CRITICAL = "CRITICAL", "Khẩn cấp"


class MaintenanceStatus(models.TextChoices):
    PENDING = "PENDING", "Chờ xử lý"
    ASSIGNED = "ASSIGNED", "Đã phân công"
    IN_PROGRESS = "IN_PROGRESS", "Đang thực hiện"
    DONE = "DONE", "Hoàn thành"
    CANCELED = "CANCELED", "Đã hủy"


class MaintenanceRequest(TimeStampedModel):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="maintenance_requests"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_maintenances"
    )
    emergency = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=20,
        choices=MaintenancePriority.choices,
        default=MaintenancePriority.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING
    )

    def __str__(self):
        return f"MR-{self.id}"


class MaintenanceAssignment(TimeStampedModel):
    request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_tasks"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_assigned_by"
    )
    note = models.TextField(blank=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.request} -> {self.assigned_to}"


class MaintenanceProgress(TimeStampedModel):
    request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name="progress_logs"
    )
    status = models.CharField(max_length=20, choices=MaintenanceStatus.choices)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.request} - {self.status}"