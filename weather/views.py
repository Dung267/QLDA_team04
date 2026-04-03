from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import WeatherData, WeatherForecast


def current_weather(request):
    data = WeatherData.objects.order_by('-recorded_at').first()
    forecasts = WeatherForecast.objects.filter(
        forecast_date__gte=timezone.now().date()
    ).order_by('forecast_date')[:7]
    return render(request, 'weather/current.html', {
        'current': data, 'forecasts': forecasts, 'page_title': 'Thời tiết'
    })


def weather_api(request):
    location = request.GET.get('location', '')
    data = WeatherData.objects.filter(location__icontains=location).order_by('-recorded_at').first()
    if data:
        return JsonResponse({
            'location': data.location,
            'temperature': data.temperature,
            'humidity': data.humidity,
            'wind_speed': data.wind_speed,
            'rainfall_mm': data.rainfall_mm,
            'description': data.description,
            'recorded_at': data.recorded_at.isoformat(),
        })
    return JsonResponse({'error': 'No data found'}, status=404)
