# weather/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.get_current_weather, name='get_current_weather'),  # Lấy thông tin thời tiết hiện tại
    path('forecast/', views.get_weather_forecast, name='get_weather_forecast'),  # Dự báo thời tiết
]