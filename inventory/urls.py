
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('export-stock/', views.export_stock, name='export_stock'),
    path('transactions/', views.transactions, name='transactions'),
    path('material/create/', views.material_create, name='material_create'),
    path('material/<int:pk>/edit/', views.material_edit, name='material_edit'),
]