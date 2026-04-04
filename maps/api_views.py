from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from infrastructure.models import Road, TrafficLight, Infrastructure
from maintenance.models import MaintenanceRequest
from flood.models import FloodAlert
from .serializers import RoadMapSerializer, TrafficLightMapSerializer, InfrastructureMapSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def map_layers_api(request):
    layer = request.query_params.get('layer', 'all')
    data = {}

    if layer in ('all', 'roads'):
        data['roads'] = RoadMapSerializer(
            Road.objects.filter(latitude__isnull=False), many=True).data

    if layer in ('all', 'lights'):
        data['lights'] = TrafficLightMapSerializer(
            TrafficLight.objects.filter(latitude__isnull=False), many=True).data

    if layer in ('all', 'infrastructure'):
        data['infrastructure'] = InfrastructureMapSerializer(
            Infrastructure.objects.filter(latitude__isnull=False), many=True).data

    if layer in ('all', 'incidents'):
        incidents = MaintenanceRequest.objects.filter(
            latitude__isnull=False,
            status__in=['pending', 'received', 'assigned', 'in_progress']
        ).values('id', 'title', 'incident_type', 'priority', 'status', 'latitude', 'longitude')
        data['incidents'] = list(incidents)

    if layer in ('all', 'floods'):
        floods = FloodAlert.objects.filter(
            is_active=True, latitude__isnull=False
        ).values('id', 'title', 'level', 'area_name', 'water_level_cm', 'latitude', 'longitude')
        data['floods'] = list(floods)

    return Response(data)
