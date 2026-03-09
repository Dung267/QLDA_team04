# incidents/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from infrastructure.models import Area
from .models import Incident

try:
    from .models import IncidentAttachment
except ImportError:
    IncidentAttachment = None

INCIDENT_TYPES = [
    ("ROAD_DAMAGE", "Đường hư hỏng"),
    ("FLOOD", "Ngập lụt"),
    ("TRAFFIC_LIGHT", "Đèn giao thông lỗi"),
    ("BRIDGE_DAMAGE", "Cầu hư hỏng"),
    ("OTHER", "Khác"),
]

def report_incident(request):
    areas = Area.objects.all()

    if request.method == "POST":
        area_id = request.POST.get("area")
        incident_type = request.POST.get("incident_type")
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if not area_id or not title or not description:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return render(request, "incidents/report.html", {
                "areas": areas,
                "incident_types": INCIDENT_TYPES,
            })

        area = get_object_or_404(Area, id=area_id)
        reporter = request.user if request.user.is_authenticated else None

        incident = Incident.objects.create(
            reporter=reporter,
            area=area,
            incident_type=incident_type,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            status="NEW",
            priority="MEDIUM",
        )

        uploaded_file = request.FILES.get("attachment")
        if uploaded_file and IncidentAttachment:
            file_type = "IMAGE" if uploaded_file.content_type.startswith("image/") else "VIDEO"
            IncidentAttachment.objects.create(
                incident=incident,
                file=uploaded_file,
                file_type=file_type
            )

        messages.success(request, "Đã gửi phản ánh thành công.")
        return redirect("/incidents/list/")

    return render(request, "incidents/report.html", {
        "areas": areas,
        "incident_types": INCIDENT_TYPES,
    })


def incident_list(request):
    incidents = Incident.objects.all().order_by("-created_at")

    status = request.GET.get("status")
    if status:
        incidents = incidents.filter(status=status)

    incident_type = request.GET.get("incident_type")
    if incident_type:
        incidents = incidents.filter(incident_type=incident_type)

    return render(request, "incidents/list.html", {
        "incidents": incidents,
        "incident_types": INCIDENT_TYPES,
    })


def incident_detail(request, id):
    incident = get_object_or_404(Incident, id=id)
    attachments = getattr(incident, "attachments", []).all() if hasattr(incident, "attachments") else []
    return render(request, "incidents/detail.html", {
        "incident": incident,
        "attachments": attachments,
    })