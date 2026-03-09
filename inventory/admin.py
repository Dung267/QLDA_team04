from django.contrib import admin
from .models import Material, StockTransaction

admin.site.register(Material)
admin.site.register(StockTransaction)