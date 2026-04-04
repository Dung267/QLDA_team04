from django.urls import path
from . import views
urlpatterns = [
    path('alerts/', views.active_alerts_api, name='api_flood_alerts'),
]
