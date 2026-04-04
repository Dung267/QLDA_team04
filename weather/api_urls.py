from django.urls import path
from . import views
urlpatterns = [
    path('current/', views.weather_api, name='api_weather'),
]
