from django.contrib import admin
from .models import Notification, NotificationHistory

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['recipient__username', 'title']
    readonly_fields = ['created_at', 'read_at']

@admin.register(NotificationHistory)
class NotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'channel', 'recipient_count', 'sent_by', 'created_at']
    readonly_fields = ['created_at']