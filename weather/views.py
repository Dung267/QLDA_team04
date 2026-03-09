# weather/views.py
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

def get_current_weather(request):
    city = request.GET.get("city", "Da Nang")
    api_key = getattr(settings, "OPENWEATHER_API_KEY", "")

    weather = None
    if not api_key:
        messages.warning(request, "Bạn chưa cấu hình OPENWEATHER_API_KEY trong settings/.env.")
        return render(request, "weather/current_weather.html", {"weather": weather, "city": city})

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric", "lang": "vi"}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        weather = response.json()
    except Exception as e:
        messages.error(request, f"Lỗi lấy dữ liệu thời tiết: {e}")

    return render(request, "weather/current_weather.html", {"weather": weather, "city": city})


def get_weather_forecast(request):
    city = request.GET.get("city", "Da Nang")
    api_key = getattr(settings, "OPENWEATHER_API_KEY", "")

    forecast = None
    if not api_key:
        messages.warning(request, "Bạn chưa cấu hình OPENWEATHER_API_KEY trong settings/.env.")
        return render(request, "weather/forecast.html", {"forecast": forecast, "city": city})

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": city, "appid": api_key, "units": "metric", "lang": "vi"}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        forecast = response.json()
    except Exception as e:
        messages.error(request, f"Lỗi lấy dữ liệu dự báo: {e}")

    return render(request, "weather/forecast.html", {"forecast": forecast, "city": city})