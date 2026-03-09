# maintenance/views.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404

from incidents.models import Incident
from .models import MaintenanceRequest

try:
    from .models import MaintenanceAssignment, MaintenanceProgress
except ImportError:
    MaintenanceAssignment = None
    MaintenanceProgress = None

User = get_user_model()

def create_maintenance_request(request):
    incidents = Incident.objects.all().order_by("-created_at")

    if request.method == "POST":
        incident_id = request.POST.get("incident_id")
        emergency = request.POST.get("emergency") == "on"
        priority = request.POST.get("priority", "MEDIUM")

        incident = get_object_or_404(Incident, id=incident_id)
        requested_by = request.user if request.user.is_authenticated else None

        MaintenanceRequest.objects.create(
            incident=incident,
            requested_by=requested_by,
            emergency=emergency,
            priority=priority,
            status="PENDING"
        )

        messages.success(request, "Đã tạo yêu cầu bảo trì.")
        return redirect("/maintenance/progress/")

    return render(request, "maintenance/create_request.html", {"incidents": incidents})


def assign_maintenance_task(request):
    requests_qs = MaintenanceRequest.objects.all().order_by("-created_at")
    staff = User.objects.all().order_by("username")

    if hasattr(User, "role"):
        staff = User.objects.filter(role__in=["TECHNICIAN", "OFFICER"]).order_by("username")

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        assigned_to_id = request.POST.get("assigned_to")
        note = request.POST.get("note", "").strip()

        req = get_object_or_404(MaintenanceRequest, id=request_id)
        assigned_to = get_object_or_404(User, id=assigned_to_id)

        if MaintenanceAssignment:
            MaintenanceAssignment.objects.filter(request=req, is_current=True).update(is_current=False)
            MaintenanceAssignment.objects.create(
                request=req,
                assigned_to=assigned_to,
                assigned_by=request.user if request.user.is_authenticated else assigned_to,
                note=note,
                is_current=True
            )

        req.status = "ASSIGNED"
        req.save()

        messages.success(request, "Đã phân công công việc.")
        return redirect("/maintenance/progress/")

    return render(request, "maintenance/assign.html", {
        "requests_qs": requests_qs,
        "staff": staff
    })


def update_progress(request):
    requests_qs = MaintenanceRequest.objects.all().order_by("-created_at")

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        status = request.POST.get("status", "IN_PROGRESS")
        note = request.POST.get("note", "").strip()

        req = get_object_or_404(MaintenanceRequest, id=request_id)
        req.status = status
        req.save()

        if MaintenanceProgress:
            MaintenanceProgress.objects.create(
                request=req,
                status=status,
                note=note
            )

        messages.success(request, "Đã cập nhật tiến độ.")
        return redirect("/maintenance/progress/")

    return render(request, "maintenance/progress.html", {"requests_qs": requests_qs})