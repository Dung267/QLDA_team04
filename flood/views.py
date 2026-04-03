from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import FloodAlert, DisasterAlert
from .forms import FloodAlertForm, DisasterAlertForm
from accounts.decorators import staff_required


def flood_alert_list(request):
    alerts = FloodAlert.objects.filter(is_active=True).order_by('-created_at')
    district = request.GET.get('district', '')
    level = request.GET.get('level', '')
    if district:
        alerts = alerts.filter(district__icontains=district)
    if level:
        alerts = alerts.filter(level=level)
    return render(request, 'flood/alert_list.html', {
        'alerts': alerts,
        'level_choices': FloodAlert.LEVEL_CHOICES,
        'page_title': 'Cảnh báo ngập lụt',
    })


def flood_alert_detail(request, pk):
    alert = get_object_or_404(FloodAlert, pk=pk)
    return render(request, 'flood/alert_detail.html', {'alert': alert, 'page_title': alert.area_name})


@login_required
@staff_required
def flood_alert_create(request):
    if request.method == 'POST':
        form = FloodAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            # Gửi thông báo khẩn
            _broadcast_flood_alert(alert)
            messages.success(request, 'Đã phát cảnh báo ngập lụt.')
            return redirect('flood:alert_list')
    else:
        form = FloodAlertForm()
    return render(request, 'flood/alert_form.html', {'form': form, 'page_title': 'Tạo cảnh báo ngập lụt'})


@login_required
@staff_required
def flood_alert_update(request, pk):
    alert = get_object_or_404(FloodAlert, pk=pk)
    if request.method == 'POST':
        form = FloodAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật cảnh báo.')
            return redirect('flood:alert_list')
    else:
        form = FloodAlertForm(instance=alert)
    return render(request, 'flood/alert_form.html', {'form': form, 'alert': alert})


@login_required
@staff_required
def resolve_alert(request, pk):
    from django.utils import timezone
    alert = get_object_or_404(FloodAlert, pk=pk)
    alert.is_active = False
    alert.resolved_at = timezone.now()
    alert.save()
    messages.success(request, 'Đã đóng cảnh báo ngập lụt.')
    return redirect('flood:alert_list')


def disaster_alert_list(request):
    alerts = DisasterAlert.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'flood/disaster_list.html', {'alerts': alerts, 'page_title': 'Cảnh báo thiên tai'})


@login_required
@staff_required
def disaster_alert_create(request):
    if request.method == 'POST':
        form = DisasterAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            messages.success(request, 'Đã tạo cảnh báo thiên tai.')
            return redirect('flood:disaster_list')
    else:
        form = DisasterAlertForm()
    return render(request, 'flood/disaster_form.html', {'form': form, 'page_title': 'Tạo cảnh báo thiên tai'})


def flood_map_api(request):
    alerts = FloodAlert.objects.filter(is_active=True).values(
        'id', 'area_name', 'level', 'latitude', 'longitude', 'water_level_cm'
    )
    return JsonResponse({'alerts': list(alerts)})


def _broadcast_flood_alert(alert):
    from notifications.models import Notification
    from accounts.models import User
    users = User.objects.filter(district=alert.district, is_active=True)
    notifs = [
        Notification(
            recipient=u,
            title=f'⚠️ Cảnh báo ngập lụt - {alert.area_name}',
            message=alert.description,
            notification_type='flood',
            related_object_id=alert.pk,
        ) for u in users
    ]
    Notification.objects.bulk_create(notifs)
