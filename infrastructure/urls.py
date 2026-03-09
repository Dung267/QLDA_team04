# infrastructure/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('roads/', views.road_list, name='road_list'),  # Danh sách các tuyến đường
    path('roads/<int:id>/', views.road_detail, name='road_detail'),  # Chi tiết tuyến đường
    path('potholes/', views.pothole_list, name='pothole_list'),  # Danh sách ổ gà
    path('traffic-lights/', views.traffic_light_status, name='traffic_light_status'),  # Trạng thái đèn giao thông
]