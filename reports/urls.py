# reports/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary_report, name='summary_report'),  # Báo cáo tóm tắt
    path('monthly/', views.monthly_report, name='monthly_report'),  # Báo cáo tháng
    path('quarterly/', views.quarterly_report, name='quarterly_report'),  # Báo cáo quý
    path('yearly/', views.yearly_report, name='yearly_report'),  # Báo cáo năm
]