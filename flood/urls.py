from django.urls import path
from . import views

app_name = 'flood'

urlpatterns = [
    path('', views.flood_alert_list, name='alert_list'),
    path('create/', views.flood_alert_create, name='alert_create'),
    path('<int:pk>/', views.flood_alert_detail, name='alert_detail'),
    path('<int:pk>/update/', views.flood_alert_update, name='alert_update'),
    path('<int:pk>/resolve/', views.resolve_alert, name='resolve'),
    path('disasters/', views.disaster_alert_list, name='disaster_list'),
    path('disasters/create/', views.disaster_alert_create, name='disaster_create'),
    path('api/map/', views.flood_map_api, name='map_api'),
]
