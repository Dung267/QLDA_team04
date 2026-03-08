from django.contrib import admin
from .models import Incident, IncidentAttachment

admin.site.register(Incident)
admin.site.register(IncidentAttachment)