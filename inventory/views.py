from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Material, StockTransaction, Supplier
from accounts.decorators import staff_required

@login_required
@staff_required
def material_list(request):
    materials = Material.objects.select_related('supplier').all()
    q = request.GET.get('q','')
    if q:
        materials = materials.filter(Q(name__icontains=q)|Q(code__icontains=q))
    paginator = Paginator(materials, 20)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'inventory/material_list.html',{'page_obj':page,'page_title':'Kho vật tư'})

@login_required
@staff_required
def add_stock(request):
    from .forms import StockTransactionForm
    if request.method=='POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.performed_by = request.user
            t.save()
            messages.success(request, 'Đã cập nhật kho vật tư.')
            return redirect('inventory:material_list')
    else:
        form = StockTransactionForm()
    return render(request,'inventory/add_stock.html',{'form':form,'page_title':'Nhập/Xuất kho'})

@login_required
@staff_required
def transactions(request):
    qs = StockTransaction.objects.select_related('material','performed_by').all()
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request,'inventory/transactions.html',{'page_obj':page,'page_title':'Giao dịch kho'})
