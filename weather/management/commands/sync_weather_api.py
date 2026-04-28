from django.core.management.base import BaseCommand

from weather.services import DISTRICT_COORDINATES, fetch_and_store_weather


class Command(BaseCommand):
    help = "Fetch live weather data from Open-Meteo for Da Nang districts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--district",
            type=str,
            help="Sync one district only. Example: Hai Chau",
        )

    def handle(self, *args, **options):
        district = options.get("district")
        districts = [district] if district else list(DISTRICT_COORDINATES.keys())
        synced = 0
        failed = 0
        for item in districts:
            try:
                fetch_and_store_weather(item)
                synced += 1
                self.stdout.write(self.style.SUCCESS(f"Synced: {item}, Da Nang"))
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.WARNING(f"Failed: {item} ({exc})"))
        self.stdout.write(
            self.style.SUCCESS(f"Completed. Synced={synced}, Failed={failed}")
        )
