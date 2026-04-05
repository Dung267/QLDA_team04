from django.contrib import admin
from .models import ReportTemplate

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name','report_type','is_active']
