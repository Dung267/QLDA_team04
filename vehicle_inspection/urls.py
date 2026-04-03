from django.urls import path
from . import views

app_name = 'vehicle_inspection'

urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:vehicle_pk>/book/', views.book_inspection, name='book'),
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('inspections/<int:pk>/process/', views.inspection_process, name='process'),
    path('stats/', views.inspection_stats, name='stats'),
]
