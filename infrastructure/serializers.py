from rest_framework import serializers
from .models import Road, TrafficLight, Pothole


class RoadSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = Road
        fields = '__all__'


class TrafficLightSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TrafficLight
        fields = '__all__'


class PotholeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pothole
        fields = '__all__'