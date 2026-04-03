from django.urls import path
from .views import flood_map_api

urlpatterns = [
    path('map/', flood_map_api, name='flood_map_api'),
]
