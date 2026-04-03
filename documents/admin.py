from django.contrib import admin
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'version', 'is_public', 'uploaded_by', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['title', 'description']
