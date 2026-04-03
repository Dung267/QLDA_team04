from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('<int:pk>/', views.material_detail, name='material_detail'),
    path('<int:pk>/stock-in/', views.stock_in, name='stock_in'),
    path('<int:pk>/stock-out/', views.stock_out, name='stock_out'),
    path('transactions/', views.transactions_list, name='transactions'),
    path('report/', views.inventory_report, name='report'),
]
