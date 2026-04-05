from django.urls import path
from . import views

app_name = 'infrastructure'

urlpatterns = [
    path('', views.road_list, name='road_list'),
    path('roads/create/', views.road_create, name='road_create'),
    path('roads/<int:pk>/', views.road_detail, name='road_detail'),
    path('roads/<int:pk>/edit/', views.road_edit, name='road_edit'),
    path('roads/<int:road_pk>/potholes/add/', views.pothole_create, name='pothole_create'),
    path('potholes/<int:pk>/edit/', views.pothole_edit, name='pothole_edit'),
    path('traffic-lights/', views.traffic_light_list, name='traffic_light_list'),
    path('traffic-lights/<int:pk>/', views.traffic_light_detail, name='traffic_light_detail'),
    path('infra/', views.infrastructure_list, name='infra_list'),
    path('infra/<int:pk>/', views.infrastructure_detail, name='infra_detail'),
    path('stats/', views.infrastructure_stats, name='stats'),
]
