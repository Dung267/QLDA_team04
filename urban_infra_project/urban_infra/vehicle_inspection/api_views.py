from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count
from .models import Vehicle, Inspection, InspectionCenter
from .serializers import VehicleSerializer, InspectionSerializer, InspectionCenterSerializer


class VehicleListAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff_member:
            return Vehicle.objects.filter(is_active=True)
        return Vehicle.objects.filter(owner=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class VehicleDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]


class InspectionListAPIView(generics.ListCreateAPIView):
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-scheduled_date']

    def get_queryset(self):
        if self.request.user.is_staff_member:
            qs = Inspection.objects.select_related('vehicle', 'center')
        else:
            qs = Inspection.objects.filter(
                vehicle__owner=self.request.user).select_related('vehicle', 'center')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class InspectionDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class InspectionCenterListAPIView(generics.ListAPIView):
    queryset = InspectionCenter.objects.filter(is_active=True)
    serializer_class = InspectionCenterSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inspection_stats_api(request):
    stats = {
        'total': Inspection.objects.count(),
        'by_status': list(Inspection.objects.values('status').annotate(count=Count('id'))),
        'pending': Inspection.objects.filter(status='pending').count(),
        'passed': Inspection.objects.filter(status='passed').count(),
    }
    return Response(stats)
