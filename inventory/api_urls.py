from django.urls import path
from . import api_views

urlpatterns = [
    path('materials/', api_views.MaterialListAPIView.as_view(), name='api_material_list'),
    path('materials/<int:pk>/', api_views.MaterialDetailAPIView.as_view(), name='api_material_detail'),
    path('transactions/', api_views.StockTransactionListAPIView.as_view(), name='api_transaction_list'),
    path('low-stock/', api_views.low_stock_api, name='api_low_stock'),
    path('stats/', api_views.inventory_stats_api, name='api_inventory_stats'),
]
