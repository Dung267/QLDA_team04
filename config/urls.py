# config/urls.py

from django.contrib import admin
from django.urls import path, include

from config.views import home

urlpatterns = [
    path('', home, name='home'),  # Thêm URL mặc định cho trang chủ
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  
    path('infrastructure/', include('infrastructure.urls')), 
    path('incidents/', include('incidents.urls')),  
    path('maintenance/', include('maintenance.urls')),  
    path('reports/', include('reports.urls')),  
    path('weather/', include('weather.urls')),  
    path('alerts/', include('alerts.urls')),  
    path('chatbot/', include('chatbot.urls')),  
    path('audit/', include('audit.urls')),  
    path('inventory/', include('inventory.urls')),  
    path('common/', include('common.urls')),  
]