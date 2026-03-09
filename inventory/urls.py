# inventory/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('materials/', views.material_list, name='material_list'),  # Danh sách vật tư
    path('add-stock/', views.add_stock, name='add_stock'),  # Thêm vật tư vào kho
    path('transactions/', views.stock_transaction_list, name='stock_transaction_list'),  # Danh sách giao dịch kho
]