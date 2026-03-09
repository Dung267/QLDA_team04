# audit/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.view_logs, name='view_logs'),  # Xem các log
    path('changes/', views.view_changes, name='view_changes'),  # Xem các thay đổi
]