from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import FloodAlert, DisasterUpdate
from accounts.decorators import staff_required


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _build_stats():
    """Trả về dict thống kê tổng hợp cho dashboard."""
    qs = FloodAlert.objects.all()
    return {
        'active':    qs.filter(is_active=True).count(),
        'level3_4':  qs.filter(is_active=True, level__in=['3', '4']).count(),
        'resolved':  qs.filter(is_active=False).count(),
        'sms_sent':  qs.filter(is_sent_sms=True).count(),
    }


def _broadcast_alert(alert):
    """Phát WebSocket broadcast khi tạo/cập nhật cảnh báo."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        layer = get_channel_layer()
        async_to_sync(layer.group_send)('flood_alerts', {
            'type': 'flood_alert',
            'data': {
                'id': alert.id,
                'title': alert.title,
                'level': alert.level,
                'area': alert.area_name,
            }
        })
    except Exception:
        pass


def _apply_filters(qs, params):
    """Áp dụng bộ lọc từ query params vào queryset FloodAlert."""
    level = params.get('level', '').strip()
    if level in ['1', '2', '3', '4']:
        qs = qs.filter(level=level)

    area_type = params.get('area_type', '').strip()
    if area_type:
        qs = qs.filter(area_type=area_type)

    active = params.get('active', '').strip()
    if active == '1':
        qs = qs.filter(is_active=True)
    elif active == '0':
        qs = qs.filter(is_active=False)

    date_from = params.get('date_from', '').strip()
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)

    return qs


# ─────────────────────────────────────────────
# Views
# ─────────────────────────────────────────────

@login_required
def alert_list(request):
    qs = FloodAlert.objects.select_related('created_by').all()
    qs = _apply_filters(qs, request.GET)

    # Banner cảnh báo khẩn cấp cấp 3-4 đang hoạt động
    critical_alert = (
        FloodAlert.objects.filter(is_active=True, level__in=['3', '4'])
        .order_by('-level', '-created_at')
        .first()
    )

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'flood/alert_list.html', {
        'page_obj':       page,
        'page_title':     'Cảnh báo ngập lụt',
        'stats':          _build_stats(),
        'critical_alert': critical_alert,
        'level_choices':  FloodAlert.LEVEL_CHOICES,  # [('1','Cấp 1 - Theo dõi'), ...]
    })


@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(
        FloodAlert.objects.select_related('created_by'), pk=pk
    )
    # Lịch sử cập nhật thiên tai liên quan (dùng DisasterUpdate nếu có quan hệ)
    # Hiện tại DisasterUpdate không FK đến FloodAlert nên để queryset rỗng
    updates = DisasterUpdate.objects.none()

    return render(request, 'flood/alert_detail.html', {
        'alert':      alert,
        'page_title': alert.title,
        'updates':    updates,
    })


@login_required
@staff_required
def alert_create(request):
    from .forms import FloodAlertForm
    if request.method == 'POST':
        form = FloodAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            _broadcast_alert(alert)
            messages.success(request, '✅ Đã phát lệnh cảnh báo ngập lụt thành công.')
            return redirect('flood:alert_detail', pk=alert.pk)
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin bên dưới.')
    else:
        form = FloodAlertForm()

    return render(request, 'flood/alert_form.html', {
        'form':       form,
        'page_title': 'Phát lệnh cảnh báo ngập lụt',
        'object':     None,
    })


@login_required
@staff_required
def alert_edit(request, pk):
    alert = get_object_or_404(FloodAlert, pk=pk)
    from .forms import FloodAlertForm
    if request.method == 'POST':
        form = FloodAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            _broadcast_alert(alert)
            messages.success(request, '✅ Đã cập nhật cảnh báo ngập lụt.')
            return redirect('flood:alert_detail', pk=alert.pk)
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin bên dưới.')
    else:
        form = FloodAlertForm(instance=alert)

    return render(request, 'flood/alert_form.html', {
        'form':       form,
        'page_title': f'Cập nhật cảnh báo: {alert.title}',
        'object':     alert,
    })


@login_required
@staff_required
def alert_resolve(request, pk):
    alert = get_object_or_404(FloodAlert, pk=pk)
    if request.method == 'POST':
        alert.is_active = False
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, '✅ Đã đánh dấu hết cảnh báo ngập lụt.')
    return redirect('flood:alert_list')


@login_required
@staff_required
def alert_send_sms(request, pk):
    """Đánh dấu đã gửi SMS; tích hợp SMS gateway thực ở đây."""
    alert = get_object_or_404(FloodAlert, pk=pk)
    if request.method == 'POST':
        # TODO: gọi SMS gateway thực (Twilio / ESMS / Viettel)
        alert.is_sent_sms = True
        alert.save(update_fields=['is_sent_sms'])
        messages.success(request, '📱 Đã gửi SMS cảnh báo đến người dân trong khu vực.')
    return redirect('flood:alert_detail', pk=pk)


@login_required
@staff_required
def alert_notify_rescue(request, pk):
    """Đánh dấu đã thông báo đội cứu hộ."""
    alert = get_object_or_404(FloodAlert, pk=pk)
    if request.method == 'POST':
        # TODO: gọi API thông báo đội cứu hộ
        alert.rescue_teams_notified = True
        alert.save(update_fields=['rescue_teams_notified'])
        messages.success(request, '🚒 Đã thông báo đội cứu hộ.')
    return redirect('flood:alert_detail', pk=pk)


@login_required
@staff_required
def alert_add_update(request, pk):
    """Thêm cập nhật tình hình thiên tai cho một cảnh báo."""
    alert = get_object_or_404(FloodAlert, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            DisasterUpdate.objects.create(
                title=f'Cập nhật: {alert.title}',
                content=content,
                disaster_type='flood',
                is_published=True,
                created_by=request.user,
            )
            messages.success(request, '✅ Đã thêm cập nhật tình hình.')
        else:
            messages.error(request, 'Nội dung cập nhật không được để trống.')
    return redirect('flood:alert_detail', pk=pk)


@login_required
def active_alerts_api(request):
    """API JSON trả về danh sách cảnh báo đang hoạt động (dùng cho bản đồ)."""
    alerts = FloodAlert.objects.filter(is_active=True).values(
        'id', 'title', 'level', 'area_name', 'area_type',
        'latitude', 'longitude', 'water_level_cm', 'created_at',
    )
    return JsonResponse({'alerts': list(alerts)})