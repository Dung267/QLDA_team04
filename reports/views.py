# reports/views.py
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from django.shortcuts import render

from infrastructure.models import Road, Pothole, TrafficLight
from incidents.models import Incident
from maintenance.models import MaintenanceRequest

def summary_report(request):
    summary = {
        "total_incidents": Incident.objects.count(),
        "total_roads": Road.objects.count(),
        "total_potholes": Pothole.objects.count(),
        "total_traffic_lights": TrafficLight.objects.count(),
        "total_maintenance_requests": MaintenanceRequest.objects.count(),
    }
    return render(request, "reports/summary.html", {"summary": summary})


def monthly_report(request):
    incident_stats = Incident.objects.annotate(period=TruncMonth("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")
    maintenance_stats = MaintenanceRequest.objects.annotate(period=TruncMonth("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")

    return render(request, "reports/monthly.html", {
        "incident_stats": incident_stats,
        "maintenance_stats": maintenance_stats,
    })


def quarterly_report(request):
    incident_stats = Incident.objects.annotate(period=TruncQuarter("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")
    maintenance_stats = MaintenanceRequest.objects.annotate(period=TruncQuarter("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")

    return render(request, "reports/quarterly.html", {
        "incident_stats": incident_stats,
        "maintenance_stats": maintenance_stats,
    })


def yearly_report(request):
    incident_stats = Incident.objects.annotate(period=TruncYear("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")
    maintenance_stats = MaintenanceRequest.objects.annotate(period=TruncYear("created_at")) \
        .values("period").annotate(total=Count("id")).order_by("period")

    return render(request, "reports/yearly.html", {
        "incident_stats": incident_stats,
        "maintenance_stats": maintenance_stats,
    })