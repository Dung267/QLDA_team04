from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.PermitListAPIView.as_view(), name='api_permit_list'),
    path('<int:pk>/', api_views.PermitDetailAPIView.as_view(), name='api_permit_detail'),
    path('<int:pk>/submit/', api_views.submit_permit_api, name='api_permit_submit'),
    path('stats/', api_views.permit_stats_api, name='api_permit_stats'),
]
