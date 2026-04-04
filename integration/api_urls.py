from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.IntegrationListAPIView.as_view(), name='api_integration_list'),
    path('<int:pk>/', api_views.IntegrationDetailAPIView.as_view(), name='api_integration_detail'),
    path('<int:pk>/test/', api_views.test_integration_api, name='api_integration_test'),
    path('webhooks/', api_views.WebhookLogListAPIView.as_view(), name='api_webhook_logs'),
    path('webhook/receive/', api_views.webhook_receive_api, name='api_webhook_receive'),
]
