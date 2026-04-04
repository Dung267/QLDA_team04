from django.urls import path
from . import api_views

urlpatterns = [
    path('layers/', api_views.map_layers_api, name='api_map_layers'),
]
