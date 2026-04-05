from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import FloodAlert, DisasterUpdate
from accounts.decorators import staff_required

@login_required
def alert_list(request):
    alerts = FloodAlert.objects.all()
    active_only = request.GET.get('active','')
    if active_only:
        alerts = alerts.filter(is_active=True)
    paginator = Paginator(alerts, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'flood/alert_list.html',{'page_obj':page,'page_title':'Cảnh báo ngập lụt'})

@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(FloodAlert, pk=pk)
    return render(request,'flood/alert_detail.html',{'alert':alert,'page_title':alert.title})

@login_required
@staff_required
def alert_create(request):
    from .forms import FloodAlertForm
    if request.method=='POST':
        form = FloodAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            _broadcast_alert(alert)
            messages.success(request,'Đã tạo cảnh báo ngập lụt.')
            return redirect('flood:alert_detail', pk=alert.pk)
    else:
        form = FloodAlertForm()
    return render(request,'flood/alert_form.html',{'form':form,'page_title':'Tạo cảnh báo'})

@login_required
@staff_required
def alert_resolve(request, pk):
    from django.utils import timezone
    alert = get_object_or_404(FloodAlert, pk=pk)
    alert.is_active = False
    alert.resolved_at = timezone.now()
    alert.save()
    messages.success(request,'Đã đánh dấu hết cảnh báo.')
    return redirect('flood:alert_list')

@login_required
def active_alerts_api(request):
    alerts = FloodAlert.objects.filter(is_active=True).values(
        'id','title','level','area_name','latitude','longitude','water_level_cm','created_at'
    )
    return JsonResponse({'alerts': list(alerts)})

def _broadcast_alert(alert):
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        import json
        layer = get_channel_layer()
        async_to_sync(layer.group_send)('flood_alerts', {
            'type': 'flood_alert',
            'data': {'id': alert.id, 'title': alert.title, 'level': alert.level, 'area': alert.area_name}
        })
    except Exception:
        pass
