from rest_framework import generics, permissions
from .models import Road, TrafficLight
from .serializers import RoadSerializer, TrafficLightSerializer


class RoadListAPIView(generics.ListAPIView):
    queryset = Road.objects.select_related('zone').all()
    serializer_class = RoadSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoadDetailAPIView(generics.RetrieveAPIView):
    queryset = Road.objects.all()
    serializer_class = RoadSerializer
    permission_classes = [permissions.IsAuthenticated]


class TrafficLightListAPIView(generics.ListAPIView):
    queryset = TrafficLight.objects.all()
    serializer_class = TrafficLightSerializer
    permission_classes = [permissions.IsAuthenticated]