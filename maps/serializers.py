from rest_framework import serializers
from infrastructure.models import Road, TrafficLight, Infrastructure


class RoadMapSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Road
        fields = ['id', 'name', 'code', 'status', 'status_display',
                  'direction', 'latitude', 'longitude']


class TrafficLightMapSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TrafficLight
        fields = ['id', 'code', 'location', 'status', 'status_display',
                  'latitude', 'longitude']


class InfrastructureMapSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Infrastructure
        fields = ['id', 'name', 'code', 'status', 'type_name', 'latitude', 'longitude']
