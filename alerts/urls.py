# alerts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('flood-warning/', views.flood_warning, name='flood_warning'),  # Cảnh báo ngập lụt
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),  # Cảnh báo sự cố khẩn cấp
]