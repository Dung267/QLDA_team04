from django.contrib import admin
from .models import SystemFeedback


@admin.register(SystemFeedback)
class SystemFeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'rating', 'status', 'like_count', 'created_at']
    list_filter = ['category', 'status', 'is_important']
    search_fields = ['title', 'content']
