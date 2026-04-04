from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Road, Pothole, RoadRepairHistory, TrafficLight, Infrastructure, ManagementZone
from .forms import RoadForm, PotholeForm, TrafficLightForm, InfrastructureForm


@login_required
def road_list(request):
    roads = Road.objects.select_related('zone').all()
    q = request.GET.get('q', '')
    zone = request.GET.get('zone', '')
    status = request.GET.get('status', '')
    if q:
        roads = roads.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if zone:
        roads = roads.filter(zone_id=zone)
    if status:
        roads = roads.filter(status=status)
    paginator = Paginator(roads.order_by('name'), 20)
    page = paginator.get_page(request.GET.get('page', 1))
    zones = ManagementZone.objects.all()
    return render(request, 'infrastructure/road_list.html', {
        'page_obj': page, 'zones': zones,
        'status_choices': Road.STATUS_CHOICES,
        'page_title': 'Danh sách tuyến đường',
    })


@login_required
def road_detail(request, pk):
    road = get_object_or_404(Road, pk=pk)
    potholes = road.potholes.all().order_by('-created_at')
    repair_history = road.repair_history.all().order_by('-repair_date')
    traffic_lights = road.traffic_lights.all()
    return render(request, 'infrastructure/road_detail.html', {
        'road': road, 'potholes': potholes,
        'repair_history': repair_history,
        'traffic_lights': traffic_lights,
        'page_title': road.name,
    })


@login_required
def road_create(request):
    if request.method == 'POST':
        form = RoadForm(request.POST)
        if form.is_valid():
            road = form.save(commit=False)
            road.created_by = request.user
            road.save()
            messages.success(request, f'Đã thêm tuyến đường {road.name}.')
            return redirect('infrastructure:road_detail', pk=road.pk)
    else:
        form = RoadForm()
    return render(request, 'infrastructure/road_form.html', {'form': form, 'page_title': 'Thêm tuyến đường'})


@login_required
def road_edit(request, pk):
    road = get_object_or_404(Road, pk=pk)
    if request.method == 'POST':
        form = RoadForm(request.POST, instance=road)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật tuyến đường.')
            return redirect('infrastructure:road_detail', pk=road.pk)
    else:
        form = RoadForm(instance=road)
    return render(request, 'infrastructure/road_form.html', {'form': form, 'road': road, 'page_title': 'Sửa tuyến đường'})


@login_required
def pothole_create(request, road_pk):
    road = get_object_or_404(Road, pk=road_pk)
    if request.method == 'POST':
        form = PotholeForm(request.POST, request.FILES)
        if form.is_valid():
            pothole = form.save(commit=False)
            pothole.road = road
            pothole.reported_by = request.user
            pothole.save()
            messages.success(request, 'Đã ghi nhận ổ gà.')
            return redirect('infrastructure:road_detail', pk=road_pk)
    else:
        form = PotholeForm()
    return render(request, 'infrastructure/pothole_form.html', {'form': form, 'road': road})


@login_required
def pothole_edit(request, pk):
    pothole = get_object_or_404(Pothole, pk=pk)
    if request.method == 'POST':
        form = PotholeForm(request.POST, request.FILES, instance=pothole)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật ổ gà.')
            return redirect('infrastructure:road_detail', pk=pothole.road_id)
    else:
        form = PotholeForm(instance=pothole)
    return render(request, 'infrastructure/pothole_form.html', {'form': form, 'pothole': pothole})


@login_required
def traffic_light_list(request):
    lights = TrafficLight.objects.select_related('road', 'zone').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        lights = lights.filter(Q(code__icontains=q) | Q(location__icontains=q))
    if status:
        lights = lights.filter(status=status)
    paginator = Paginator(lights, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'infrastructure/traffic_light_list.html', {
        'page_obj': page, 'status_choices': TrafficLight.STATUS_CHOICES,
        'page_title': 'Đèn giao thông',
    })


@login_required
def traffic_light_detail(request, pk):
    light = get_object_or_404(TrafficLight, pk=pk)
    return render(request, 'infrastructure/traffic_light_detail.html', {'light': light})


@login_required
def infrastructure_list(request):
    items = Infrastructure.objects.select_related('type', 'zone').all()
    q = request.GET.get('q', '')
    zone = request.GET.get('zone', '')
    if q:
        items = items.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if zone:
        items = items.filter(zone_id=zone)
    paginator = Paginator(items, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'infrastructure/infra_list.html', {
        'page_obj': page,
        'zones': ManagementZone.objects.all(),
        'page_title': 'Danh sách hạ tầng',
    })


@login_required
def infrastructure_detail(request, pk):
    item = get_object_or_404(Infrastructure, pk=pk)
    return render(request, 'infrastructure/infra_detail.html', {'item': item, 'page_title': item.name})


@login_required
def infrastructure_stats(request):
    from django.db.models import Count, Avg
    stats = {
        'total_roads': Road.objects.count(),
        'roads_by_status': dict(Road.objects.values_list('status').annotate(c=Count('id'))),
        'total_potholes': Pothole.objects.count(),
        'unrepaired_potholes': Pothole.objects.filter(is_repaired=False).count(),
        'total_lights': TrafficLight.objects.count(),
        'lights_by_status': dict(TrafficLight.objects.values_list('status').annotate(c=Count('id'))),
        'total_infra': Infrastructure.objects.count(),
        'infra_by_status': dict(Infrastructure.objects.values_list('status').annotate(c=Count('id'))),
    }
    return render(request, 'infrastructure/stats.html', {'stats': stats, 'page_title': 'Thống kê hạ tầng'})
