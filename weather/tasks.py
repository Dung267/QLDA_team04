from datetime import datetime, timezone as dt_timezone

import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from flood.models import FloodAlert
from notifications.models import Notification

from .models import WeatherData
from .services import DISTRICT_COORDINATES, fetch_and_store_weather, is_dangerous_weather


OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"


def _recorded_at_from_timestamp(timestamp):
    recorded = datetime.fromtimestamp(timestamp, tz=dt_timezone.utc)
    return timezone.localtime(recorded)


def _rain_from_payload(payload):
    rain = payload.get("rain") or {}
    return float(rain.get("1h") or rain.get("3h") or 0)


def _notify_staff(alert):
    User = get_user_model()
    staff_users = User.objects.filter(is_active=True, is_staff=True)
    for user in staff_users:
        Notification.objects.get_or_create(
            recipient=user,
            title=f"Canh bao ngap: {alert.area_name}",
            notification_type="flood",
            related_object_id=alert.id,
            defaults={
                "message": alert.description,
                "action_url": f"/flood/{alert.id}/",
            },
        )


def _create_or_update_flood_alert(weather_obj):
    alert_threshold = getattr(settings, "WEATHER_ALERT_RAIN_MM", 50)
    if not weather_obj.is_dangerous and weather_obj.rain_mm < alert_threshold:
        return None

    level = "3" if weather_obj.rain_mm >= alert_threshold else "2"
    title = f"Canh bao mua lon - {weather_obj.location}"
    description = (
        f"He thong thoi tiet ghi nhan mua {weather_obj.rain_mm:.1f} mm tai "
        f"{weather_obj.location}. Can theo doi nguy co ngap ung va dieu tiet giao thong."
    )

    alert, _ = FloodAlert.objects.update_or_create(
        title=title,
        area_name=weather_obj.location,
        is_active=True,
        defaults={
            "description": description,
            "level": level,
            "area_type": "district",
            "latitude": weather_obj.latitude,
            "longitude": weather_obj.longitude,
            "water_level_cm": int(max(weather_obj.rain_mm * 2, 20)),
            "safe_routes": "Can bo truc ban cap nhat tuyen an toan sau khi xac minh hien truong.",
            "evacuation_info": "Theo doi thong bao tu ban chi huy va chinh quyen dia phuong.",
        },
    )
    _notify_staff(alert)
    return alert


def fetch_openweathermap_weather(district):
    api_key = getattr(settings, "OPENWEATHER_API_KEY", "")
    if not api_key:
        return fetch_and_store_weather(district)

    latitude, longitude = DISTRICT_COORDINATES[district]
    response = requests.get(
        OPENWEATHER_CURRENT_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
            "lang": "vi",
        },
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()

    weather = (payload.get("weather") or [{}])[0]
    main = payload.get("main") or {}
    wind = payload.get("wind") or {}
    rain_mm = _rain_from_payload(payload)
    weather_code = int(weather.get("id") or 0)
    recorded_at = _recorded_at_from_timestamp(payload.get("dt") or timezone.now().timestamp())
    location = f"{district}, Da Nang"
    dangerous = is_dangerous_weather(
        rain_mm=rain_mm,
        weather_code=weather_code,
        rain_probability=0,
    ) or rain_mm >= getattr(settings, "WEATHER_ALERT_RAIN_MM", 50) or weather_code // 100 in {2, 5}

    weather_obj, _ = WeatherData.objects.update_or_create(
        location=location,
        recorded_at=recorded_at,
        defaults={
            "latitude": latitude,
            "longitude": longitude,
            "temperature": float(main.get("temp") or 0),
            "humidity": int(main.get("humidity") or 0),
            "wind_speed": round(float(wind.get("speed") or 0) * 3.6, 1),
            "wind_direction": str(wind.get("deg") or ""),
            "description": weather.get("description") or "",
            "icon": weather.get("icon") or "",
            "rain_mm": rain_mm,
            "pressure_hpa": float(main.get("pressure") or 0),
            "is_dangerous": dangerous,
            "source": "openweathermap",
        },
    )
    return weather_obj


@shared_task(name="weather.tasks.sync_danang_weather")
def sync_danang_weather():
    synced = 0
    alerts = 0
    errors = {}

    for district in DISTRICT_COORDINATES:
        try:
            weather_obj = fetch_openweathermap_weather(district)
            synced += 1
            if _create_or_update_flood_alert(weather_obj):
                alerts += 1
        except Exception as exc:
            errors[district] = str(exc)

    return {
        "synced": synced,
        "alerts": alerts,
        "errors": errors,
    }
