from django.db import models
from common.models import TimeStampedModel
from infrastructure.models import Area

class Alert(TimeStampedModel):
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    alert_type = models.CharField(max_length=30)  # FLOOD, STORM, DISASTER
    severity = models.CharField(max_length=20)    # LOW, MEDIUM, HIGH, CRITICAL
    title = models.CharField(max_length=255)
    message = models.TextField()
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)