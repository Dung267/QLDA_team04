from django.contrib import admin
from .models import Material, MaterialCategory, Supplier, StockTransaction


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'unit', 'quantity_in_stock', 'minimum_stock', 'unit_price']
    list_filter = ['category', 'unit']
    search_fields = ['name', 'code']


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_name', 'phone', 'email', 'is_active']
    list_filter = ['is_active']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['material', 'transaction_type', 'quantity', 'unit_price', 'performed_by', 'created_at']
    list_filter = ['transaction_type']
    readonly_fields = ['created_at']
