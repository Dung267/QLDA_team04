# audit/views.py
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.shortcuts import render

def view_logs(request):
    logs = LogEntry.objects.select_related("user", "content_type").order_by("-action_time")[:50]
    return render(request, "audit/logs.html", {"logs": logs})


def view_changes(request):
    changes = LogEntry.objects.select_related("user", "content_type").filter(
        action_flag__in=[ADDITION, CHANGE, DELETION]
    ).order_by("-action_time")[:50]
    return render(request, "audit/changes.html", {"changes": changes})