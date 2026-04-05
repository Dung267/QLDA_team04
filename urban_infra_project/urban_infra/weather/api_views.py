from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import WeatherData, WeatherForecast
from .serializers import WeatherDataSerializer, WeatherForecastSerializer


class WeatherDataListAPIView(generics.ListAPIView):
    queryset = WeatherData.objects.order_by('-recorded_at')[:50]
    serializer_class = WeatherDataSerializer
    permission_classes = [permissions.AllowAny]


class WeatherForecastListAPIView(generics.ListAPIView):
    serializer_class = WeatherForecastSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        location = self.request.query_params.get('location', '')
        qs = WeatherForecast.objects.filter(forecast_date__gte=timezone.now().date())
        if location:
            qs = qs.filter(location__icontains=location)
        return qs[:7]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def current_weather_api(request):
    location = request.query_params.get('location', 'Da Nang')
    latest = WeatherData.objects.filter(location__icontains=location).first()
    if latest:
        return Response(WeatherDataSerializer(latest).data)
    return Response({'error': 'No data available'}, status=404)
