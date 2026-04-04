from django.urls import path
from . import views
app_name = 'integration'
urlpatterns = [
    path('', views.integration_list, name='list'),
    path('<int:pk>/test/', views.test_integration, name='test'),
]
