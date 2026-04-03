from django.contrib import admin
from .models import Contract, Tender, Contractor


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'title', 'contractor', 'value', 'status', 'start_date', 'end_date']
    list_filter = ['status']
    search_fields = ['contract_number', 'title']


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['title', 'budget', 'deadline', 'status']
    list_filter = ['status']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_code', 'phone', 'is_active']
