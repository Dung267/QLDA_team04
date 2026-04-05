from django.contrib import admin
from .models import ConstructionPermit, PermitDocument

class PermitDocumentInline(admin.TabularInline):
    model = PermitDocument
    extra = 0

@admin.register(ConstructionPermit)
class ConstructionPermitAdmin(admin.ModelAdmin):
    list_display = ['permit_number','title','applicant','status','created_at']
    list_filter = ['status']
    search_fields = ['permit_number','title','applicant__username']
    inlines = [PermitDocumentInline]
