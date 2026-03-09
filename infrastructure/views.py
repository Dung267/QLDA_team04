# infrastructure/views.py
from django.shortcuts import render, get_object_or_404
from .models import Road, Pothole, TrafficLight

def road_list(request):
    roads = Road.objects.all().order_by("name")
    return render(request, "infrastructure/road_list.html", {"roads": roads})


def road_detail(request, id):
    road = get_object_or_404(Road, id=id)
    potholes = getattr(road, "potholes", []).all() if hasattr(road, "potholes") else []
    return render(request, "infrastructure/road_detail.html", {
        "road": road,
        "potholes": potholes,
    })


def pothole_list(request):
    potholes = Pothole.objects.select_related("road").all().order_by("-created_at")
    return render(request, "infrastructure/pothole_list.html", {"potholes": potholes})


def traffic_light_status(request):
    traffic_lights = TrafficLight.objects.all().order_by("location_name")
    return render(request, "infrastructure/traffic_light_status.html", {"traffic_lights": traffic_lights})