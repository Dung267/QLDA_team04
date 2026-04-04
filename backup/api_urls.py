from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.BackupListAPIView.as_view(), name='api_backup_list'),
    path('<int:pk>/', api_views.BackupDetailAPIView.as_view(), name='api_backup_detail'),
    path('trigger/', api_views.trigger_backup_api, name='api_backup_trigger'),
    path('<int:pk>/restore/', api_views.restore_backup_api, name='api_backup_restore'),
    path('config/', api_views.backup_config_api, name='api_backup_config'),
]
