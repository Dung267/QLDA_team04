from django.urls import path
from . import api_views

urlpatterns = [
    path('vehicles/', api_views.VehicleListAPIView.as_view(), name='api_vehicle_list'),
    path('vehicles/<int:pk>/', api_views.VehicleDetailAPIView.as_view(), name='api_vehicle_detail'),
    path('inspections/', api_views.InspectionListAPIView.as_view(), name='api_inspection_list'),
    path('inspections/<int:pk>/', api_views.InspectionDetailAPIView.as_view(), name='api_inspection_detail'),
    path('centers/', api_views.InspectionCenterListAPIView.as_view(), name='api_center_list'),
    path('stats/', api_views.inspection_stats_api, name='api_inspection_stats'),
]
