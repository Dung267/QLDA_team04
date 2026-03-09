# maintenance/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_maintenance_request, name='create_maintenance_request'),  # Tạo yêu cầu bảo trì
    path('assign/', views.assign_maintenance_task, name='assign_maintenance_task'),  # Phân công công việc bảo trì
    path('progress/', views.update_progress, name='update_progress'),  # Cập nhật tiến độ bảo trì
]