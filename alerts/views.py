# alerts/views.py
from django.contrib import messages
from django.shortcuts import render, redirect

def flood_warning(request):
    alerts = request.session.get("demo_flood_alerts", [])

    if request.method == "POST":
        location = request.POST.get("location", "").strip()
        severity = request.POST.get("severity", "LOW")
        note = request.POST.get("note", "").strip()

        if not location:
            messages.error(request, "Vui lòng nhập khu vực.")
            return render(request, "alerts/flood_warning.html", {"alerts": alerts})

        alerts.insert(0, {
            "location": location,
            "severity": severity,
            "note": note,
        })
        request.session["demo_flood_alerts"] = alerts
        request.session.modified = True

        messages.success(request, "Đã tạo cảnh báo ngập lụt.")
        return redirect("/alerts/flood-warning/")

    return render(request, "alerts/flood_warning.html", {"alerts": alerts})


def emergency_alert(request):
    alerts = request.session.get("demo_emergency_alerts", [])

    if request.method == "POST":
        disaster_type = request.POST.get("disaster_type", "").strip()
        location = request.POST.get("location", "").strip()
        level = request.POST.get("level", "MEDIUM")

        if not disaster_type or not location:
            messages.error(request, "Vui lòng nhập đầy đủ loại sự cố và khu vực.")
            return render(request, "alerts/emergency_alert.html", {"alerts": alerts})

        alerts.insert(0, {
            "disaster_type": disaster_type,
            "location": location,
            "level": level,
        })
        request.session["demo_emergency_alerts"] = alerts
        request.session.modified = True

        messages.success(request, "Đã tạo cảnh báo khẩn cấp.")
        return redirect("/alerts/emergency-alert/")

    return render(request, "alerts/emergency_alert.html", {"alerts": alerts})