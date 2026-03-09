# inventory/views.py
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Material, StockTransaction

def material_list(request):
    materials = Material.objects.all().order_by("name")
    return render(request, "inventory/material_list.html", {"materials": materials})


def add_stock(request):
    materials = Material.objects.all().order_by("name")

    if request.method == "POST":
        material_id = request.POST.get("material_id")
        quantity = request.POST.get("quantity", "0")
        note = request.POST.get("note", "").strip()

        if not material_id:
            messages.error(request, "Vui lòng chọn vật tư.")
            return render(request, "inventory/add_stock.html", {"materials": materials})

        material = get_object_or_404(Material, id=material_id)
        quantity_decimal = Decimal(quantity)

        material.quantity_in_stock = Decimal(material.quantity_in_stock) + quantity_decimal
        material.save()

        StockTransaction.objects.create(
            material=material,
            transaction_type="IN",
            quantity=quantity_decimal,
            note=note
        )

        messages.success(request, "Nhập kho thành công.")
        return redirect("/inventory/materials/")

    return render(request, "inventory/add_stock.html", {"materials": materials})


def stock_transaction_list(request):
    transactions = StockTransaction.objects.select_related("material").all().order_by("-created_at")
    return render(request, "inventory/transactions.html", {"transactions": transactions})