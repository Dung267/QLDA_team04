from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Material, StockTransaction, Supplier
from accounts.decorators import staff_required


@login_required
@staff_required
def material_list(request):
    materials = Material.objects.select_related('supplier').all()

    # Tìm kiếm theo tên, mã, nhà cung cấp
    q = request.GET.get('q', '')
    if q:
        materials = materials.filter(
            Q(name__icontains=q) | Q(code__icontains=q) | Q(supplier__name__icontains=q)
        )

    # Lọc tồn kho
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        from django.db.models import F
        materials = materials.filter(current_stock__gt=0, current_stock__lte=F('min_stock'))
    elif stock_filter == 'ok':
        from django.db.models import F
        materials = materials.filter(current_stock__gt=F('min_stock'))
    elif stock_filter == 'zero':
        materials = materials.filter(current_stock__lte=0)

    # Thống kê tổng
    all_materials = Material.objects.all()
    from django.db.models import F as F2
    low_stock_count = all_materials.filter(
        current_stock__gt=0, current_stock__lte=F2('min_stock')
    ).count()

    today = timezone.now().date()
    total_value = sum(
        m.current_stock * float(m.unit_price) for m in all_materials
    ) / 1_000_000

    stats = {
        'total_types': all_materials.count(),
        'low_stock': low_stock_count,
        'total_value': round(total_value, 1),
        'transactions_today': StockTransaction.objects.filter(
            created_at__date=today
        ).count(),
    }

    paginator = Paginator(materials, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/material_list.html', {
        'page_obj': page,
        'page_title': 'Kho vật tư',
        'low_stock_count': low_stock_count,
        'stats': stats,
    })


@login_required
@staff_required
def add_stock(request):
    from .forms import StockTransactionForm

    preselected_material = request.GET.get('material')

    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.performed_by = request.user
            t.save()
            messages.success(request, 'Đã cập nhật kho vật tư.')
            return redirect('inventory:material_list')
    else:
        initial = {'transaction_type': 'in'}
        if preselected_material:
            initial['material'] = preselected_material
        form = StockTransactionForm(initial=initial)

    recent_transactions = StockTransaction.objects.select_related(
        'material', 'performed_by'
    ).all()[:10]

    material_list_qs = Material.objects.all()

    return render(request, 'inventory/add_stock.html', {
        'form': form,
        'page_title': 'Nhập kho',
        'recent_transactions': recent_transactions,
        'material_list': material_list_qs,
        'preselected_material': int(preselected_material) if preselected_material else None,
    })


@login_required
@staff_required
def export_stock(request):
    """Shortcut: mở add_stock ở chế độ xuất kho."""
    material_pk = request.GET.get('material', '')
    url = f"/inventory/add-stock/?material={material_pk}" if material_pk else "/inventory/add-stock/"
    # Truyền default type qua session để view add_stock biết
    request.session['default_tx_type'] = 'out'
    return redirect(url)


@login_required
@staff_required
def transactions(request):
    qs = StockTransaction.objects.select_related('material', 'performed_by').all()

    # Lọc theo vật tư
    material_pk = request.GET.get('material', '')
    if material_pk:
        qs = qs.filter(material__pk=material_pk)

    # Lọc loại giao dịch
    # Template gửi 'in'/'out', khớp luôn với model
    tx_type = request.GET.get('type', '')
    if tx_type in ('in', 'out', 'adjust'):
        qs = qs.filter(transaction_type=tx_type)

    # Lọc ngày (dùng created_at vì model không có transaction_date)
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    # Thống kê
    summary = {
        'import_count': qs.filter(transaction_type='in').count(),
        'export_count': qs.filter(transaction_type='out').count(),
        'total_import_value': (
            qs.filter(transaction_type='in').aggregate(
                s=Sum(models_expr('quantity * unit_price'))
            )['s'] or 0
        ) / 1_000_000,
        'total_export_value': (
            qs.filter(transaction_type='out').aggregate(
                s=Sum(models_expr('quantity * unit_price'))
            )['s'] or 0
        ) / 1_000_000,
    }

    material_list_qs = Material.objects.all()

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/transactions.html', {
        'page_obj': page,
        'page_title': 'Giao dịch kho',
        'summary': summary,
        'material_list': material_list_qs,
    })


def models_expr(expr):
    """Helper: tính tổng quantity * unit_price trong DB."""
    from django.db.models import ExpressionWrapper, F, FloatField
    return ExpressionWrapper(F('quantity') * F('unit_price'), output_field=FloatField())


@login_required
@staff_required
def material_create(request):
    from .forms import MaterialForm
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm vật tư mới.')
            return redirect('inventory:material_list')
    else:
        form = MaterialForm()
    return render(request, 'inventory/material_form.html', {
        'form': form,
        'page_title': 'Thêm vật tư',
    })


@login_required
@staff_required
def material_edit(request, pk):
    from .forms import MaterialForm
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật vật tư.')
            return redirect('inventory:material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'inventory/material_form.html', {
        'form': form,
        'page_title': 'Chỉnh sửa vật tư',
        'material': material,
    })