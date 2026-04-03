from django.urls import path
from .views import weather_api

urlpatterns = [
    path('current/', weather_api, name='weather_api'),
]