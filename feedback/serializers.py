from rest_framework import serializers
from .models import SystemFeedback


class SystemFeedbackSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = SystemFeedback
        fields = '__all__'
        read_only_fields = ['author', 'likes', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.is_anonymous or not obj.author:
            return 'Ẩn danh'
        return obj.author.get_full_name() or obj.author.username
