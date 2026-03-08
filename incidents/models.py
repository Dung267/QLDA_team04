from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from infrastructure.models import Area

class Incident(TimeStampedModel):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    incident_type = models.CharField(max_length=30)
    title = models.CharField(max_length=255)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    status = models.CharField(max_length=20, default="NEW")
    priority = models.CharField(max_length=20, default="MEDIUM")
    duplicate_of = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

class IncidentAttachment(TimeStampedModel):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="incident_attachments/%Y/%m/")
    file_type = models.CharField(max_length=10, default="IMAGE")