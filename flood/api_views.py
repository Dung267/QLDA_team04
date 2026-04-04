from rest_framework import generics, permissions
from .models import FloodAlert
from .serializers import FloodAlertSerializer


class FloodAlertListAPIView(generics.ListAPIView):
    queryset = FloodAlert.objects.all()
    serializer_class = FloodAlertSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActiveFloodAlertsAPIView(generics.ListAPIView):
    queryset = FloodAlert.objects.filter(is_active=True)
    serializer_class = FloodAlertSerializer
    permission_classes = [permissions.AllowAny]
