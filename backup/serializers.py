from rest_framework import serializers
from .models import BackupRecord, RestoreRecord, BackupConfig


class BackupConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupConfig
        fields = '__all__'


class BackupRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BackupRecord
        fields = '__all__'

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class RestoreRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestoreRecord
        fields = '__all__'
