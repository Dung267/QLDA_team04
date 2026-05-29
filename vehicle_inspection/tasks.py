from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from notifications.models import Notification

from .models import Inspection


@shared_task(name="vehicle_inspection.tasks.notify_expiring_inspections")
def notify_expiring_inspections(days=30):
    today = timezone.localdate()
    deadline = today + timedelta(days=days)
    created = 0

    inspections = (
        Inspection.objects.select_related("vehicle", "vehicle__owner")
        .filter(
            status="passed",
            valid_until__isnull=False,
            valid_until__gte=today,
            valid_until__lte=deadline,
        )
        .order_by("valid_until")
    )

    for inspection in inspections:
        owner = inspection.vehicle.owner
        days_left = (inspection.valid_until - today).days
        title = f"Phuong tien {inspection.vehicle.license_plate} sap het han dang kiem"
        _, was_created = Notification.objects.get_or_create(
            recipient=owner,
            title=title,
            notification_type="reminder",
            related_object_id=inspection.id,
            defaults={
                "message": (
                    f"Giay chung nhan dang kiem het han vao "
                    f"{inspection.valid_until:%d/%m/%Y}, con {days_left} ngay."
                ),
                "action_url": f"/vehicle-inspection/{inspection.id}/",
            },
        )
        if was_created:
            created += 1

    return {
        "checked": inspections.count(),
        "created": created,
    }
