from django.contrib import admin
from .models import ConstructionPermit, PermitDocument, PermitInspection


class PermitDocumentInline(admin.TabularInline):
    model = PermitDocument
    extra = 0


@admin.register(ConstructionPermit)
class ConstructionPermitAdmin(admin.ModelAdmin):
    list_display = ['permit_number', 'project_name', 'permit_type', 'status', 'applicant', 'created_at']
    list_filter = ['status', 'permit_type']
    search_fields = ['permit_number', 'project_name']
    inlines = [PermitDocumentInline]
