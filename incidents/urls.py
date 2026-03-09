# incidents/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.report_incident, name='report_incident'),  # Báo cáo sự cố
    path('list/', views.incident_list, name='incident_list'),  # Danh sách sự cố
    path('<int:id>/', views.incident_detail, name='incident_detail'),  # Chi tiết sự cố
]