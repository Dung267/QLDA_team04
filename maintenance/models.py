from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from incidents.models import Incident

class MaintenanceRequest(TimeStampedModel):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="maintenance_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    emergency = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, default="MEDIUM")
    status = models.CharField(max_length=20, default="PENDING")

    def __str__(self):
        return f"MR-{self.id}"