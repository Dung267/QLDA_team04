from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('monthly/', views.monthly_report, name='monthly'),
    path('quarterly/', views.quarterly_report, name='quarterly'),
    path('yearly/', views.yearly_report, name='yearly'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
