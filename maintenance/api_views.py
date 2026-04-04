from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum
from .models import MaintenanceRequest, MaintenanceSchedule
from .serializers import MaintenanceRequestSerializer, MaintenanceScheduleSerializer


class MaintenanceRequestListAPIView(generics.ListCreateAPIView):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = MaintenanceRequest.objects.select_related('reported_by', 'assigned_to')
        if self.request.user.role == 'citizen':
            qs = qs.filter(reported_by=self.request.user)
        status = self.request.query_params.get('status')
        incident_type = self.request.query_params.get('type')
        priority = self.request.query_params.get('priority')
        if status:
            qs = qs.filter(status=status)
        if incident_type:
            qs = qs.filter(incident_type=incident_type)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class MaintenanceRequestDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class MaintenanceScheduleListAPIView(generics.ListCreateAPIView):
    queryset = MaintenanceSchedule.objects.all()
    serializer_class = MaintenanceScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def maintenance_stats_api(request):
    stats = {
        'by_status': list(MaintenanceRequest.objects.values('status').annotate(count=Count('id'))),
        'by_type': list(MaintenanceRequest.objects.values('incident_type').annotate(count=Count('id'))),
        'by_priority': list(MaintenanceRequest.objects.values('priority').annotate(count=Count('id'))),
        'avg_rating': MaintenanceRequest.objects.filter(
            citizen_rating__isnull=False).aggregate(avg=Avg('citizen_rating'))['avg'],
        'total_cost': float(MaintenanceRequest.objects.aggregate(
            t=Sum('actual_cost'))['t'] or 0),
    }
    return Response(stats)
