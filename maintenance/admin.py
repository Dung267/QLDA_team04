from django.contrib import admin
from .models import MaintenanceRequest, MaintenanceAssignment, MaintenanceProgress

admin.site.register(MaintenanceRequest)
admin.site.register(MaintenanceAssignment)
admin.site.register(MaintenanceProgress)