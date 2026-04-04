from django.urls import path
from . import views
app_name = 'inventory'
urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('transactions/', views.transactions, name='transactions'),
]
