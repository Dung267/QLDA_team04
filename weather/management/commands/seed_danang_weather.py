from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from weather.models import WeatherData, WeatherForecast


DISTRICTS = [
    {
        "name": "Hai Chau",
        "temperature": 32.0,
        "humidity": 79,
        "wind_speed": 21.0,
        "description": "Mua vua",
        "rain_mm": 23.5,
        "is_dangerous": True,
    },
    {
        "name": "Son Tra",
        "temperature": 31.0,
        "humidity": 75,
        "wind_speed": 28.0,
        "description": "Co gio",
        "rain_mm": 9.0,
        "is_dangerous": False,
    },
    {
        "name": "Thanh Khe",
        "temperature": 33.0,
        "humidity": 71,
        "wind_speed": 18.0,
        "description": "Nang nong",
        "rain_mm": 2.0,
        "is_dangerous": False,
    },
    {
        "name": "Lien Chieu",
        "temperature": 30.0,
        "humidity": 83,
        "wind_speed": 15.0,
        "description": "Nhieu may",
        "rain_mm": 12.0,
        "is_dangerous": False,
    },
    {
        "name": "Ngu Hanh Son",
        "temperature": 31.5,
        "humidity": 77,
        "wind_speed": 24.0,
        "description": "Mua rao",
        "rain_mm": 15.0,
        "is_dangerous": False,
    },
]

FORECAST_PATTERN = [
    (28, 34, "Nang nhe", 10, False, ""),
    (27, 33, "Nhieu may", 25, False, ""),
    (26, 32, "Mua rao", 60, False, ""),
    (26, 31, "Mua vua", 75, True, "Canh bao ngap ung mot so tuyen duong noi thanh."),
    (27, 32, "Co gio", 40, False, ""),
    (28, 34, "Nang nong", 15, False, ""),
    (26, 31, "Mua dong", 80, True, "Canh bao ngap ung tuyen pho Le Duan vao gio cao diem."),
]


class Command(BaseCommand):
    help = "Seed weather demo data for Da Nang districts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing weather data before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            WeatherForecast.objects.all().delete()
            WeatherData.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing weather data."))

        now = timezone.now()
        today = timezone.localdate()
        weather_created = 0
        weather_updated = 0
        forecast_created = 0
        forecast_updated = 0

        for district in DISTRICTS:
            location = f'{district["name"]}, Da Nang'
            _, created = WeatherData.objects.update_or_create(
                location=location,
                recorded_at=now.replace(minute=0, second=0, microsecond=0),
                defaults={
                    "temperature": district["temperature"],
                    "humidity": district["humidity"],
                    "wind_speed": district["wind_speed"],
                    "wind_direction": "NE",
                    "description": district["description"],
                    "icon": "",
                    "rain_mm": district["rain_mm"],
                    "pressure_hpa": 1007.0,
                    "is_dangerous": district["is_dangerous"],
                    "source": "seed_command",
                },
            )
            if created:
                weather_created += 1
            else:
                weather_updated += 1

            for day_offset, pattern in enumerate(FORECAST_PATTERN):
                temp_min, temp_max, description, rain_probability, is_warning, warning_message = pattern
                _, created = WeatherForecast.objects.update_or_create(
                    location=location,
                    forecast_date=today + timedelta(days=day_offset),
                    defaults={
                        "temp_min": temp_min,
                        "temp_max": temp_max,
                        "description": description,
                        "rain_probability": rain_probability,
                        "is_warning": is_warning,
                        "warning_message": warning_message,
                    },
                )
                if created:
                    forecast_created += 1
                else:
                    forecast_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seed completed. "
                f"Weather created/updated: {weather_created}/{weather_updated}; "
                f"Forecast created/updated: {forecast_created}/{forecast_updated}."
            )
        )
