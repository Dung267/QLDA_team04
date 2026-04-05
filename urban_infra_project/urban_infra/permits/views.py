from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import ConstructionPermit, PermitDocument
from accounts.decorators import staff_required
import uuid

@login_required
def permit_list(request):
    qs = ConstructionPermit.objects.select_related('applicant')
    if request.user.role == 'citizen':
        qs = qs.filter(applicant=request.user)
    status = request.GET.get('status','')
    q = request.GET.get('q','')
    if status: qs = qs.filter(status=status)
    if q: qs = qs.filter(Q(title__icontains=q)|Q(permit_number__icontains=q)|Q(location__icontains=q))
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'permits/list.html',{
        'page_obj':page,'status_choices':ConstructionPermit.STATUS_CHOICES,'page_title':'Giấy phép thi công'})

@login_required
def permit_create(request):
    from .forms import PermitForm
    if request.method=='POST':
        form = PermitForm(request.POST)
        if form.is_valid():
            permit = form.save(commit=False)
            permit.applicant = request.user
            permit.status = 'draft'
            permit.save()
            for f in request.FILES.getlist('documents'):
                PermitDocument.objects.create(permit=permit, name=f.name, file=f, uploaded_by=request.user)
            messages.success(request,'Đã tạo hồ sơ. Bạn có thể nộp hồ sơ khi đã hoàn chỉnh.')
            return redirect('permits:detail', pk=permit.pk)
    else:
        form = PermitForm()
    return render(request,'permits/form.html',{'form':form,'page_title':'Tạo hồ sơ xin phép'})

@login_required
def permit_detail(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)
    if request.user.role=='citizen' and permit.applicant!=request.user:
        messages.error(request,'Bạn không có quyền xem hồ sơ này.')
        return redirect('permits:list')
    return render(request,'permits/detail.html',{'permit':permit,'page_title':permit.title})

@login_required
def permit_submit(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk, applicant=request.user)
    if permit.status == 'draft':
        permit.status = 'submitted'
        permit.save()
        messages.success(request,'Đã nộp hồ sơ thành công.')
    return redirect('permits:detail', pk=pk)

@login_required
@staff_required
def permit_process(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)
    if request.method=='POST':
        action = request.POST.get('action')
        if action=='receive':
            permit.status='received'; permit.assigned_reviewer=request.user
        elif action=='approve':
            permit.status='approved'; permit.approved_by=request.user
            permit.issued_at=timezone.now()
            permit.permit_number = f"GP-{timezone.now().year}-{permit.pk:04d}"
        elif action=='reject':
            permit.status='rejected'; permit.rejection_reason=request.POST.get('reason','')
        elif action=='request_additional':
            permit.status='additional_required'; permit.additional_required=request.POST.get('note','')
        elif action=='warn':
            permit.violation_warning = request.POST.get('warning','')
        elif action=='suspend':
            permit.status='suspended'
        elif action=='complete':
            permit.status='completed'
        permit.save()
        messages.success(request,'Đã cập nhật hồ sơ.')
    return redirect('permits:detail', pk=pk)

@login_required
def permit_stats(request):
    from django.db.models import Count
    stats = {'by_status': list(ConstructionPermit.objects.values('status').annotate(count=Count('id')))}
    return render(request,'permits/stats.html',{'stats':stats,'page_title':'Thống kê giấy phép'})
