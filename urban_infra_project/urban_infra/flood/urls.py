from django.urls import path
from . import views
app_name = 'flood'
urlpatterns = [
    path('', views.alert_list, name='alert_list'),
    path('create/', views.alert_create, name='alert_create'),
    path('<int:pk>/', views.alert_detail, name='alert_detail'),
    path('<int:pk>/resolve/', views.alert_resolve, name='alert_resolve'),
    path('api/active/', views.active_alerts_api, name='active_api'),
]
