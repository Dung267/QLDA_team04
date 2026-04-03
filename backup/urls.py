from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_list, name='list'),
    path('create/', views.backup_create, name='create'),
    path('<int:pk>/delete/', views.backup_delete, name='delete'),
    path('<int:pk>/restore/', views.restore_backup, name='restore'),
    path('schedules/', views.schedule_list, name='schedules'),
]