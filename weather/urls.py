from django.urls import path
from . import views
app_name = 'weather'
urlpatterns = [
    path('', views.current_weather, name='current'),
    path('forecast/', views.forecast_weather, name='forecast'),
    path('sync/', views.sync_weather_api, name='sync'),
    path('api/', views.weather_api, name='api'),
]
