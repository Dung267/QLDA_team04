from rest_framework import serializers
from .models import Notification, NotificationHistory


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'type_display',
                  'is_read', 'action_url', 'created_at', 'read_at']
        read_only_fields = ['created_at', 'read_at']


class NotificationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationHistory
        fields = '__all__'
