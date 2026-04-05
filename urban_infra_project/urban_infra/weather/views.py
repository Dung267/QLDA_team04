from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import WeatherData, WeatherForecast
from django.utils import timezone

@login_required
def current_weather(request):
    location = request.GET.get('location','Da Nang')
    latest = WeatherData.objects.filter(location__icontains=location).first()
    forecasts = WeatherForecast.objects.filter(
        location__icontains=location,
        forecast_date__gte=timezone.now().date()
    )[:7]
    return render(request,'weather/current_weather.html',{
        'latest':latest,'forecasts':forecasts,'location':location,'page_title':'Thời tiết'})

@login_required
def weather_api(request):
    location = request.GET.get('location','')
    qs = WeatherData.objects.all()
    if location:
        qs = qs.filter(location__icontains=location)
    data = list(qs.values('location','temperature','humidity','wind_speed','description','recorded_at')[:10])
    return JsonResponse({'data':data})
