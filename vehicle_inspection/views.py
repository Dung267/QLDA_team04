from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Vehicle, Inspection, InspectionCenter
from .forms import VehicleForm, InspectionBookingForm
from accounts.decorators import staff_required


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(owner=request.user)
    return render(request, 'vehicle_inspection/vehicle_list.html', {
        'vehicles': vehicles, 'page_title': 'Phương tiện của tôi'
    })


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, 'Đã đăng ký phương tiện.')
            return redirect('vehicle_inspection:vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'vehicle_inspection/vehicle_form.html', {'form': form, 'page_title': 'Đăng ký phương tiện'})


@login_required
def book_inspection(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, owner=request.user)
    if request.method == 'POST':
        form = InspectionBookingForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.vehicle = vehicle
            inspection.save()
            messages.success(request, f'Đã đặt lịch đăng kiểm ngày {inspection.scheduled_date}.')
            return redirect('vehicle_inspection:inspection_list')
    else:
        form = InspectionBookingForm()
    centers = InspectionCenter.objects.filter(is_active=True)
    return render(request, 'vehicle_inspection/book.html', {
        'form': form, 'vehicle': vehicle, 'centers': centers,
        'page_title': 'Đặt lịch đăng kiểm',
    })


@login_required
def inspection_list(request):
    inspections = Inspection.objects.filter(vehicle__owner=request.user).select_related('vehicle', 'center')
    if request.user.is_staff_member:
        inspections = Inspection.objects.all().select_related('vehicle', 'center')
    status = request.GET.get('status', '')
    if status:
        inspections = inspections.filter(status=status)
    paginator = Paginator(inspections, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'vehicle_inspection/inspection_list.html', {
        'page_obj': page, 'status_choices': Inspection.STATUS_CHOICES,
        'page_title': 'Lịch sử đăng kiểm',
    })


@login_required
def inspection_detail(request, pk):
    inspection = get_object_or_404(Inspection, pk=pk)
    return render(request, 'vehicle_inspection/inspection_detail.html', {
        'inspection': inspection, 'page_title': f'Đăng kiểm {inspection.vehicle.plate_number}'
    })


@login_required
@staff_required
def inspection_process(request, pk):
    inspection = get_object_or_404(Inspection, pk=pk)
    if request.method == 'POST':
        result = request.POST.get('result')
        inspection.defects = request.POST.get('defects', '')
        inspection.result_notes = request.POST.get('notes', '')
        if result == 'passed':
            inspection.status = 'passed'
            inspection.certificate_number = f"CN{timezone.now().strftime('%Y%m%d')}{inspection.pk}"
            from datetime import timedelta
            inspection.valid_until = timezone.now().date() + timedelta(days=365)
        else:
            inspection.status = 'failed'
            inspection.repair_required = request.POST.get('repair_required', '')
        inspection.inspector = request.user
        inspection.save()
        messages.success(request, f'Đã cập nhật kết quả đăng kiểm.')
    return redirect('vehicle_inspection:inspection_detail', pk=pk)


@login_required
@staff_required
def inspection_stats(request):
    from django.db.models import Count
    stats = {
        'by_status': list(Inspection.objects.values('status').annotate(c=Count('id'))),
        'total': Inspection.objects.count(),
        'passed_this_month': Inspection.objects.filter(
            status='passed', updated_at__month=timezone.now().month
        ).count(),
    }
    return render(request, 'vehicle_inspection/stats.html', {'stats': stats, 'page_title': 'Thống kê đăng kiểm'})
