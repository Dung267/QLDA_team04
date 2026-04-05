from django.urls import path
from . import api_views

urlpatterns = [
    path('roads/', api_views.RoadListAPIView.as_view(), name='api_road_list'),
    path('roads/<int:pk>/', api_views.RoadDetailAPIView.as_view(), name='api_road_detail'),
    path('traffic-lights/', api_views.TrafficLightListAPIView.as_view(), name='api_light_list'),
]
