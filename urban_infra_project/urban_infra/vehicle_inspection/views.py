from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Vehicle, Inspection, InspectionCenter
from accounts.decorators import staff_required

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(owner=request.user, is_active=True)
    return render(request,'vehicle_inspection/vehicle_list.html',{'vehicles':vehicles,'page_title':'Phương tiện'})

@login_required
def vehicle_create(request):
    from .forms import VehicleForm
    if request.method=='POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.owner = request.user
            v.save()
            messages.success(request,'Đã đăng ký phương tiện.')
            return redirect('vehicle_inspection:vehicle_list')
    else:
        form = VehicleForm()
    return render(request,'vehicle_inspection/vehicle_form.html',{'form':form,'page_title':'Đăng ký xe'})

@login_required
def inspection_list(request):
    if request.user.is_staff_member:
        qs = Inspection.objects.select_related('vehicle','center').all()
    else:
        qs = Inspection.objects.filter(vehicle__owner=request.user)
    status = request.GET.get('status','')
    if status: qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'vehicle_inspection/inspection_list.html',{
        'page_obj':page,'status_choices':Inspection.STATUS_CHOICES,'page_title':'Lịch đăng kiểm'})

@login_required
def schedule_inspection(request):
    from .forms import InspectionForm
    if request.method=='POST':
        form = InspectionForm(request.POST)
        if form.is_valid():
            insp = form.save()
            messages.success(request,f'Đã đặt lịch đăng kiểm. Mã: #{insp.pk}')
            return redirect('vehicle_inspection:inspection_list')
    else:
        form = InspectionForm()
        form.fields['vehicle'].queryset = Vehicle.objects.filter(owner=request.user, is_active=True)
    return render(request,'vehicle_inspection/schedule_form.html',{'form':form,'page_title':'Đặt lịch đăng kiểm'})

@login_required
def cancel_inspection(request, pk):
    insp = get_object_or_404(Inspection, pk=pk, vehicle__owner=request.user)
    if insp.status == 'pending':
        insp.status = 'cancelled'
        insp.save()
        messages.success(request,'Đã hủy lịch đăng kiểm.')
    return redirect('vehicle_inspection:inspection_list')

@login_required
@staff_required
def update_inspection(request, pk):
    insp = get_object_or_404(Inspection, pk=pk)
    if request.method=='POST':
        insp.status = request.POST.get('status', insp.status)
        insp.technical_notes = request.POST.get('technical_notes','')
        insp.defects = request.POST.get('defects','')
        insp.repair_required = request.POST.get('repair_required','')
        if request.POST.get('certificate_number'):
            insp.certificate_number = request.POST.get('certificate_number')
        insp.inspector = request.user
        insp.save()
        messages.success(request,'Đã cập nhật kết quả đăng kiểm.')
    return redirect('vehicle_inspection:inspection_list')

@login_required
def pay_fee(request, pk):
    insp = get_object_or_404(Inspection, pk=pk, vehicle__owner=request.user)
    insp.is_fee_paid = True
    insp.save()
    messages.success(request,'Đã xác nhận thanh toán.')
    return redirect('vehicle_inspection:inspection_list')
