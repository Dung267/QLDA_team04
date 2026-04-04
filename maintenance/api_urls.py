from django.urls import path
from . import api_views

urlpatterns = [
    path('requests/', api_views.MaintenanceRequestListAPIView.as_view(), name='api_maintenance_list'),
    path('requests/<int:pk>/', api_views.MaintenanceRequestDetailAPIView.as_view(), name='api_maintenance_detail'),
    path('schedules/', api_views.MaintenanceScheduleListAPIView.as_view(), name='api_schedule_list'),
    path('stats/', api_views.maintenance_stats_api, name='api_maintenance_stats'),
]
