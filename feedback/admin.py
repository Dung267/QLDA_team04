from django.contrib import admin
from .models import SystemFeedback

@admin.register(SystemFeedback)
class SystemFeedbackAdmin(admin.ModelAdmin):
    list_display = ['author','rating','category','status','is_important','likes','created_at']
    list_filter = ['status','rating','is_important']
    search_fields = ['content']
