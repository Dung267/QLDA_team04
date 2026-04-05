from rest_framework import serializers
from .models import FloodAlert, DisasterUpdate


class FloodAlertSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    area_type_display = serializers.CharField(source='get_area_type_display', read_only=True)

    class Meta:
        model = FloodAlert
        fields = '__all__'


class DisasterUpdateSerializer(serializers.ModelSerializer):
    disaster_type_display = serializers.CharField(source='get_disaster_type_display', read_only=True)

    class Meta:
        model = DisasterUpdate
        fields = '__all__'
