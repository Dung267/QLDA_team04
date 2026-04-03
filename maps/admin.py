from django.contrib import admin
from .models import MapLayer

@admin.register(MapLayer)
class MapLayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'layer_type', 'is_visible']
