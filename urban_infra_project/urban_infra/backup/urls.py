from django.urls import path
from . import views
app_name = 'backup'
urlpatterns = [
    path('', views.backup_list, name='list'),
    path('create/', views.create_backup, name='create'),
    path('<int:pk>/restore/', views.restore_backup, name='restore'),
    path('<int:pk>/delete/', views.delete_backup, name='delete'),
    path('config/', views.save_config, name='config'),
]
