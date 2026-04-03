from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    from maintenance.models import MaintenanceRequest
    from infrastructure.models import Road, TrafficLight
    from notifications.models import Notification
    from flood.models import FloodAlert
    from vehicle_inspection.models import Inspection

    now = timezone.now()
    today = now.date()
    month_start = today.replace(day=1)

    # Thống kê tổng quan
    stats = {
        'total_roads': Road.objects.count(),
        'total_lights': TrafficLight.objects.count(),
        'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').count(),
        'in_progress_maintenance': MaintenanceRequest.objects.filter(status='in_progress').count(),
        'completed_this_month': MaintenanceRequest.objects.filter(
            status='completed',
            completed_at__date__gte=month_start
        ).count(),
        'active_flood_alerts': FloodAlert.objects.filter(is_active=True).count(),
        'unread_notifications': Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
        'pending_inspections': Inspection.objects.filter(status='pending').count(),
    }

    # Phản ánh gần đây
    recent_requests = MaintenanceRequest.objects.select_related(
        'infrastructure', 'reported_by'
    ).order_by('-created_at')[:10]

    # Cảnh báo ngập lụt đang hoạt động
    flood_alerts = FloodAlert.objects.filter(is_active=True).order_by('-created_at')[:5]

    # Thông báo chưa đọc
    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')[:5]

    # Thống kê sự cố 7 ngày gần đây
    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = MaintenanceRequest.objects.filter(created_at__date=day).count()
        last_7_days.append({'date': day.strftime('%d/%m'), 'count': count})

    context = {
        'stats': stats,
        'recent_requests': recent_requests,
        'flood_alerts': flood_alerts,
        'notifications': notifications,
        'last_7_days': last_7_days,
        'page_title': 'Bảng điều khiển',
    }
    return render(request, 'dashboard.html', context)


def home(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'home.html')