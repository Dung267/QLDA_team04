from rest_framework import serializers
from .models import FloodAlert, DisasterAlert


class FloodAlertSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = FloodAlert
        fields = '__all__'


class DisasterAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterAlert
        fields = '__all__'
