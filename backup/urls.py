from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # Danh sách backup
    path('', views.list_backups, name='list'),
    
    # Tạo backup
    path('create/', views.create_backup, name='create'),
    
    # Xóa backup
    path('<int:pk>/delete/', views.delete_backup, name='delete'),
    
    # Khôi phục backup
    path('<int:pk>/restore/', views.restore_backup, name='restore'),
    
    # Download backup
    path('<int:pk>/download/', views.download_backup, name='download'),
    
    # Cấu hình backup
    path('config/', views.configure_backup, name='config'),
    
    # Thống kê
    path('stats/', views.backup_stats, name='stats'),
]