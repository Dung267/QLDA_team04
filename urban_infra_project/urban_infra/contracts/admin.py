from django.contrib import admin
from .models import Contract, Tender, Contractor

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['name','tax_code','phone','is_active']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number','title','contractor','status','value','start_date','end_date']
    list_filter = ['status']

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['title','budget','deadline','status']
    list_filter = ['status']
