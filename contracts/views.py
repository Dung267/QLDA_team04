from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Contract, Tender, Contractor
from accounts.decorators import staff_required

@login_required
@staff_required
def contract_list(request):
    contracts = Contract.objects.select_related('contractor','created_by').all()
    paginator = Paginator(contracts, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'contracts/contract_list.html',{'page_obj':page,'page_title':'Hợp đồng'})

@login_required
@staff_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request,'contracts/contract_detail.html',{'contract':contract,'page_title':contract.title})

@login_required
@staff_required
def contract_create(request):
    from .forms import ContractForm
    if request.method=='POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            c = form.save(commit=False)
            c.created_by = request.user
            c.save()
            messages.success(request,'Đã tạo hợp đồng.')
            return redirect('contracts:contract_detail', pk=c.pk)
    else:
        form = ContractForm()
    return render(request,'contracts/contract_form.html',{'form':form,'page_title':'Tạo hợp đồng'})

@login_required
@staff_required
def tender_list(request):
    tenders = Tender.objects.all()
    paginator = Paginator(tenders, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'contracts/tender_list.html',{'page_obj':page,'page_title':'Đấu thầu'})

@login_required
@staff_required
def tender_create(request):
    from .forms import TenderForm
    if request.method=='POST':
        form = TenderForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.created_by = request.user
            t.save()
            messages.success(request,'Đã tạo gói thầu.')
            return redirect('contracts:tender_list')
    else:
        form = TenderForm()
    return render(request,'contracts/tender_form.html',{'form':form,'page_title':'Tạo gói thầu'})
