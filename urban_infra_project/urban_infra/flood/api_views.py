from rest_framework import generics, permissions
from .models import FloodAlert, DisasterUpdate
from .serializers import FloodAlertSerializer, DisasterUpdateSerializer


class FloodAlertListAPIView(generics.ListAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActiveFloodAlertsAPIView(generics.ListAPIView):
    queryset = FloodAlert.objects.filter(is_active=True)
    serializer_class = FloodAlertSerializer
    permission_classes = [permissions.AllowAny]


class DisasterUpdateListAPIView(generics.ListAPIView):
    queryset = DisasterUpdate.objects.filter(is_published=True)
    serializer_class = DisasterUpdateSerializer
    permission_classes = [permissions.AllowAny]
