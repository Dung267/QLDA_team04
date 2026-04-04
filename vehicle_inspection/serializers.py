from rest_framework import serializers
from .models import Vehicle, Inspection, InspectionCenter


class InspectionCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCenter
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = '__all__'

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username


class InspectionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.license_plate', read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)

    class Meta:
        model = Inspection
        fields = '__all__'
