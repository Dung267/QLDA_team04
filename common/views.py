# common/views.py
from django.db import connections
from django.shortcuts import render
import django
import sys

def system_health(request):
    db_status = "OK"
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_status = "ERROR"

    context = {
        "status": "RUNNING",
        "db_status": db_status,
        "django_version": django.get_version(),
        "python_version": sys.version.split()[0],
    }
    return render(request, "common/system_health.html", context)