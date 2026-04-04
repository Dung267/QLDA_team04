from django.contrib import admin
from .models import Material, StockTransaction, Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name','contact','phone','email']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name','code','unit','current_stock','min_stock','unit_price','supplier']
    list_filter = ['unit']
    search_fields = ['name','code']

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['material','transaction_type','quantity','performed_by','created_at']
    list_filter = ['transaction_type']
