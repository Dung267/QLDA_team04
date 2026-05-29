from django.urls import path
from . import views

app_name = 'integration'

urlpatterns = [
    # Danh sách integrations
    path('', views.list_integrations, name='list'),
    
    # Tạo integration mới
    path('create/', views.create_integration, name='create'),
    
    # Cập nhật integration
    path('<int:pk>/update/', views.update_integration, name='update'),
    
    # Xóa integration
    path('<int:pk>/delete/', views.delete_integration, name='delete'),
    
    # Test kết nối API
    path('<int:pk>/test/', views.test_connection, name='test'),
    
    # Webhook logs
    path('<int:pk>/logs/', views.webhook_logs, name='logs'),
    
    # Trigger manual sync
    path('<int:pk>/sync/', views.trigger_sync, name='sync'),
    
    # Thống kê
    path('stats/', views.integration_stats, name='stats'),
]