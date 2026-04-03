from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from .models import Material, StockTransaction, Supplier, MaterialCategory, MaintenanceMaterialUsage
from .forms import MaterialForm, StockTransactionForm
from accounts.decorators import staff_required


@login_required
@staff_required
def material_list(request):
    materials = Material.objects.select_related('category', 'supplier').all()
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')
    if q:
        materials = materials.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if category:
        materials = materials.filter(category_id=category)
    if low_stock:
        materials = materials.filter(quantity_in_stock__lte=F('minimum_stock'))
    paginator = Paginator(materials, 25)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'inventory/material_list.html', {
        'page_obj': page,
        'categories': MaterialCategory.objects.all(),
        'page_title': 'Kho vật tư',
    })


@login_required
@staff_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    transactions = material.transactions.all()[:20]
    return render(request, 'inventory/material_detail.html', {
        'material': material, 'transactions': transactions,
        'page_title': material.name,
    })


@login_required
@staff_required
def stock_in(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.material = material
            tx.transaction_type = 'import'
            tx.performed_by = request.user
            tx.save()
            messages.success(request, f'Đã nhập {tx.quantity} {material.get_unit_display()}.')
            return redirect('inventory:material_detail', pk=pk)
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/stock_form.html', {'form': form, 'material': material, 'action': 'Nhập kho'})


@login_required
@staff_required
def stock_out(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            if tx.quantity > material.quantity_in_stock:
                messages.error(request, 'Số lượng xuất vượt quá tồn kho.')
            else:
                tx.material = material
                tx.transaction_type = 'export'
                tx.performed_by = request.user
                tx.save()
                messages.success(request, f'Đã xuất {tx.quantity} {material.get_unit_display()}.')
                return redirect('inventory:material_detail', pk=pk)
    else:
        form = StockTransactionForm()
    return render(request, 'inventory/stock_form.html', {'form': form, 'material': material, 'action': 'Xuất kho'})


@login_required
@staff_required
def inventory_report(request):
    from django.db.models import Count, Sum as DSum
    stats = {
        'total_materials': Material.objects.count(),
        'low_stock_count': Material.objects.filter(quantity_in_stock__lte=F('minimum_stock')).count(),
        'total_value': sum(m.total_value for m in Material.objects.all()),
        'by_category': list(Material.objects.values('category__name').annotate(count=Count('id'))),
    }
    return render(request, 'inventory/report.html', {'stats': stats, 'page_title': 'Báo cáo vật tư'})


@login_required
@staff_required
def transactions_list(request):
    transactions = StockTransaction.objects.select_related('material', 'performed_by').order_by('-created_at')
    paginator = Paginator(transactions, 30)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'inventory/transactions.html', {'page_obj': page, 'page_title': 'Giao dịch kho'})
