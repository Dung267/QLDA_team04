from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import ConstructionPermit, PermitDocument
from accounts.decorators import staff_required


@login_required
def permit_list(request):
    permits = ConstructionPermit.objects.all()
    if request.user.role == 'citizen':
        permits = permits.filter(applicant=request.user)
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status:
        permits = permits.filter(status=status)
    if q:
        permits = permits.filter(Q(project_name__icontains=q) | Q(permit_number__icontains=q))
    paginator = Paginator(permits, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'permits/list.html', {
        'page_obj': page, 'status_choices': ConstructionPermit.STATUS_CHOICES,
        'page_title': 'Giấy phép thi công',
    })


@login_required
def permit_create(request):
    from .forms import PermitForm
    if request.method == 'POST':
        form = PermitForm(request.POST)
        if form.is_valid():
            permit = form.save(commit=False)
            permit.applicant = request.user
            permit.save()
            for f in request.FILES.getlist('documents'):
                PermitDocument.objects.create(
                    permit=permit, file=f,
                    doc_type=request.POST.get('doc_type', 'Tài liệu'),
                    uploaded_by=request.user
                )
            messages.success(request, f'Đã tạo hồ sơ xin phép.')
            return redirect('permits:detail', pk=permit.pk)
    else:
        form = PermitForm()
    return render(request, 'permits/form.html', {'form': form, 'page_title': 'Xin giấy phép thi công'})


@login_required
def permit_detail(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)
    if request.user.role == 'citizen' and permit.applicant != request.user:
        messages.error(request, 'Không có quyền truy cập.')
        return redirect('permits:list')
    return render(request, 'permits/detail.html', {'permit': permit, 'page_title': permit.project_name})


@login_required
def permit_submit(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk, applicant=request.user, status='draft')
    permit.status = 'submitted'
    permit.save()
    messages.success(request, 'Đã nộp hồ sơ xin phép.')
    return redirect('permits:detail', pk=pk)


@login_required
@staff_required
def permit_process(request, pk):
    permit = get_object_or_404(ConstructionPermit, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'receive':
            permit.status = 'received'
            permit.assigned_officer = request.user
        elif action == 'approve':
            permit.status = 'approved'
        elif action == 'issue':
            permit.status = 'issued'
            permit.issued_at = timezone.now()
        elif action == 'reject':
            permit.status = 'rejected'
            permit.rejection_reason = request.POST.get('reason', '')
        elif action == 'additional':
            permit.status = 'additional_needed'
            permit.additional_required = request.POST.get('additional', '')
        permit.save()
        messages.success(request, 'Đã cập nhật trạng thái hồ sơ.')
    return redirect('permits:detail', pk=pk)


@login_required
@staff_required
def permit_stats(request):
    from django.db.models import Count
    stats = {
        'by_status': list(ConstructionPermit.objects.values('status').annotate(c=Count('id'))),
        'by_type': list(ConstructionPermit.objects.values('permit_type').annotate(c=Count('id'))),
        'total': ConstructionPermit.objects.count(),
        'pending': ConstructionPermit.objects.filter(status__in=['submitted', 'received', 'legal_check']).count(),
    }
    return render(request, 'permits/stats.html', {'stats': stats, 'page_title': 'Thống kê giấy phép'})
