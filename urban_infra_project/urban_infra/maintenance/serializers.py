from rest_framework import serializers
from .models import MaintenanceRequest, MaintenancePhoto, MaintenanceComment, MaintenanceSchedule


class MaintenancePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenancePhoto
        fields = ['id', 'image', 'phase', 'caption', 'uploaded_at']


class MaintenanceCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = MaintenanceComment
        fields = ['id', 'author_name', 'content', 'is_internal', 'created_at']


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    incident_type_display = serializers.CharField(source='get_incident_type_display', read_only=True)
    reporter_name = serializers.SerializerMethodField()
    assignee_name = serializers.SerializerMethodField()
    photos = MaintenancePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

    def get_reporter_name(self, obj):
        if obj.is_anonymous or not obj.reported_by:
            return 'Ẩn danh'
        return obj.reported_by.get_full_name() or obj.reported_by.username

    def get_assignee_name(self, obj):
        if not obj.assigned_to:
            return None
        return obj.assigned_to.get_full_name() or obj.assigned_to.username


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
