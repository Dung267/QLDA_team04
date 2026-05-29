from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Contract, Tender, Contractor
from .forms import ContractForm, TenderForm
from accounts.decorators import staff_required


@login_required
@staff_required
def contract_list(request):
    qs = Contract.objects.select_related('contractor', 'created_by').all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(contract_number__icontains=q) |
            Q(title__icontains=q) |
            Q(contractor__name__icontains=q)
        )

    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    all_contracts = Contract.objects.all()
    stats = {
        'total':     all_contracts.count(),
        'active':    all_contracts.filter(status='active').count(),
        'completed': all_contracts.filter(status='completed').count(),
        'draft':     all_contracts.filter(status='draft').count(),
    }

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'contracts/contract_list.html', {
        'page_obj':   page,
        'page_title': 'Hợp đồng',
        'stats':      stats,
    })


@login_required
@staff_required
def contract_detail(request, pk):
    contract = get_object_or_404(
        Contract.objects.select_related('contractor', 'created_by', 'approved_by'),
        pk=pk
    )
    return render(request, 'contracts/contract_detail.html', {
        'contract':   contract,
        'page_title': contract.title,
    })


@login_required
@staff_required
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            c = form.save(commit=False)
            c.created_by = request.user
            c.save()
            messages.success(request, 'Đã tạo hợp đồng thành công.')
            return redirect('contracts:contract_detail', pk=c.pk)
    else:
        form = ContractForm()

    return render(request, 'contracts/contract_form.html', {
        'form':       form,
        'page_title': 'Tạo hợp đồng mới',
        'is_edit':    False,
    })


@login_required
@staff_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật hợp đồng thành công.')
            return redirect('contracts:contract_detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)

    return render(request, 'contracts/contract_form.html', {
        'form':       form,
        'page_title': f'Chỉnh sửa: {contract.title}',
        'contract':   contract,
        'is_edit':    True,
    })


@login_required
@staff_required
def tender_list(request):
    qs = Tender.objects.select_related('awarded_to', 'created_by', 'result_contract').all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    all_tenders = Tender.objects.all()
    stats = {
        'total':     all_tenders.count(),
        'open':      all_tenders.filter(status='open').count(),
        'awarded':   all_tenders.filter(status='awarded').count(),
        'cancelled': all_tenders.filter(status='cancelled').count(),
    }

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'contracts/tender_list.html', {
        'page_obj':   page,
        'page_title': 'Đấu thầu',
        'stats':      stats,
    })


@login_required
@staff_required
def tender_create(request):
    if request.method == 'POST':
        form = TenderForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.created_by = request.user
            t.save()
            messages.success(request, 'Đã tạo gói thầu thành công.')
            return redirect('contracts:tender_list')
    else:
        form = TenderForm()

    # Danh sách nhà thầu đang hoạt động
    contractor_list = Contractor.objects.filter(is_active=True).order_by('name')
    # Chỉ lấy hợp đồng chưa liên kết gói thầu nào
    available_contracts = Contract.objects.filter(tender__isnull=True).order_by('-created_at')

    return render(request, 'contracts/tender_form.html', {
        'form':               form,
        'page_title':         'Tạo gói thầu mới',
        'contractor_list':    contractor_list,
        'contract_list':      available_contracts,
    })