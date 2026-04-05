from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from infrastructure.models import Road, TrafficLight, Infrastructure
from maintenance.models import MaintenanceRequest
from flood.models import FloodAlert

@login_required
def map_view(request):
    return render(request,'maps/map.html',{'page_title':'Bản đồ hạ tầng'})

@login_required
def map_data_api(request):
    layer = request.GET.get('layer','all')
    data = {}
    if layer in ('all','roads'):
        data['roads'] = list(Road.objects.filter(
            latitude__isnull=False).values('id','name','status','latitude','longitude','direction'))
    if layer in ('all','lights'):
        data['lights'] = list(TrafficLight.objects.filter(
            latitude__isnull=False).values('id','code','location','status','latitude','longitude'))
    if layer in ('all','incidents'):
        data['incidents'] = list(MaintenanceRequest.objects.filter(
            latitude__isnull=False, status__in=['pending','received','assigned','in_progress']
        ).values('id','title','incident_type','priority','latitude','longitude'))
    if layer in ('all','floods'):
        data['floods'] = list(FloodAlert.objects.filter(
            is_active=True, latitude__isnull=False
        ).values('id','title','level','area_name','latitude','longitude'))
    return JsonResponse(data)
