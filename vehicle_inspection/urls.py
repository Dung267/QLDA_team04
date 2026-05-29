from django.urls import path
from . import views

app_name = 'vehicle_inspection'

urlpatterns = [
    # --- Quản lý phương tiện (Vehicles) ---
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/add/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle_update'),

    # --- Quản lý lịch đăng kiểm (Inspections) ---
    path('', views.InspectionListView.as_view(), name='inspection_list'),
    path('schedule/', views.ScheduleInspectionView.as_view(), name='schedule'), # Đã sửa tên View
    path('<int:pk>/', views.InspectionDetailView.as_view(), name='inspection_detail'), # Bổ sung trang chi tiết
    path('<int:pk>/certificate/', views.inspection_certificate_pdf, name='certificate_pdf'),
    
    # --- Các thao tác (Actions) ---
    path('<int:pk>/cancel/', views.cancel_inspection, name='cancel'),
    path('<int:pk>/update/', views.InspectionResultView.as_view(), name='update'), # Đã sửa thành Class-Based View
    path('<int:pk>/pay/', views.pay_inspection_fee, name='pay'), # Đã sửa tên hàm
]
