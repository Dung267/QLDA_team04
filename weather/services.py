from datetime import datetime

import requests
from django.utils import timezone

from .models import WeatherData, WeatherForecast


DISTRICT_COORDINATES = {
    "Hai Chau": (16.0678, 108.2208),
    "Son Tra": (16.1132, 108.2630),
    "Thanh Khe": (16.0675, 108.1894),
    "Lien Chieu": (16.1039, 108.1171),
    "Ngu Hanh Son": (16.0114, 108.2646),
    "Cam Le": (16.0320, 108.2098),
    "Hoa Vang": (16.1230, 108.0150),
}


def weather_code_to_description(code):
    if code in {0, 1}:
        return "Nang nhe"
    if code in {2, 3, 45, 48}:
        return "Nhieu may"
    if code in {51, 53, 55, 56, 57, 61, 63, 65, 80, 81}:
        return "Mua rao"
    if code in {66, 67, 82, 95, 96, 99}:
        return "Mua dong"
    return "On dinh"


def is_dangerous_weather(rain_mm, weather_code, rain_probability=0):
    return rain_mm >= 30 or rain_probability >= 80 or weather_code in {82, 95, 96, 99}


def _parse_recorded_time(time_str):
    dt = datetime.fromisoformat(time_str)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def fetch_and_store_weather(district):
    if district not in DISTRICT_COORDINATES:
        raise ValueError(f"Unsupported district: {district}")

    latitude, longitude = DISTRICT_COORDINATES[district]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "pressure_msl",
                "weather_code",
            ]
        ),
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_min",
                "temperature_2m_max",
                "precipitation_probability_max",
            ]
        ),
        "forecast_days": 7,
        "timezone": "Asia/Ho_Chi_Minh",
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=12)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    daily = data.get("daily", {})
    location = f"{district}, Da Nang"

    weather_code = int(current.get("weather_code", 0))
    rain_mm = float(current.get("precipitation") or 0)
    weather_obj, _ = WeatherData.objects.update_or_create(
        location=location,
        recorded_at=_parse_recorded_time(current["time"]),
        defaults={
            "latitude": latitude,
            "longitude": longitude,
            "temperature": float(current.get("temperature_2m") or 0),
            "humidity": int(current.get("relative_humidity_2m") or 0),
            "wind_speed": float(current.get("wind_speed_10m") or 0),
            "wind_direction": str(current.get("wind_direction_10m") or ""),
            "description": weather_code_to_description(weather_code),
            "icon": "",
            "rain_mm": rain_mm,
            "pressure_hpa": float(current.get("pressure_msl") or 0),
            "is_dangerous": is_dangerous_weather(rain_mm=rain_mm, weather_code=weather_code),
            "source": "open-meteo",
        },
    )

    days = daily.get("time", [])
    temp_min = daily.get("temperature_2m_min", [])
    temp_max = daily.get("temperature_2m_max", [])
    codes = daily.get("weather_code", [])
    rain_prob = daily.get("precipitation_probability_max", [])

    for i, forecast_day in enumerate(days[:7]):
        day_code = int(codes[i] if i < len(codes) else 0)
        day_rain_probability = int(rain_prob[i] if i < len(rain_prob) else 0)
        warning = is_dangerous_weather(
            rain_mm=0,
            weather_code=day_code,
            rain_probability=day_rain_probability,
        )
        warning_message = ""
        if warning:
            warning_message = "Canh bao mua lon va nguy co ngap ung tai mot so tuyen duong noi thanh Da Nang."
        WeatherForecast.objects.update_or_create(
            location=location,
            forecast_date=datetime.strptime(forecast_day, "%Y-%m-%d").date(),
            defaults={
                "temp_min": float(temp_min[i] if i < len(temp_min) else 0),
                "temp_max": float(temp_max[i] if i < len(temp_max) else 0),
                "description": weather_code_to_description(day_code),
                "rain_probability": day_rain_probability,
                "is_warning": warning,
                "warning_message": warning_message,
            },
        )
    return weather_obj
