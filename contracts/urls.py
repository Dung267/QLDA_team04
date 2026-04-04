from django.urls import path
from . import views
app_name = 'contracts'
urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('create/', views.contract_create, name='contract_create'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
    path('tenders/', views.tender_list, name='tender_list'),
    path('tenders/create/', views.tender_create, name='tender_create'),
]
