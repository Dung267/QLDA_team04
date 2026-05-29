from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import WeatherData, WeatherForecast
from .services import fetch_and_store_weather

DANANG_DISTRICTS = [
    ("Hai Chau", "Hải Châu"),
    ("Son Tra", "Sơn Trà"),
    ("Thanh Khe", "Thanh Khê"),
    ("Lien Chieu", "Liên Chiểu"),
    ("Ngu Hanh Son", "Ngũ Hành Sơn"),
    ("Cam Le", "Cẩm Lệ"),
    ("Hoa Vang", "Hòa Vang"),
]


def _get_weather_icon(description, rain_mm=0, wind_speed=0):
    text = (description or "").lower()
    if rain_mm >= 10 or "mua" in text or "rain" in text:
        return "bi-cloud-rain"
    if wind_speed >= 25 or "gio" in text or "wind" in text:
        return "bi-wind"
    if "may" in text or "cloud" in text:
        return "bi-cloud-sun"
    return "bi-sun"


def _build_dummy_forecasts(location):
    base_date = timezone.localdate()
    samples = [
        (29, 35, "Nang nhe", 10, False, ""),
        (28, 34, "Nhieu may", 30, False, ""),
        (27, 32, "Mua rao", 65, False, ""),
        (26, 31, "Mua vua", 75, True, "Theo doi diem ngap cuc bo khu vuc Hai Chau."),
        (27, 33, "Co gio", 40, False, ""),
        (28, 34, "Nang nong", 15, False, ""),
        (27, 32, "Mua dong", 80, True, "Canh bao ngap ung tuyen pho Le Duan vao khung gio cao diem."),
    ]
    dummy_items = []
    for i, item in enumerate(samples):
        temp_min, temp_max, description, rain_probability, is_warning, warning_message = item
        dummy_items.append(
            {
                "forecast_date": base_date + timedelta(days=i),
                "temp_min": temp_min,
                "temp_max": temp_max,
                "description": description,
                "rain_probability": rain_probability,
                "is_warning": is_warning,
                "warning_message": warning_message,
                "location": location,
                "icon_class": _get_weather_icon(description),
            }
        )
    return dummy_items


def _resolve_location(request):
    district = request.GET.get("district") or request.POST.get("district") or "Hai Chau"
    district_values = {item[0] for item in DANANG_DISTRICTS}
    if district not in district_values:
        district = "Hai Chau"
    location = f"{district}, Da Nang"
    return district, location

@login_required
def current_weather(request):
    district, location = _resolve_location(request)
    should_refresh = request.GET.get("refresh") == "1"
    if should_refresh:
        try:
            fetch_and_store_weather(district)
            messages.success(request, f"Da cap nhat du lieu thoi tiet moi nhat cho {location}.")
        except Exception:
            messages.warning(request, "Khong the cap nhat du lieu tu API luc nay. Dang hien thi du lieu hien co.")

    latest = WeatherData.objects.filter(location__icontains=location).first()

    if latest:
        latest.icon_class = _get_weather_icon(latest.description, latest.rain_mm, latest.wind_speed)

    db_forecasts = list(
        WeatherForecast.objects.filter(
            location__icontains=location,
            forecast_date__gte=timezone.localdate(),
        )[:7]
    )

    forecasts = []
    for item in db_forecasts:
        item.icon_class = _get_weather_icon(item.description, 0, 0)
        forecasts.append(item)

    if len(forecasts) < 7:
        dummy_forecasts = _build_dummy_forecasts(location)
        existing_dates = {item.forecast_date for item in db_forecasts}
        for item in dummy_forecasts:
            if item["forecast_date"] not in existing_dates:
                forecasts.append(item)
            if len(forecasts) == 7:
                break

    context = {
        "latest": latest,
        "forecasts": forecasts,
        "location": location,
        "district": district,
        "district_options": DANANG_DISTRICTS,
        "page_title": "Theo doi thoi tiet va canh bao",
        "alert_message": "Canh bao ngap ung tuyen pho Le Duan va mot so diem trung tam quan Hai Chau.",
    }
    return render(request, "weather/current_weather.html", context)


@login_required
def forecast_weather(request):
    district, location = _resolve_location(request)
    should_refresh = request.GET.get("refresh") == "1"
    if should_refresh:
        try:
            fetch_and_store_weather(district)
            messages.success(request, f"Da dong bo du bao 7 ngay cho {location}.")
        except Exception:
            messages.warning(request, "Khong the dong bo du bao tu API luc nay. Dang hien thi du lieu hien co.")

    db_forecasts = list(
        WeatherForecast.objects.filter(
            location__icontains=location,
            forecast_date__gte=timezone.localdate(),
        )[:7]
    )

    forecasts = []
    for item in db_forecasts:
        item.icon_class = _get_weather_icon(item.description, 0, 0)
        forecasts.append(item)

    if len(forecasts) < 7:
        dummy_forecasts = _build_dummy_forecasts(location)
        existing_dates = {item.forecast_date for item in db_forecasts}
        for item in dummy_forecasts:
            if item["forecast_date"] not in existing_dates:
                forecasts.append(item)
            if len(forecasts) == 7:
                break

    return render(
        request,
        "weather/forecast_page.html",
        {
            "forecasts": forecasts[:7],
            "location": location,
            "district": district,
            "district_options": DANANG_DISTRICTS,
            "page_title": "Du bao 7 ngay toi",
        },
    )


@login_required
def sync_weather_api(request):
    district, location = _resolve_location(request)
    if request.method == "POST":
        try:
            fetch_and_store_weather(district)
            messages.success(request, f"Da cap nhat du lieu API cho {location}.")
        except Exception:
            messages.error(request, "Cap nhat API that bai. Vui long thu lai sau.")
    fallback_url = f"/weather/?district={district}"
    return redirect(request.META.get("HTTP_REFERER") or fallback_url)

@login_required
def weather_api(request):
    location = request.GET.get("location", "")
    qs = WeatherData.objects.all()
    if location:
        qs = qs.filter(location__icontains=location)
    data = list(
        qs.values(
            "location",
            "temperature",
            "humidity",
            "wind_speed",
            "rain_mm",
            "is_dangerous",
            "description",
            "recorded_at",
        )[:10]
    )
    return JsonResponse({"data": data})
