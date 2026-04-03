from django.urls import path
from . import views

app_name = 'integration'

urlpatterns = [
    path('', views.integration_list, name='list'),
    path('<int:pk>/test/', views.integration_test, name='test'),
    path('<int:pk>/logs/', views.api_logs, name='logs'),
]
