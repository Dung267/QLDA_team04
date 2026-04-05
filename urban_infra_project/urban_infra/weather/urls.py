from django.urls import path
from . import views
app_name = 'weather'
urlpatterns = [
    path('', views.current_weather, name='current'),
    path('api/', views.weather_api, name='api'),
]
