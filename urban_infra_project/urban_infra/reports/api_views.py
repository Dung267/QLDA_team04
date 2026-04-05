from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from django.utils import timezone


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def summary_stats_api(request):
    from maintenance.models import MaintenanceRequest
    from infrastructure.models import Road, TrafficLight
    from flood.models import FloodAlert
    now = timezone.now()
    month_start = now.date().replace(day=1)
    return Response({
        'total_incidents': MaintenanceRequest.objects.count(),
        'monthly_incidents': MaintenanceRequest.objects.filter(
            created_at__date__gte=month_start).count(),
        'completed_incidents': MaintenanceRequest.objects.filter(status='completed').count(),
        'pending_incidents': MaintenanceRequest.objects.filter(status='pending').count(),
        'total_roads': Road.objects.count(),
        'total_lights': TrafficLight.objects.count(),
        'active_flood_alerts': FloodAlert.objects.filter(is_active=True).count(),
        'avg_citizen_rating': MaintenanceRequest.objects.filter(
            citizen_rating__isnull=False).aggregate(avg=Avg('citizen_rating'))['avg'],
        'total_repair_cost': float(
            MaintenanceRequest.objects.aggregate(t=Sum('actual_cost'))['t'] or 0),
        'incidents_by_type': list(
            MaintenanceRequest.objects.values('incident_type').annotate(count=Count('id'))),
        'incidents_by_status': list(
            MaintenanceRequest.objects.values('status').annotate(count=Count('id'))),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def monthly_stats_api(request):
    from maintenance.models import MaintenanceRequest
    year = int(request.query_params.get('year', timezone.now().year))
    monthly = []
    for m in range(1, 13):
        qs = MaintenanceRequest.objects.filter(created_at__year=year, created_at__month=m)
        monthly.append({
            'month': m,
            'total': qs.count(),
            'completed': qs.filter(status='completed').count(),
            'cost': float(qs.aggregate(t=Sum('actual_cost'))['t'] or 0),
        })
    return Response({'year': year, 'monthly': monthly})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def area_comparison_api(request):
    from maintenance.models import MaintenanceRequest
    from django.db.models import Count
    data = list(
        MaintenanceRequest.objects.values('road__zone__name').annotate(
            count=Count('id')).order_by('-count')[:10])
    return Response(data)
