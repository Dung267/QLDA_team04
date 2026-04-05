from django.urls import path
from . import api_views

urlpatterns = [
    path('alerts/', api_views.FloodAlertListAPIView.as_view(), name='api_flood_alerts'),
    path('alerts/active/', api_views.ActiveFloodAlertsAPIView.as_view(), name='api_flood_active'),
    path('disasters/', api_views.DisasterUpdateListAPIView.as_view(), name='api_disaster_updates'),
]
